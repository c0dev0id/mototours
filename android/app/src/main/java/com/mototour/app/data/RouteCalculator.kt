package com.mototour.app.data

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

object RouteCalculator {

    private const val OSRM_BASE = "https://router.project-osrm.org/route/v1/driving"

    /**
     * Calculate a road-following route between the given waypoints using OSRM.
     * Returns the route as a list of [GpxPoint], or null if the request fails.
     */
    suspend fun calculateRoute(waypoints: List<GpxPoint>): List<GpxPoint>? {
        if (waypoints.size < 2) return null

        return withContext(Dispatchers.IO) {
            try {
                val coords = waypoints.joinToString(";") { "${it.lon},${it.lat}" }
                val url = URL("$OSRM_BASE/$coords?overview=full&geometries=polyline")
                val conn = url.openConnection() as HttpURLConnection
                conn.connectTimeout = 10_000
                conn.readTimeout = 10_000
                conn.setRequestProperty("User-Agent", "MotoTourApp/1.0")

                try {
                    if (conn.responseCode != 200) return@withContext null
                    val body = conn.inputStream.bufferedReader().readText()
                    val json = JSONObject(body)
                    if (json.optString("code") != "Ok") return@withContext null

                    val geometry = json.getJSONArray("routes")
                        .getJSONObject(0)
                        .getString("geometry")

                    decodePolyline(geometry)
                } finally {
                    conn.disconnect()
                }
            } catch (_: Exception) {
                null
            }
        }
    }

    /**
     * Decode a Google encoded polyline string into a list of [GpxPoint].
     * See: https://developers.google.com/maps/documentation/utilities/polylinealgorithm
     */
    private fun decodePolyline(encoded: String): List<GpxPoint> {
        val points = mutableListOf<GpxPoint>()
        var index = 0
        var lat = 0
        var lng = 0

        while (index < encoded.length) {
            // Decode latitude
            var shift = 0
            var result = 0
            var b: Int
            do {
                b = encoded[index++].code - 63
                result = result or ((b and 0x1F) shl shift)
                shift += 5
            } while (b >= 0x20)
            lat += if (result and 1 != 0) (result shr 1).inv() else result shr 1

            // Decode longitude
            shift = 0
            result = 0
            do {
                b = encoded[index++].code - 63
                result = result or ((b and 0x1F) shl shift)
                shift += 5
            } while (b >= 0x20)
            lng += if (result and 1 != 0) (result shr 1).inv() else result shr 1

            points.add(GpxPoint(lat / 1e5, lng / 1e5))
        }
        return points
    }
}
