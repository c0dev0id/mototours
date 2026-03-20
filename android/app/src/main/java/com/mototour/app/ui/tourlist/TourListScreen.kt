package com.mototour.app.ui.tourlist

import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.mototour.app.data.TourCategory
import com.mototour.app.data.TourWithDays
import com.mototour.app.ui.theme.Accent
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TourListScreen(
    onTourClick: (Long) -> Unit,
    vm: TourListViewModel = viewModel()
) {
    val tours by vm.tours.collectAsStateWithLifecycle(initialValue = emptyList())
    val importResult by vm.importResult.collectAsStateWithLifecycle()
    val currentFilter by vm.filter.collectAsStateWithLifecycle()
    var showImportMenu by remember { mutableStateOf(false) }

    // ZIP picker
    val zipPicker = rememberLauncherForActivityResult(
        ActivityResultContracts.OpenDocument()
    ) { uri: Uri? ->
        uri?.let { vm.importZip(it) }
    }

    // Loose file picker (multiple files: PDF + GPX)
    val loosePicker = rememberLauncherForActivityResult(
        ActivityResultContracts.OpenMultipleDocuments()
    ) { uris: List<Uri> ->
        if (uris.isNotEmpty()) vm.importLooseFiles(uris)
    }

    // Show snackbar on import result
    val snackbarHostState = remember { SnackbarHostState() }
    LaunchedEffect(importResult) {
        importResult?.let {
            snackbarHostState.showSnackbar(it)
            vm.clearImportResult()
        }
    }

    Scaffold(
        snackbarHost = { SnackbarHost(snackbarHostState) },
        topBar = {
            TopAppBar(
                title = { Text("MotoTour") },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primary,
                    titleContentColor = MaterialTheme.colorScheme.onPrimary,
                    actionIconContentColor = MaterialTheme.colorScheme.onPrimary
                ),
                actions = {
                    Box {
                        IconButton(onClick = { showImportMenu = true }) {
                            Icon(Icons.Default.Add, contentDescription = "Import")
                        }
                        DropdownMenu(
                            expanded = showImportMenu,
                            onDismissRequest = { showImportMenu = false }
                        ) {
                            DropdownMenuItem(
                                text = { Text("Import ZIP bundle") },
                                leadingIcon = { Icon(Icons.Default.FolderZip, null) },
                                onClick = {
                                    showImportMenu = false
                                    zipPicker.launch(arrayOf(
                                        "application/zip",
                                        "application/x-zip-compressed"
                                    ))
                                }
                            )
                            DropdownMenuItem(
                                text = { Text("Import PDF + GPX files") },
                                leadingIcon = { Icon(Icons.Default.AttachFile, null) },
                                onClick = {
                                    showImportMenu = false
                                    loosePicker.launch(arrayOf(
                                        "application/pdf",
                                        "application/gpx+xml",
                                        "application/xml",
                                        "text/xml",
                                        "application/octet-stream"
                                    ))
                                }
                            )
                        }
                    }
                }
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier.fillMaxSize().padding(padding)
        ) {
            // Filter chips
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 8.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                FilterChip(
                    selected = currentFilter == TourFilter.ALL,
                    onClick = { vm.setFilter(TourFilter.ALL) },
                    label = { Text("All") },
                    leadingIcon = if (currentFilter == TourFilter.ALL) {
                        { Icon(Icons.Default.Done, null, modifier = Modifier.size(18.dp)) }
                    } else null
                )
                FilterChip(
                    selected = currentFilter == TourFilter.FAVORITES,
                    onClick = { vm.setFilter(TourFilter.FAVORITES) },
                    label = { Text("Favorites") },
                    leadingIcon = {
                        Icon(
                            if (currentFilter == TourFilter.FAVORITES) Icons.Default.Favorite
                            else Icons.Default.FavoriteBorder,
                            null,
                            modifier = Modifier.size(18.dp)
                        )
                    }
                )
                FilterChip(
                    selected = currentFilter == TourFilter.COMPLETED,
                    onClick = { vm.setFilter(TourFilter.COMPLETED) },
                    label = { Text("Completed") },
                    leadingIcon = {
                        Icon(
                            if (currentFilter == TourFilter.COMPLETED) Icons.Default.CheckCircle
                            else Icons.Default.CheckCircleOutline,
                            null,
                            modifier = Modifier.size(18.dp)
                        )
                    }
                )
            }

            if (tours.isEmpty()) {
                Box(
                    Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Icon(
                            Icons.Default.TwoWheeler, null,
                            modifier = Modifier.size(64.dp),
                            tint = MaterialTheme.colorScheme.primary.copy(alpha = 0.4f)
                        )
                        Spacer(Modifier.height(16.dp))
                        Text(
                            when (currentFilter) {
                                TourFilter.ALL -> "No tours yet"
                                TourFilter.FAVORITES -> "No favorite tours"
                                TourFilter.COMPLETED -> "No completed tours"
                            },
                            style = MaterialTheme.typography.titleMedium
                        )
                        Spacer(Modifier.height(8.dp))
                        Text(
                            when (currentFilter) {
                                TourFilter.ALL -> "Import tours using the + button above"
                                TourFilter.FAVORITES -> "Tap the heart icon on a tour to add it to favorites"
                                TourFilter.COMPLETED -> "Mark tours as completed from the tour detail screen"
                            },
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                        )
                    }
                }
            } else {
                val grouped = tours.groupBy { it.tour.category }
                LazyColumn(
                    modifier = Modifier.fillMaxSize(),
                    contentPadding = PaddingValues(bottom = 16.dp)
                ) {
                    for (category in TourCategory.entries) {
                        val categoryTours = grouped[category] ?: continue
                        item(key = "header_$category") {
                            CategoryHeader(category, categoryTours.size)
                        }
                        items(categoryTours, key = { it.tour.id }) { tourWithDays ->
                            TourCard(
                                tourWithDays,
                                onClick = { onTourClick(tourWithDays.tour.id) },
                                onFavoriteClick = {
                                    vm.toggleFavorite(tourWithDays.tour.id, tourWithDays.tour.isFavorite)
                                }
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun CategoryHeader(category: TourCategory, count: Int) {
    Surface(
        modifier = Modifier.fillMaxWidth().padding(top = 16.dp),
        color = MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.3f)
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 16.dp, vertical = 12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = category.label,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.primary
            )
            Spacer(Modifier.width(8.dp))
            Text(
                text = "($count)",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.5f)
            )
        }
    }
}

@Composable
private fun TourCard(tourWithDays: TourWithDays, onClick: () -> Unit, onFavoriteClick: () -> Unit) {
    val tour = tourWithDays.tour
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 6.dp)
            .clickable(onClick = onClick),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = tour.name,
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.weight(1f)
                )
                if (tour.completedAt != null) {
                    Icon(
                        Icons.Default.CheckCircle, "Completed",
                        modifier = Modifier.size(20.dp),
                        tint = MaterialTheme.colorScheme.primary
                    )
                    Spacer(Modifier.width(4.dp))
                }
                IconButton(
                    onClick = onFavoriteClick,
                    modifier = Modifier.size(32.dp)
                ) {
                    Icon(
                        if (tour.isFavorite) Icons.Default.Favorite else Icons.Default.FavoriteBorder,
                        contentDescription = if (tour.isFavorite) "Remove from favorites" else "Add to favorites",
                        modifier = Modifier.size(20.dp),
                        tint = if (tour.isFavorite) MaterialTheme.colorScheme.error else MaterialTheme.colorScheme.onSurface.copy(alpha = 0.5f)
                    )
                }
            }
            Spacer(Modifier.height(4.dp))
            Row(verticalAlignment = Alignment.CenterVertically) {
                if (tour.region.isNotEmpty()) {
                    Icon(Icons.Default.Place, null, modifier = Modifier.size(14.dp),
                        tint = Accent)
                    Spacer(Modifier.width(4.dp))
                    Text(tour.region, style = MaterialTheme.typography.bodySmall,
                        color = Accent)
                    Spacer(Modifier.width(12.dp))
                }
                Icon(Icons.Default.Route, null, modifier = Modifier.size(14.dp),
                    tint = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.5f))
                Spacer(Modifier.width(4.dp))
                Text(
                    "${tour.totalDistanceKm} km",
                    style = MaterialTheme.typography.bodySmall
                )
                if (tour.dayCount > 1) {
                    Spacer(Modifier.width(12.dp))
                    Icon(Icons.Default.CalendarMonth, null, modifier = Modifier.size(14.dp),
                        tint = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.5f))
                    Spacer(Modifier.width(4.dp))
                    Text(
                        "${tour.dayCount} days",
                        style = MaterialTheme.typography.bodySmall
                    )
                }
            }
            if (tour.completedAt != null) {
                Spacer(Modifier.height(4.dp))
                val dateStr = SimpleDateFormat("MMM d, yyyy", Locale.getDefault())
                    .format(Date(tour.completedAt))
                Text(
                    "Completed $dateStr",
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.primary.copy(alpha = 0.7f)
                )
            }
            if (tour.overview.isNotEmpty()) {
                Spacer(Modifier.height(8.dp))
                Text(
                    text = tour.overview,
                    style = MaterialTheme.typography.bodySmall,
                    maxLines = 2,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
                )
            }
        }
    }
}
