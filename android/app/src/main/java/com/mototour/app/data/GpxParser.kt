package com.mototour.app.data

import org.xmlpull.v1.XmlPullParser
import org.xmlpull.v1.XmlPullParserFactory
import java.io.InputStream

/** Parsed GPX data. */
data class GpxData(
    val name: String,
    val description: String,
    val waypoints: List<GpxWaypoint>,
    val routePoints: List<GpxPoint>
)

data class GpxWaypoint(
    val name: String,
    val lat: Double,
    val lon: Double,
    val description: String,
    val symbol: String,
    val type: String
)

data class GpxPoint(val lat: Double, val lon: Double)

object GpxParser {

    fun parse(input: InputStream): GpxData {
        val parser = XmlPullParserFactory.newInstance().newPullParser()
        parser.setInput(input, "UTF-8")

        var name = ""
        var description = ""
        val waypoints = mutableListOf<GpxWaypoint>()
        val routePoints = mutableListOf<GpxPoint>()

        // Current element state
        var inMetadata = false
        var inWpt = false
        var inRtePt = false
        var wptLat = 0.0
        var wptLon = 0.0
        var wptName = ""
        var wptDesc = ""
        var wptSym = ""
        var wptType = ""
        var currentTag = ""

        while (true) {
            when (parser.next()) {
                XmlPullParser.START_TAG -> {
                    currentTag = parser.name
                    when (currentTag) {
                        "metadata" -> inMetadata = true
                        "wpt" -> {
                            inWpt = true
                            wptLat = parser.getAttributeValue(null, "lat")?.toDoubleOrNull() ?: 0.0
                            wptLon = parser.getAttributeValue(null, "lon")?.toDoubleOrNull() ?: 0.0
                            wptName = ""; wptDesc = ""; wptSym = ""; wptType = ""
                        }
                        "rtept" -> {
                            inRtePt = true
                            val lat = parser.getAttributeValue(null, "lat")?.toDoubleOrNull() ?: 0.0
                            val lon = parser.getAttributeValue(null, "lon")?.toDoubleOrNull() ?: 0.0
                            routePoints.add(GpxPoint(lat, lon))
                        }
                    }
                }
                XmlPullParser.TEXT -> {
                    val text = parser.text?.trim() ?: ""
                    if (text.isEmpty()) continue
                    when {
                        inMetadata && currentTag == "name" -> name = text
                        inMetadata && currentTag == "desc" -> description = text
                        inWpt && currentTag == "name" -> wptName = text
                        inWpt && currentTag == "desc" -> wptDesc = text
                        inWpt && currentTag == "sym" -> wptSym = text
                        inWpt && currentTag == "type" -> wptType = text
                    }
                }
                XmlPullParser.END_TAG -> {
                    when (parser.name) {
                        "metadata" -> inMetadata = false
                        "wpt" -> {
                            waypoints.add(GpxWaypoint(wptName, wptLat, wptLon, wptDesc, wptSym, wptType))
                            inWpt = false
                        }
                        "rtept" -> inRtePt = false
                    }
                    currentTag = ""
                }
                XmlPullParser.END_DOCUMENT -> break
            }
        }
        return GpxData(name, description, waypoints, routePoints)
    }

    /** Map GPX symbol/type to our WaypointType. */
    fun classifyWaypoint(wpt: GpxWaypoint): WaypointType = when {
        wpt.type == "Start/End" && wpt.symbol == "Flag, Blue" -> {
            // First occurrence = START, second = END — caller decides by index
            WaypointType.START
        }
        wpt.symbol == "Restaurant" -> WaypointType.MIDPOINT
        wpt.symbol == "Hotel" -> WaypointType.OVERNIGHT
        else -> WaypointType.VIA
    }

    /** Approximate distance in km from route points using Haversine. */
    fun estimateDistanceKm(points: List<GpxPoint>): Int {
        if (points.size < 2) return 0
        var total = 0.0
        for (i in 1 until points.size) {
            total += haversineKm(
                points[i - 1].lat, points[i - 1].lon,
                points[i].lat, points[i].lon
            )
        }
        return total.toInt()
    }

    private fun haversineKm(lat1: Double, lon1: Double, lat2: Double, lon2: Double): Double {
        val R = 6371.0
        val dLat = Math.toRadians(lat2 - lat1)
        val dLon = Math.toRadians(lon2 - lon1)
        val a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
                Math.cos(Math.toRadians(lat1)) * Math.cos(Math.toRadians(lat2)) *
                Math.sin(dLon / 2) * Math.sin(dLon / 2)
        return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
    }
}
