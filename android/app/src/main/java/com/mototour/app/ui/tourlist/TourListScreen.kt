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
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.mototour.app.data.TourCategory
import com.mototour.app.data.TourWithDays
import com.mototour.app.ui.theme.Accent

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TourListScreen(
    onTourClick: (Long) -> Unit,
    vm: TourListViewModel = viewModel()
) {
    val tours by vm.tours.collectAsStateWithLifecycle(initialValue = emptyList())
    val importResult by vm.importResult.collectAsStateWithLifecycle()
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
        if (tours.isEmpty()) {
            Box(
                Modifier.fillMaxSize().padding(padding),
                contentAlignment = Alignment.Center
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Icon(
                        Icons.Default.TwoWheeler, null,
                        modifier = Modifier.size(64.dp),
                        tint = MaterialTheme.colorScheme.primary.copy(alpha = 0.4f)
                    )
                    Spacer(Modifier.height(16.dp))
                    Text("No tours yet", style = MaterialTheme.typography.titleMedium)
                    Spacer(Modifier.height(8.dp))
                    Text("Import tours using the + button above",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f))
                }
            }
        } else {
            val grouped = tours.groupBy { it.tour.category }
            LazyColumn(
                modifier = Modifier.fillMaxSize().padding(padding),
                contentPadding = PaddingValues(bottom = 16.dp)
            ) {
                for (category in TourCategory.entries) {
                    val categoryTours = grouped[category] ?: continue
                    item(key = "header_$category") {
                        CategoryHeader(category, categoryTours.size)
                    }
                    items(categoryTours, key = { it.tour.id }) { tourWithDays ->
                        TourCard(tourWithDays, onClick = { onTourClick(tourWithDays.tour.id) })
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
private fun TourCard(tourWithDays: TourWithDays, onClick: () -> Unit) {
    val tour = tourWithDays.tour
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 6.dp)
            .clickable(onClick = onClick),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = tour.name,
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.Bold
            )
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
