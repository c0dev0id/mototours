package com.mototour.app.data

import android.content.Context
import android.content.Intent
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import androidx.core.content.FileProvider
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.io.File
import java.net.HttpURLConnection
import java.net.URL

data class UpdateInfo(
    val apkName: String,
    val downloadUrl: String,
    val commitSha: String,
    val body: String
)

object UpdateChecker {

    private const val GITHUB_OWNER = "c0dev0id"
    private const val GITHUB_REPO = "mototours"
    private const val RELEASE_TAG = "dev"
    private const val API_URL =
        "https://api.github.com/repos/$GITHUB_OWNER/$GITHUB_REPO/releases/tags/$RELEASE_TAG"

    fun isOnline(context: Context): Boolean {
        val cm = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        val network = cm.activeNetwork ?: return false
        val caps = cm.getNetworkCapabilities(network) ?: return false
        return caps.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET) &&
                caps.hasCapability(NetworkCapabilities.NET_CAPABILITY_VALIDATED)
    }

    suspend fun checkForUpdate(currentSha: String): UpdateInfo? = withContext(Dispatchers.IO) {
        try {
            val conn = URL(API_URL).openConnection() as HttpURLConnection
            conn.connectTimeout = 10_000
            conn.readTimeout = 10_000
            conn.setRequestProperty("Accept", "application/vnd.github+json")
            conn.setRequestProperty("User-Agent", "MotoTourApp/1.0")

            try {
                if (conn.responseCode != 200) return@withContext null
                val json = JSONObject(conn.inputStream.bufferedReader().readText())
                if (!json.optBoolean("prerelease", false)) return@withContext null

                val assets = json.getJSONArray("assets")
                if (assets.length() == 0) return@withContext null

                val asset = assets.getJSONObject(0)
                val apkName = asset.getString("name")
                val downloadUrl = asset.getString("browser_download_url")

                // Extract SHA from filename: MotoTour-dev-<sha>.apk
                val sha = apkName.removeSuffix(".apk").substringAfterLast("-")
                if (sha.equals(currentSha, ignoreCase = true)) return@withContext null

                UpdateInfo(
                    apkName = apkName,
                    downloadUrl = downloadUrl,
                    commitSha = sha,
                    body = json.optString("body", "")
                )
            } finally {
                conn.disconnect()
            }
        } catch (_: Exception) {
            null
        }
    }

    suspend fun downloadApk(context: Context, update: UpdateInfo): File? =
        withContext(Dispatchers.IO) {
            try {
                val conn = URL(update.downloadUrl).openConnection() as HttpURLConnection
                conn.connectTimeout = 15_000
                conn.readTimeout = 60_000
                conn.setRequestProperty("User-Agent", "MotoTourApp/1.0")
                conn.instanceFollowRedirects = true

                try {
                    if (conn.responseCode != 200) return@withContext null
                    val file = File(context.cacheDir, update.apkName)
                    conn.inputStream.use { input ->
                        file.outputStream().use { output ->
                            input.copyTo(output)
                        }
                    }
                    file
                } finally {
                    conn.disconnect()
                }
            } catch (_: Exception) {
                null
            }
        }

    fun installApk(context: Context, apkFile: File) {
        val uri = FileProvider.getUriForFile(
            context,
            "${context.packageName}.fileprovider",
            apkFile
        )
        val intent = Intent(Intent.ACTION_VIEW).apply {
            setDataAndType(uri, "application/vnd.android.package-archive")
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        }
        context.startActivity(intent)
    }
}
