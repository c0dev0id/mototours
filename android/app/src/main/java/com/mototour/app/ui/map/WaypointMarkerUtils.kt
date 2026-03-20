package com.mototour.app.ui.map

import androidx.core.content.ContextCompat
import com.mototour.app.R
import com.mototour.app.data.WaypointEntity
import com.mototour.app.data.WaypointType
import org.osmdroid.util.GeoPoint
import org.osmdroid.views.MapView
import org.osmdroid.views.overlay.Marker

object WaypointMarkerUtils {

    /** Returns the drawable resource ID for a given WaypointType. */
    fun iconResForType(type: WaypointType): Int = when (type) {
        WaypointType.START -> R.drawable.ic_marker_start
        WaypointType.END -> R.drawable.ic_marker_end
        WaypointType.MIDPOINT -> R.drawable.ic_marker_midpoint
        WaypointType.OVERNIGHT -> R.drawable.ic_marker_overnight
        WaypointType.VIA -> R.drawable.ic_marker_via
    }

    /** Creates an osmdroid Marker with the appropriate POI icon for the waypoint type. */
    fun createMarker(mapView: MapView, wpt: WaypointEntity): Marker {
        return Marker(mapView).apply {
            position = GeoPoint(wpt.lat, wpt.lon)
            title = wpt.name
            snippet = wpt.description
            icon = ContextCompat.getDrawable(mapView.context, iconResForType(wpt.type))
            if (wpt.type == WaypointType.VIA) {
                setAnchor(Marker.ANCHOR_CENTER, Marker.ANCHOR_CENTER)
            } else {
                setAnchor(Marker.ANCHOR_CENTER, Marker.ANCHOR_BOTTOM)
            }
        }
    }
}
