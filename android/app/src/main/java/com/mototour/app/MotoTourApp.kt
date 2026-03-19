package com.mototour.app

import android.app.Application
import com.mototour.app.data.BundleManager
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch
import org.osmdroid.config.Configuration
import java.io.File

class MotoTourApp : Application() {

    private val appScope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    override fun onCreate() {
        super.onCreate()

        // Configure osmdroid to use internal storage before any MapView is created.
        // Without this, osmdroid defaults to Environment.getExternalStorageDirectory()
        // which requires WRITE_EXTERNAL_STORAGE — unavailable on API 34.
        Configuration.getInstance().apply {
            userAgentValue = packageName
            osmdroidBasePath = File(filesDir, "osmdroid")
            osmdroidTileCache = File(cacheDir, "osmdroid")
        }

        // Seed bundled tours on first launch
        appScope.launch {
            try {
                BundleManager(this@MotoTourApp).seedFromAssets()
            } catch (_: Exception) {
                // Seeding failure must not crash the app
            }
        }
    }
}
