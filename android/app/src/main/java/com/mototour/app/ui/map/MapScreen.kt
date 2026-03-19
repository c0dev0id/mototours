package com.mototour.app.ui.map

import android.app.Application
import android.graphics.Color as AndroidColor
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Layers
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.viewinterop.AndroidView
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewModelScope
import androidx.lifecycle.viewmodel.compose.viewModel
import com.mototour.app.data.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import org.osmdroid.tileprovider.tilesource.TileSourceFactory
import org.osmdroid.util.BoundingBox
import org.osmdroid.util.GeoPoint
import org.osmdroid.views.MapView
import org.osmdroid.views.overlay.Marker
import org.osmdroid.views.overlay.Polyline
import java.io.File

class MapViewModel(app: Application) : AndroidViewModel(app) {
    private val dao = AppDatabase.get(app).tourDao()

    private val _state = MutableStateFlow<MapState>(MapState.Loading)
    val state = _state.asStateFlow()

    fun load(dayId: Long) {
        viewModelScope.launch {
            val dayWithWaypoints = dao.dayWithWaypoints(dayId)
            if (dayWithWaypoints != null) {
                // Parse GPX for route points
                val gpxFile = File(dayWithWaypoints.day.gpxPath)
                val routePoints = if (gpxFile.exists()) {
                    gpxFile.inputStream().use { GpxParser.parse(it) }.routePoints
                } else emptyList()

                _state.value = MapState.Loaded(dayWithWaypoints, routePoints)
            } else {
                _state.value = MapState.Error
            }
        }
    }
}

sealed interface MapState {
    data object Loading : MapState
    data object Error : MapState
    data class Loaded(val day: DayWithWaypoints, val routePoints: List<GpxPoint>) : MapState
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MapScreen(
    dayId: Long,
    onBack: () -> Unit,
    vm: MapViewModel = viewModel()
) {
    val state by vm.state.collectAsStateWithLifecycle()

    LaunchedEffect(dayId) { vm.load(dayId) }

    when (val s = state) {
        MapState.Loading -> {
            Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
        }
        MapState.Error -> {
            Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                Text("Day not found")
            }
        }
        is MapState.Loaded -> {
            val day = s.day.day
            val waypoints = s.day.waypoints.sortedBy { it.orderIndex }
            val routePoints = s.routePoints

            Scaffold(
                topBar = {
                    TopAppBar(
                        title = { Text(day.name, maxLines = 1) },
                        navigationIcon = {
                            IconButton(onClick = onBack) {
                                Icon(Icons.AutoMirrored.Filled.ArrowBack, "Back")
                            }
                        },
                        colors = TopAppBarDefaults.topAppBarColors(
                            containerColor = MaterialTheme.colorScheme.primary,
                            titleContentColor = MaterialTheme.colorScheme.onPrimary,
                            navigationIconContentColor = MaterialTheme.colorScheme.onPrimary
                        )
                    )
                }
            ) { padding ->
                AndroidView(
                    modifier = Modifier.fillMaxSize().padding(padding),
                    factory = { ctx ->
                        MapView(ctx).apply {
                            setTileSource(TileSourceFactory.MAPNIK)
                            setMultiTouchControls(true)
                            isTilesScaledToDpi = true

                            // Draw route polyline
                            if (routePoints.isNotEmpty()) {
                                val polyline = Polyline().apply {
                                    outlinePaint.color = AndroidColor.rgb(0x2C, 0x55, 0x30)
                                    outlinePaint.strokeWidth = 8f
                                    setPoints(routePoints.map { GeoPoint(it.lat, it.lon) })
                                }
                                overlays.add(polyline)
                            }

                            // Add waypoint markers
                            for (wpt in waypoints) {
                                val marker = Marker(this).apply {
                                    position = GeoPoint(wpt.lat, wpt.lon)
                                    title = wpt.name
                                    snippet = wpt.description
                                    setAnchor(Marker.ANCHOR_CENTER, Marker.ANCHOR_BOTTOM)
                                }
                                // Color markers by type
                                // Default markers are fine; we set alpha to distinguish
                                overlays.add(marker)
                            }

                            // Zoom to fit route
                            val allPoints = if (routePoints.isNotEmpty()) {
                                routePoints.map { GeoPoint(it.lat, it.lon) }
                            } else {
                                waypoints.map { GeoPoint(it.lat, it.lon) }
                            }

                            if (allPoints.isNotEmpty()) {
                                val box = BoundingBox.fromGeoPoints(allPoints)
                                post {
                                    zoomToBoundingBox(box.increaseByScale(1.2f), true)
                                }
                            }
                        }
                    }
                )
            }
        }
    }
}
