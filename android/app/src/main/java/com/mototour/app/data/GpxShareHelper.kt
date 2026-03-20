package com.mototour.app.data

import android.content.Context
import android.content.Intent
import androidx.core.content.FileProvider
import java.io.File

object GpxShareHelper {

    fun shareGpxFile(context: Context, gpxPath: String, dayName: String) {
        val gpxFile = File(gpxPath)
        if (!gpxFile.exists()) return

        val uri = FileProvider.getUriForFile(
            context,
            "${context.packageName}.fileprovider",
            gpxFile
        )

        val intent = Intent(Intent.ACTION_SEND).apply {
            type = "application/gpx+xml"
            putExtra(Intent.EXTRA_STREAM, uri)
            putExtra(Intent.EXTRA_SUBJECT, dayName)
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        }

        context.startActivity(Intent.createChooser(intent, "Open GPX in\u2026"))
    }
}
