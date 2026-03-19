package com.mototour.app

import android.app.Application
import com.mototour.app.data.BundleManager
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch

class MotoTourApp : Application() {

    private val appScope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    override fun onCreate() {
        super.onCreate()
        // Seed bundled tours on first launch
        appScope.launch {
            BundleManager(this@MotoTourApp).seedFromAssets()
        }
    }
}
