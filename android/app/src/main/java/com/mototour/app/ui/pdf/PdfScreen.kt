package com.mototour.app.ui.pdf

import android.app.Application
import android.graphics.Bitmap
import android.graphics.pdf.PdfRenderer
import android.os.ParcelFileDescriptor
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.unit.dp
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewModelScope
import androidx.lifecycle.viewmodel.compose.viewModel
import com.mototour.app.data.AppDatabase
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File

class PdfViewModel(app: Application) : AndroidViewModel(app) {
    private val dao = AppDatabase.get(app).tourDao()

    private val _state = MutableStateFlow<PdfState>(PdfState.Loading)
    val state = _state.asStateFlow()

    fun load(tourId: Long) {
        viewModelScope.launch {
            val tour = dao.tourWithDays(tourId)?.tour
            if (tour == null || tour.pdfPath.isEmpty()) {
                _state.value = PdfState.Error("No PDF available")
                return@launch
            }
            val file = File(tour.pdfPath)
            if (!file.exists()) {
                _state.value = PdfState.Error("PDF file not found")
                return@launch
            }

            withContext(Dispatchers.IO) {
                try {
                    val fd = ParcelFileDescriptor.open(file, ParcelFileDescriptor.MODE_READ_ONLY)
                    val renderer = PdfRenderer(fd)
                    val pages = mutableListOf<Bitmap>()

                    for (i in 0 until renderer.pageCount) {
                        val page = renderer.openPage(i)
                        // Render at 2x for readability
                        val scale = 2
                        val bitmap = Bitmap.createBitmap(
                            page.width * scale, page.height * scale,
                            Bitmap.Config.ARGB_8888
                        )
                        bitmap.eraseColor(android.graphics.Color.WHITE)
                        page.render(bitmap, null, null, PdfRenderer.Page.RENDER_MODE_FOR_DISPLAY)
                        page.close()
                        pages.add(bitmap)
                    }
                    renderer.close()
                    fd.close()

                    _state.value = PdfState.Loaded(tour.name, pages)
                } catch (e: Exception) {
                    _state.value = PdfState.Error("Failed to render PDF: ${e.message}")
                }
            }
        }
    }

    override fun onCleared() {
        // Release bitmaps
        (_state.value as? PdfState.Loaded)?.pages?.forEach { it.recycle() }
    }
}

sealed interface PdfState {
    data object Loading : PdfState
    data class Loaded(val title: String, val pages: List<Bitmap>) : PdfState
    data class Error(val message: String) : PdfState
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PdfScreen(
    tourId: Long,
    onBack: () -> Unit,
    vm: PdfViewModel = viewModel()
) {
    val state by vm.state.collectAsStateWithLifecycle()

    LaunchedEffect(tourId) { vm.load(tourId) }

    when (val s = state) {
        PdfState.Loading -> {
            Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
        }
        is PdfState.Error -> {
            Scaffold(
                topBar = {
                    TopAppBar(
                        title = { Text("PDF") },
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
                Box(Modifier.fillMaxSize().padding(padding), contentAlignment = Alignment.Center) {
                    Text(s.message)
                }
            }
        }
        is PdfState.Loaded -> {
            Scaffold(
                topBar = {
                    TopAppBar(
                        title = { Text(s.title, maxLines = 1) },
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
                LazyColumn(
                    modifier = Modifier.fillMaxSize().padding(padding),
                    contentPadding = PaddingValues(8.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    itemsIndexed(s.pages) { index, bitmap ->
                        Card(elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)) {
                            Column {
                                Image(
                                    bitmap = bitmap.asImageBitmap(),
                                    contentDescription = "Page ${index + 1}",
                                    modifier = Modifier.fillMaxWidth(),
                                    contentScale = ContentScale.FillWidth
                                )
                                Text(
                                    "Page ${index + 1} of ${s.pages.size}",
                                    modifier = Modifier.padding(4.dp).align(Alignment.CenterHorizontally),
                                    style = MaterialTheme.typography.labelSmall,
                                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.5f)
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}
