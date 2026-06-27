package com.example.expensetracker.data.remote

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.jsoup.Jsoup
import android.util.Log
import java.net.URLEncoder

object ImageFetcher {
    private const val TAG = "ImageFetcher"

    suspend fun fetchImageFor(query: String): String? = withContext(Dispatchers.IO) {
        try {
            // Поиск в Bing Images (он выдает хорошие результаты без сложного JS)
            val url = "https://www.bing.com/images/search?q=${URLEncoder.encode(query, "UTF-8")}"
            val document = Jsoup.connect(url)
                .userAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
                .timeout(5000)
                .get()

            // Ищем все картинки с классом mimg (стандартный класс картинок в Bing)
            val imageElements = document.select("img.mimg")

            for (img in imageElements) {
                // Bing часто прячет оригинальную ссылку в дата-атрибуты или JSON 'm'
                val mUrl = img.attr("m")
                if (mUrl.isNotEmpty()) {
                    val murlRegex = "\"murl\":\"(.*?)\"".toRegex()
                    val match = murlRegex.find(mUrl)
                    if (match != null) {
                        return@withContext match.groupValues[1]
                    }
                }

                // Или ссылка может быть в data-src (ленивая загрузка) или src
                val dataSrc = img.attr("data-src")
                if (dataSrc.startsWith("http")) {
                    return@withContext dataSrc
                }

                val src = img.attr("src")
                if (src.startsWith("http")) {
                    return@withContext src
                }
            }
            null
        } catch (e: Exception) {
            Log.e(TAG, "Error fetching image for $query", e)
            null
        }
    }
}
