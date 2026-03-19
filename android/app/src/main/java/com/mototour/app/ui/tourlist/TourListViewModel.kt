package com.mototour.app.ui.tourlist

import android.app.Application
import android.net.Uri
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.mototour.app.data.AppDatabase
import com.mototour.app.data.BundleManager
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class TourListViewModel(app: Application) : AndroidViewModel(app) {

    private val dao = AppDatabase.get(app).tourDao()
    private val bundleManager = BundleManager(app)

    val tours = dao.allToursWithDays()

    private val _importResult = MutableStateFlow<String?>(null)
    val importResult = _importResult.asStateFlow()

    fun importZip(uri: Uri) {
        viewModelScope.launch {
            val id = bundleManager.importZip(uri)
            _importResult.value = if (id != null) "Tour imported" else "Import failed or duplicate"
        }
    }

    fun importLooseFiles(uris: List<Uri>) {
        viewModelScope.launch {
            // Separate PDFs from GPX files
            val context = getApplication<Application>()
            val pdfUri = uris.firstOrNull { uri ->
                context.contentResolver.getType(uri)?.contains("pdf") == true ||
                    uri.toString().endsWith(".pdf", ignoreCase = true)
            }
            val gpxUris = uris.filter { uri ->
                val type = context.contentResolver.getType(uri) ?: ""
                val path = uri.toString().lowercase()
                type.contains("xml") || type.contains("gpx") || type.contains("octet-stream") ||
                    path.endsWith(".gpx")
            }

            if (gpxUris.isEmpty()) {
                _importResult.value = "No GPX files found in selection"
                return@launch
            }

            val id = bundleManager.importLooseFiles(pdfUri, gpxUris)
            _importResult.value = if (id != null) "Tour imported (${gpxUris.size} day(s))"
                else "Import failed or duplicate"
        }
    }

    fun clearImportResult() { _importResult.value = null }
}
