package com.mototour.app.ui.detail

import android.app.Application
import android.graphics.Color as AndroidColor
import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewModelScope
import androidx.lifecycle.viewmodel.compose.viewModel
import com.mototour.app.data.*
import com.mototour.app.ui.theme.Accent
import com.mototour.app.ui.theme.Blue
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.osmdroid.tileprovider.tilesource.TileSourceFactory
import org.osmdroid.util.BoundingBox
import org.osmdroid.util.GeoPoint
import org.osmdroid.views.MapView
import org.osmdroid.views.overlay.Marker
import org.osmdroid.views.overlay.Polyline
import java.io.File

data class DayRouteData(
    val dayNumber: Int,
    val name: String,
    val routePoints: List<GpxPoint>,
    val startEnd: List<WaypointEntity>
)

private val routeColors = listOf(
    AndroidColor.rgb(0x2C, 0x55, 0x30),  // Dark green
    AndroidColor.rgb(0xC8, 0x61, 0x1A),  // Orange
    AndroidColor.rgb(0x2B, 0x54, 0x7E),  // Blue
    AndroidColor.rgb(0x8B, 0x23, 0x52),  // Burgundy
    AndroidColor.rgb(0x6B, 0x8E, 0x23),  // Olive green
    AndroidColor.rgb(0x80, 0x46, 0x00),  // Brown
)

private val routeComposeColors = listOf(
    Color(0xFF2C5530),
    Color(0xFFC8611A),
    Color(0xFF2B547E),
    Color(0xFF8B2352),
    Color(0xFF6B8E23),
    Color(0xFF804600),
)

class TourDetailViewModel(app: Application) : AndroidViewModel(app) {
    private val dao = AppDatabase.get(app).tourDao()
    private val bundleManager = BundleManager(app)

    private val _state = MutableStateFlow<TourDetailState>(TourDetailState.Loading)
    val state = _state.asStateFlow()

    private val _exportResult = MutableStateFlow<String?>(null)
    val exportResult = _exportResult.asStateFlow()

    fun load(tourId: Long) {
        viewModelScope.launch {
            val tour = dao.tourWithDays(tourId)
            val days = dao.daysWithWaypoints(tourId)
            if (tour == null) {
                _state.value = TourDetailState.Error
                return@launch
            }

            // Load GPX route data for overview map (multi-day tours only)
            val dayRoutes = if (days.size > 1) {
                withContext(Dispatchers.IO) {
                    days.sortedBy { it.day.dayNumber }.mapNotNull { dw ->
                        val gpxFile = File(dw.day.gpxPath)
                        if (!gpxFile.exists()) return@mapNotNull null
                        val gpxData = gpxFile.inputStream().use { GpxParser.parse(it) }
                        val startEnd = dw.waypoints.filter {
                            it.type == WaypointType.START || it.type == WaypointType.END ||
                                    it.type == WaypointType.OVERNIGHT
                        }
                        DayRouteData(dw.day.dayNumber, dw.day.name, gpxData.routePoints, startEnd)
                    }
                }
            } else emptyList()

            _state.value = TourDetailState.Loaded(tour, days, dayRoutes)

            // Calculate road-following routes via OSRM for the overview map
            if (dayRoutes.isNotEmpty()) {
                val calculatedDayRoutes = days.sortedBy { it.day.dayNumber }.mapNotNull { dw ->
                    val waypoints = dw.waypoints
                        .sortedBy { it.orderIndex }
                        .map { GpxPoint(it.lat, it.lon) }
                    if (waypoints.size < 2) return@mapNotNull null
                    val calculated = RouteCalculator.calculateRoute(waypoints)
                    val startEnd = dw.waypoints.filter {
                        it.type == WaypointType.START || it.type == WaypointType.END ||
                                it.type == WaypointType.OVERNIGHT
                    }
                    if (calculated != null && calculated.size >= 2) {
                        DayRouteData(dw.day.dayNumber, dw.day.name, calculated, startEnd)
                    } else {
                        // Keep GPX route points as fallback
                        dayRoutes.find { it.dayNumber == dw.day.dayNumber }
                    }
                }
                if (calculatedDayRoutes.isNotEmpty()) {
                    _state.value = TourDetailState.Loaded(tour, days, calculatedDayRoutes)
                }
            }
        }
    }

