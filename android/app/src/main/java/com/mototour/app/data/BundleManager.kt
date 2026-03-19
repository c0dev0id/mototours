package com.mototour.app.data

import android.content.Context
import android.net.Uri
import org.json.JSONObject
import java.io.*
import java.util.zip.ZipEntry
import java.util.zip.ZipInputStream
import java.util.zip.ZipOutputStream

/**
 * Handles import and export of tour bundles.
 *
 * Bundle format (ZIP):
 *   tour.json   — metadata
 *   tour.pdf    — companion PDF
 *   day1.gpx    — GPX per day (or single .gpx for day tours)
 *
 * Also supports "loose file" import: user picks a PDF + one or more GPX files.
 */
class BundleManager(private val context: Context) {

    private val dao = AppDatabase.get(context).tourDao()
    private val toursDir get() = File(context.filesDir, "tours").apply { mkdirs() }

    // ── Import from ZIP ─────────────────────────────────────────────

    suspend fun importZip(uri: Uri): Long? {
        val tempDir = File(context.cacheDir, "import_${System.currentTimeMillis()}")
        tempDir.mkdirs()
        try {
            // Extract ZIP
            context.contentResolver.openInputStream(uri)?.use { stream ->
                ZipInputStream(stream).use { zip ->
                    var entry: ZipEntry?
                    while (zip.nextEntry.also { entry = it } != null) {
                        val file = File(tempDir, entry!!.name)
                        if (entry!!.isDirectory) { file.mkdirs(); continue }
                        file.parentFile?.mkdirs()
                        file.outputStream().use { out -> zip.copyTo(out) }
                    }
                }
            } ?: return null

            return importFromDir(tempDir)
        } finally {
            tempDir.deleteRecursively()
        }
    }

    /** Import from an extracted directory containing tour.json + PDF + GPX. */
    private suspend fun importFromDir(dir: File): Long? {
        val manifestFile = dir.resolve("tour.json")
        val gpxFiles = dir.listFiles { f -> f.extension == "gpx" }
            ?.sortedBy { it.name } ?: emptyList()
        val pdfFile = dir.listFiles { f -> f.extension == "pdf" }?.firstOrNull()

        if (gpxFiles.isEmpty()) return null

        // Parse manifest if available, otherwise derive from GPX
        val manifest = if (manifestFile.exists()) {
            JSONObject(manifestFile.readText())
        } else null

        val category = manifest?.optString("category")?.let {
            runCatching { TourCategory.valueOf(it) }.getOrNull()
        } ?: categoryFromDayCount(gpxFiles.size)

        val slug = manifest?.optString("slug")
            ?: gpxFiles.first().nameWithoutExtension.replace(Regex("[^a-z0-9]"), "_")

        // Skip if already imported
        if (dao.tourExists(slug, category)) return null

        // Parse first GPX for tour name fallback
        val firstGpx = gpxFiles.first().inputStream().use { GpxParser.parse(it) }

        val name = manifest?.optString("name")?.takeIf { it.isNotEmpty() }
            ?: firstGpx.name.replace(Regex("^.*?:\\s*"), "") // strip "Tour 01, Day 1: " prefix

        // Create tour directory
        val tourDir = File(toursDir, slug).apply { mkdirs() }

        // Copy PDF
        val pdfPath = if (pdfFile != null) {
            val dest = File(tourDir, "tour.pdf")
            pdfFile.copyTo(dest, overwrite = true)
            dest.absolutePath
        } else ""

        // Insert tour
        val tourId = dao.insertTour(
            TourEntity(
                name = name,
                slug = slug,
                category = category,
                region = manifest?.optString("region") ?: "",
                totalDistanceKm = manifest?.optInt("total_distance_km") ?: 0,
                dayCount = gpxFiles.size,
                overview = manifest?.optString("overview") ?: firstGpx.description,
                highlights = manifest?.optString("highlights") ?: "",
                roadCharacter = manifest?.optString("road_character") ?: "",
                pdfPath = pdfPath
            )
        )

        // Process each GPX → day + waypoints
        var totalDist = 0
        for ((index, gpxFile) in gpxFiles.withIndex()) {
            val gpx = gpxFile.inputStream().use { GpxParser.parse(it) }
            val distKm = manifest?.optJSONArray("days")
                ?.optJSONObject(index)?.optInt("distance_km")
                ?: GpxParser.estimateDistanceKm(gpx.routePoints)
            totalDist += distKm

            val destGpx = File(tourDir, "day${index + 1}.gpx")
            gpxFile.copyTo(destGpx, overwrite = true)

            val dayName = manifest?.optJSONArray("days")
                ?.optJSONObject(index)?.optString("name")
                ?: gpx.name

            val dayId = dao.insertDay(
                DayEntity(
                    tourId = tourId,
                    dayNumber = index + 1,
                    name = dayName,
                    distanceKm = distKm,
                    description = gpx.description,
                    gpxPath = destGpx.absolutePath
                )
            )

            // Insert waypoints
            val waypoints = gpx.waypoints.mapIndexed { i, wpt ->
                val type = when {
                    i == 0 -> WaypointType.START
                    i == gpx.waypoints.lastIndex &&
                        wpt.type == "Start/End" -> WaypointType.END
                    else -> GpxParser.classifyWaypoint(wpt)
                }
                WaypointEntity(
                    dayId = dayId,
                    orderIndex = i,
                    name = wpt.name,
                    lat = wpt.lat,
                    lon = wpt.lon,
                    description = wpt.description,
                    type = type
                )
            }
            dao.insertWaypoints(waypoints)
        }

        // Update total distance if it was derived
        if (manifest?.optInt("total_distance_km") == null || manifest.optInt("total_distance_km") == 0) {
            // Re-insert with correct distance — Room doesn't have a simple update-single-field,
            // so we delete and re-insert. Fine for import.
            val tour = dao.tourWithDays(tourId)?.tour ?: return tourId
            dao.deleteTour(tour)
            val newId = dao.insertTour(tour.copy(id = 0, totalDistanceKm = totalDist))
            // Re-import days (they were cascade-deleted)
            for ((index, gpxFile) in gpxFiles.withIndex()) {
                val gpx = gpxFile.inputStream().use { GpxParser.parse(it) }
                val destGpx = File(tourDir, "day${index + 1}.gpx")
                val distKm = GpxParser.estimateDistanceKm(gpx.routePoints)
                val dayId = dao.insertDay(
                    DayEntity(
                        tourId = newId,
                        dayNumber = index + 1,
                        name = gpx.name,
                        distanceKm = distKm,
                        description = gpx.description,
                        gpxPath = destGpx.absolutePath
                    )
                )
                val waypoints = gpx.waypoints.mapIndexed { i, wpt ->
                    val type = when {
                        i == 0 -> WaypointType.START
                        i == gpx.waypoints.lastIndex && wpt.type == "Start/End" -> WaypointType.END
                        else -> GpxParser.classifyWaypoint(wpt)
                    }
                    WaypointEntity(dayId = dayId, orderIndex = i,
                        name = wpt.name, lat = wpt.lat, lon = wpt.lon,
                        description = wpt.description, type = type)
                }
                dao.insertWaypoints(waypoints)
            }
            return newId
        }

        return tourId
    }

