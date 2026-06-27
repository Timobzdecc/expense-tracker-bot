package com.example.expensetracker

import android.app.DownloadManager
import android.content.Context
import android.net.Uri
import android.os.Environment
import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

class UpdateManager(private val context: Context) {
    
    data class UpdateInfo(
        val isUpdateAvailable: Boolean,
        val newVersionCode: Int,
        val downloadUrl: String,
        val releaseNotes: String
    )

    suspend fun checkForUpdates(): UpdateInfo? = withContext(Dispatchers.IO) {
        try {
            val url = URL("https://api.github.com/repos/Timobzdecc/expense-tracker-bot/releases/latest")
            val connection = url.openConnection() as HttpURLConnection
            connection.requestMethod = "GET"
            connection.setRequestProperty("Accept", "application/vnd.github.v3+json")
            
            if (connection.responseCode == HttpURLConnection.HTTP_OK) {
                val response = connection.inputStream.bufferedReader().use { it.readText() }
                val json = JSONObject(response)
                
                val tagName = json.getString("tag_name")
                val newVersionCode = tagName.substringAfterLast("v").toIntOrNull() ?: 0
                val body = json.optString("body", "Доступна новая версия приложения.")
                
                val assets = json.getJSONArray("assets")
                var downloadUrl = ""
                for (i in 0 until assets.length()) {
                    val asset = assets.getJSONObject(i)
                    if (asset.getString("name").endsWith(".apk")) {
                        downloadUrl = asset.getString("browser_download_url")
                        break
                    }
                }
                
                if (newVersionCode > BuildConfig.VERSION_CODE && downloadUrl.isNotEmpty()) {
                    return@withContext UpdateInfo(true, newVersionCode, downloadUrl, body)
                }
            }
        } catch (e: Exception) {
            Log.e("UpdateManager", "Error checking for updates", e)
        }
        return@withContext null
    }

    fun downloadAndInstallUpdate(url: String, fileName: String = "app-update.apk") {
        try {
            val oldFile = java.io.File(context.getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS), fileName)
            if (oldFile.exists()) {
                oldFile.delete()
            }
            
            val request = DownloadManager.Request(Uri.parse(url))
                .setTitle("Обновление Expense Tracker")
                .setDescription("Идет скачивание новой версии...")
                .setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
                .setDestinationInExternalFilesDir(context, Environment.DIRECTORY_DOWNLOADS, fileName)
                .setAllowedOverMetered(true)
                .setAllowedOverRoaming(true)

            val downloadManager = context.getSystemService(Context.DOWNLOAD_SERVICE) as DownloadManager
            downloadManager.enqueue(request)
        } catch (e: Exception) {
            Log.e("UpdateManager", "Error enqueueing download", e)
        }
    }
}