    fun export(tourId: Long, uri: Uri) {
        viewModelScope.launch {
            val ok = bundleManager.exportTour(tourId, uri)
            _exportResult.value = if (ok) "Tour exported" else "Export failed"
        }
    }

    fun deleteTour(tourId: Long, onDone: () -> Unit) {
        viewModelScope.launch {
            val tour = dao.tourWithDays(tourId)?.tour ?: return@launch
            dao.deleteTour(tour)
            onDone()
        }
    }

    fun clearExportResult() { _exportResult.value = null }
}

sealed interface TourDetailState {
    data object Loading : TourDetailState
    data object Error : TourDetailState
    data class Loaded(
        val tour: TourWithDays,
        val days: List<DayWithWaypoints>,
        val dayRoutes: List<DayRouteData> = emptyList()
    ) : TourDetailState
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TourDetailScreen(
    tourId: Long,
    onDayMapClick: (Long) -> Unit,
    onPdfClick: () -> Unit,
    onBack: () -> Unit,
    vm: TourDetailViewModel = viewModel()
) {
    val state by vm.state.collectAsStateWithLifecycle()
    val exportResult by vm.exportResult.collectAsStateWithLifecycle()
    val snackbarHostState = remember { SnackbarHostState() }

    LaunchedEffect(tourId) { vm.load(tourId) }

    LaunchedEffect(exportResult) {
        exportResult?.let {
            snackbarHostState.showSnackbar(it)
            vm.clearExportResult()
        }
    }

    val exportLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.CreateDocument("application/zip")
    ) { uri: Uri? ->
        uri?.let { vm.export(tourId, it) }
    }

    var showDeleteDialog by remember { mutableStateOf(false) }

    when (val s = state) {
        TourDetailState.Loading -> {
            Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
        }
        TourDetailState.Error -> {
            Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                Text("Tour not found")
            }
        }
        is TourDetailState.Loaded -> {
            val tour = s.tour.tour
            val days = s.days.sortedBy { it.day.dayNumber }
            val dayRoutes = s.dayRoutes

            if (showDeleteDialog) {
                AlertDialog(
                    onDismissRequest = { showDeleteDialog = false },
                    title = { Text("Delete tour?") },
                    text = { Text("\"${tour.name}\" will be permanently removed.") },
                    confirmButton = {
                        TextButton(onClick = {
                            showDeleteDialog = false
                            vm.deleteTour(tourId) { onBack() }
                        }) { Text("Delete", color = MaterialTheme.colorScheme.error) }
                    },
                    dismissButton = {
                        TextButton(onClick = { showDeleteDialog = false }) { Text("Cancel") }
                    }
                )
            }

            Scaffold(
                snackbarHost = { SnackbarHost(snackbarHostState) },
                topBar = {
                    TopAppBar(
                        title = { Text(tour.name, maxLines = 1) },
                        navigationIcon = {
                            IconButton(onClick = onBack) {
                                Icon(Icons.AutoMirrored.Filled.ArrowBack, "Back")
                            }
                        },
                        colors = TopAppBarDefaults.topAppBarColors(
                            containerColor = MaterialTheme.colorScheme.primary,
                            titleContentColor = MaterialTheme.colorScheme.onPrimary,
                            navigationIconContentColor = MaterialTheme.colorScheme.onPrimary,
                            actionIconContentColor = MaterialTheme.colorScheme.onPrimary
                        ),
                        actions = {
                            IconButton(onClick = {
                                exportLauncher.launch("${tour.slug}.zip")
                            }) {
                                Icon(Icons.Default.Share, "Export")
                            }
                            IconButton(onClick = { showDeleteDialog = true }) {
                                Icon(Icons.Default.Delete, "Delete")
                            }
                        }
                    )
                }
            ) { padding ->
                LazyColumn(
                    modifier = Modifier.fillMaxSize().padding(padding),
                    contentPadding = PaddingValues(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    // Tour info header
                    item {
                        TourInfoHeader(tour)
                    }

                    // PDF button
                    if (tour.pdfPath.isNotEmpty()) {
                        item {
                            OutlinedButton(
                                onClick = onPdfClick,
                                modifier = Modifier.fillMaxWidth()
                            ) {
                                Icon(Icons.Default.PictureAsPdf, null,
                                    modifier = Modifier.size(18.dp))
                                Spacer(Modifier.width(8.dp))
                                Text("View Tour Guide (PDF)")
                            }
                        }
                    }

                    // Overview map for multi-day tours
                    if (dayRoutes.isNotEmpty()) {
                        item {
                            TourOverviewMap(dayRoutes)
                        }
                    }

                    // Day cards
                    item {
                        Text(
                            if (days.size == 1) "Route" else "Days",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            modifier = Modifier.padding(top = 8.dp)
                        )
                    }

                    items(days, key = { it.day.id }) { dayWithWaypoints ->
                        DayCard(dayWithWaypoints, onClick = { onDayMapClick(dayWithWaypoints.day.id) })
                    }
                }
            }
        }
    }
}