    // ── Import loose files (PDF + GPX selection) ────────────────────

    suspend fun importLooseFiles(pdfUri: Uri?, gpxUris: List<Uri>): Long? {
        if (gpxUris.isEmpty()) return null

        val tempDir = File(context.cacheDir, "loose_${System.currentTimeMillis()}")
        tempDir.mkdirs()
        try {
            // Copy GPX files
            val gpxFiles = gpxUris.mapIndexed { index, uri ->
                val dest = File(tempDir, "day${index + 1}.gpx")
                context.contentResolver.openInputStream(uri)?.use { input ->
                    dest.outputStream().use { out -> input.copyTo(out) }
                }
                dest
            }.filter { it.exists() }

            // Copy PDF if provided
            if (pdfUri != null) {
                val dest = File(tempDir, "tour.pdf")
                context.contentResolver.openInputStream(pdfUri)?.use { input ->
                    dest.outputStream().use { out -> input.copyTo(out) }
                }
            }

            return importFromDir(tempDir)
        } finally {
            tempDir.deleteRecursively()
        }
    }

    // ── Export ───────────────────────────────────────────────────────

    suspend fun exportTour(tourId: Long, outputUri: Uri): Boolean {
        val tourWithDays = dao.tourWithDays(tourId) ?: return false
        val tour = tourWithDays.tour
        val days = tourWithDays.days.sortedBy { it.dayNumber }

        context.contentResolver.openOutputStream(outputUri)?.use { outStream ->
            ZipOutputStream(outStream).use { zip ->
                // tour.json manifest
                val manifest = JSONObject().apply {
                    put("name", tour.name)
                    put("slug", tour.slug)
                    put("category", tour.category.name)
                    put("region", tour.region)
                    put("total_distance_km", tour.totalDistanceKm)
                    put("day_count", tour.dayCount)
                    put("overview", tour.overview)
                    put("highlights", tour.highlights)
                    put("road_character", tour.roadCharacter)
                    val daysArr = org.json.JSONArray()
                    for (day in days) {
                        daysArr.put(JSONObject().apply {
                            put("name", day.name)
                            put("distance_km", day.distanceKm)
                            put("description", day.description)
                        })
                    }
                    put("days", daysArr)
                }
                zip.putNextEntry(ZipEntry("tour.json"))
                zip.write(manifest.toString(2).toByteArray())
                zip.closeEntry()

                // PDF
                val pdfFile = File(tour.pdfPath)
                if (pdfFile.exists()) {
                    zip.putNextEntry(ZipEntry("tour.pdf"))
                    pdfFile.inputStream().use { it.copyTo(zip) }
                    zip.closeEntry()
                }

                // GPX files
                for (day in days) {
                    val gpxFile = File(day.gpxPath)
                    if (gpxFile.exists()) {
                        zip.putNextEntry(ZipEntry("day${day.dayNumber}.gpx"))
                        gpxFile.inputStream().use { it.copyTo(zip) }
                        zip.closeEntry()
                    }
                }
            }
        } ?: return false

        return true
    }

    // ── First-launch asset seeding ──────────────────────────────────

    suspend fun seedFromAssets() {
        if (dao.tourCount() > 0) return

        val assetManager = context.assets
        val bundles = try {
            assetManager.list("tours") ?: emptyArray()
        } catch (_: IOException) {
            emptyArray()
        }

        for (bundle in bundles.filter { it.endsWith(".zip") }) {
            val tempFile = File(context.cacheDir, bundle)
            try {
                assetManager.open("tours/$bundle").use { input ->
                    tempFile.outputStream().use { out -> input.copyTo(out) }
                }
                importZip(Uri.fromFile(tempFile))
            } finally {
                tempFile.delete()
            }
        }
    }

    // ── Helpers ──────────────────────────────────────────────────────

    private fun categoryFromDayCount(days: Int) = when (days) {
        1 -> TourCategory.DAY
        2 -> TourCategory.WEEKEND
        3 -> TourCategory.THREE_DAY
        else -> TourCategory.SIX_DAY
    }
}
