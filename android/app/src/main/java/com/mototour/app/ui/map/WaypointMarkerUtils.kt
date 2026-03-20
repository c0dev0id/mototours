package com.mototour.app.ui.map

import androidx.core.content.ContextCompat
import com.mototour.app.R
import com.mototour.app.data.WaypointEntity
import com.mototour.app.data.WaypointType
import org.osmdroid.util.GeoPoint
import org.osmdroid.views.MapView
import org.osmdroid.views.overlay.Marker

object WaypointMarkerUtils {

    /** Returns the drawable resource ID for a given WaypointType and description. */
    fun iconResForType(type: WaypointType, description: String = ""): Int = when (type) {
        WaypointType.START    -> R.drawable.ic_marker_start
        WaypointType.END      -> R.drawable.ic_marker_end
        WaypointType.MIDPOINT -> R.drawable.ic_marker_midpoint
        WaypointType.OVERNIGHT -> R.drawable.ic_marker_overnight
        WaypointType.OPTIONAL -> R.drawable.ic_marker_optional
        WaypointType.VIA      -> iconResForViaPoi(description)
    }

    private fun iconResForViaPoi(description: String): Int {
        val d = description.lowercase()
        return when {
            d.containsAny("pass", "col ", "summit", "historic mountain", "pass village")
                -> R.drawable.ic_marker_summit
            d.containsAny("viewpoint", "panorama", "scenic", "belvedere")
                -> R.drawable.ic_marker_scenic
            d.containsAny("castle", "burg", "schloss", "festung", "veste", "trifels", "ruin")
                -> R.drawable.ic_marker_castle
            d.containsAny("waterfall", "wasserfall")
                -> R.drawable.ic_marker_waterfall
            d.containsAny(" lake", "mummelsee", "titisee", "schluchsee", "bodensee", "edersee")
                -> R.drawable.ic_marker_lake
            d.containsAny("museum")
                -> R.drawable.ic_marker_museum
            d.containsAny("monastery", "abbey", "kloster", "cistercian", "romanesque", "baroque")
                -> R.drawable.ic_marker_monastery
            d.containsAny("spa", "thermal", "bad ")
                -> R.drawable.ic_marker_spa
            d.containsAny("winery", "brewery", "brauerei", "wine route", "wine village", "wine town")
                -> R.drawable.ic_marker_winery
            else -> R.drawable.ic_marker_via
        }
    }

    private fun String.containsAny(vararg keywords: String) = keywords.any { this.contains(it) }

    /** Creates an osmdroid Marker with the appropriate POI icon for the waypoint type. */
    fun createMarker(mapView: MapView, wpt: WaypointEntity): Marker {
        return Marker(mapView).apply {
            position = GeoPoint(wpt.lat, wpt.lon)
            title = wpt.name
            snippet = wpt.description
            icon = ContextCompat.getDrawable(mapView.context, iconResForType(wpt.type, wpt.description))
            if (wpt.type == WaypointType.VIA || wpt.type == WaypointType.OPTIONAL) {
                setAnchor(Marker.ANCHOR_CENTER, Marker.ANCHOR_CENTER)
            } else {
                setAnchor(Marker.ANCHOR_CENTER, Marker.ANCHOR_BOTTOM)
            }
        }
    }
}
