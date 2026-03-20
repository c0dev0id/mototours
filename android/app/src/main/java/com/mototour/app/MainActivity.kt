package com.mototour.app

import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.runtime.*
import androidx.lifecycle.lifecycleScope
import com.mototour.app.data.BundleManager
import com.mototour.app.data.UpdateChecker
import com.mototour.app.data.UpdateInfo
import com.mototour.app.ui.MotoTourNavHost
import com.mototour.app.ui.UpdateDialog
import com.mototour.app.ui.theme.MotoTourTheme
import kotlinx.coroutines.launch

class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        // Handle ZIP file opened from external app
        handleIncomingIntent(intent)

        setContent {
            MotoTourTheme {
                var pendingUpdate by remember { mutableStateOf<UpdateInfo?>(null) }

                // Check for updates on first composition
                LaunchedEffect(Unit) {
                    if (UpdateChecker.isOnline(applicationContext)) {
                        pendingUpdate = UpdateChecker.checkForUpdate(BuildConfig.GIT_SHA)
                    }
                }

                if (pendingUpdate != null) {
                    UpdateDialog(
                        update = pendingUpdate!!,
                        onInstall = {
                            lifecycleScope.launch {
                                val apk = UpdateChecker.downloadApk(applicationContext, pendingUpdate!!)
                                if (apk != null) {
                                    UpdateChecker.installApk(applicationContext, apk)
                                }
                                pendingUpdate = null
                            }
                        },
                        onDismiss = { pendingUpdate = null }
                    )
                }

                MotoTourNavHost()
            }
        }
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        handleIncomingIntent(intent)
    }

    private fun handleIncomingIntent(intent: Intent?) {
        val uri = intent?.data ?: return
        if (intent.action == Intent.ACTION_VIEW) {
            lifecycleScope.launch {
                BundleManager(applicationContext).importZip(uri)
            }
        }
    }
}