@Composable
private fun TourOverviewMap(dayRoutes: List<DayRouteData>) {
    Card(
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column {
            Text(
                "Tour Overview",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.padding(start = 16.dp, top = 12.dp, end = 16.dp)
            )

            AndroidView(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(250.dp)
                    .padding(horizontal = 8.dp, vertical = 8.dp),
                factory = { ctx ->
                    MapView(ctx).apply {
                        setTileSource(TileSourceFactory.MAPNIK)
                        setMultiTouchControls(true)
                        isTilesScaledToDpi = true

                        val allGeoPoints = mutableListOf<GeoPoint>()

                        dayRoutes.forEachIndexed { index, dayRoute ->
                            if (dayRoute.routePoints.isEmpty()) return@forEachIndexed
                            val color = routeColors[index % routeColors.size]
                            val geoPoints = dayRoute.routePoints.map { GeoPoint(it.lat, it.lon) }
                            allGeoPoints.addAll(geoPoints)

                            val polyline = Polyline().apply {
                                outlinePaint.color = color
                                outlinePaint.strokeWidth = 6f
                                setPoints(geoPoints)
                            }
                            overlays.add(polyline)

                            // Add markers for start/end/overnight waypoints
                            for (wpt in dayRoute.startEnd) {
                                val marker = Marker(this).apply {
                                    position = GeoPoint(wpt.lat, wpt.lon)
                                    title = wpt.name
                                    snippet = wpt.description
                                    setAnchor(Marker.ANCHOR_CENTER, Marker.ANCHOR_BOTTOM)
                                }
                                overlays.add(marker)
                            }
                        }

                        if (allGeoPoints.isNotEmpty()) {
                            val box = BoundingBox.fromGeoPoints(allGeoPoints)
                            post {
                                zoomToBoundingBox(box.increaseByScale(1.2f), true)
                            }
                        }
                    }
                }
            )

            // Legend
            Column(
                modifier = Modifier.padding(start = 16.dp, end = 16.dp, bottom = 12.dp),
                verticalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                dayRoutes.forEachIndexed { index, dayRoute ->
                    val color = routeComposeColors[index % routeComposeColors.size]
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Box(
                            Modifier
                                .size(10.dp)
                                .clip(CircleShape)
                                .background(color)
                        )
                        Spacer(Modifier.width(8.dp))
                        Text(
                            dayRoute.name,
                            style = MaterialTheme.typography.bodySmall
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun TourInfoHeader(tour: TourEntity) {
    Card(
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.3f)
        )
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                AssistChip(
                    onClick = {},
                    label = { Text(tour.category.label) },
                    leadingIcon = {
                        Icon(Icons.Default.TwoWheeler, null, modifier = Modifier.size(16.dp))
                    }
                )
                Spacer(Modifier.width(8.dp))
                Text("${tour.totalDistanceKm} km total", style = MaterialTheme.typography.bodyMedium)
            }
            if (tour.region.isNotEmpty()) {
                Spacer(Modifier.height(8.dp))
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Default.Place, null, modifier = Modifier.size(16.dp), tint = Accent)
                    Spacer(Modifier.width(4.dp))
                    Text(tour.region, color = Accent, style = MaterialTheme.typography.bodyMedium)
                }
            }
            if (tour.overview.isNotEmpty()) {
                Spacer(Modifier.height(12.dp))
                Text(tour.overview, style = MaterialTheme.typography.bodyMedium)
            }
            if (tour.highlights.isNotEmpty()) {
                Spacer(Modifier.height(8.dp))
                Text("Highlights", fontWeight = FontWeight.Bold,
                    style = MaterialTheme.typography.bodySmall, color = Accent)
                Text(tour.highlights, style = MaterialTheme.typography.bodySmall)
            }
            if (tour.roadCharacter.isNotEmpty()) {
                Spacer(Modifier.height(8.dp))
                Text("Road Character", fontWeight = FontWeight.Bold,
                    style = MaterialTheme.typography.bodySmall, color = Blue)
                Text(tour.roadCharacter, style = MaterialTheme.typography.bodySmall)
            }
        }
    }
}

@Composable
private fun DayCard(dayWithWaypoints: DayWithWaypoints, onClick: () -> Unit) {
    val day = dayWithWaypoints.day
    val wpts = dayWithWaypoints.waypoints.sortedBy { it.orderIndex }
    val midpoint = wpts.find { it.type == WaypointType.MIDPOINT }
    val overnight = wpts.find { it.type == WaypointType.OVERNIGHT }
    val context = LocalContext.current

    Card(
        modifier = Modifier.fillMaxWidth(),
        onClick = onClick,
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Default.Map, null,
                    modifier = Modifier.size(20.dp),
                    tint = MaterialTheme.colorScheme.primary)
                Spacer(Modifier.width(8.dp))
                Text(day.name, fontWeight = FontWeight.Bold,
                    style = MaterialTheme.typography.titleSmall,
                    modifier = Modifier.weight(1f))
                Text("${day.distanceKm} km",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f))
                Spacer(Modifier.width(8.dp))
                IconButton(
                    onClick = {
                        GpxShareHelper.shareGpxFile(context, day.gpxPath, day.name)
                    },
                    modifier = Modifier.size(32.dp)
                ) {
                    Icon(Icons.Default.Share, "Share GPX",
                        modifier = Modifier.size(18.dp),
                        tint = MaterialTheme.colorScheme.primary)
                }
            }

            if (day.description.isNotEmpty()) {
                Spacer(Modifier.height(6.dp))
                Text(day.description,
                    style = MaterialTheme.typography.bodySmall,
                    maxLines = 3,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f))
            }

            if (midpoint != null || overnight != null) {
                Spacer(Modifier.height(6.dp))
                Row {
                    midpoint?.let {
                        Icon(Icons.Default.Restaurant, null,
                            modifier = Modifier.size(14.dp), tint = Accent)
                        Spacer(Modifier.width(4.dp))
                        Text(it.name, style = MaterialTheme.typography.bodySmall, color = Accent)
                    }
                    if (midpoint != null && overnight != null) Spacer(Modifier.width(12.dp))
                    overnight?.let {
                        Icon(Icons.Default.Hotel, null,
                            modifier = Modifier.size(14.dp), tint = Blue)
                        Spacer(Modifier.width(4.dp))
                        Text(it.name, style = MaterialTheme.typography.bodySmall, color = Blue)
                    }
                }
            }

            Spacer(Modifier.height(8.dp))
            Text("Tap to view on map",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.primary.copy(alpha = 0.6f))
        }
    }
}
