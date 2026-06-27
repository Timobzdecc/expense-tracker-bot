package com.example.expensetracker.data.ai

import android.graphics.Bitmap
import com.example.expensetracker.domain.model.Category
import com.example.expensetracker.domain.model.ChatMessage
import com.example.expensetracker.domain.model.ParsedExpense
import com.google.ai.client.generativeai.GenerativeModel
import com.google.ai.client.generativeai.type.BlockThreshold
import com.google.ai.client.generativeai.type.HarmCategory
import com.google.ai.client.generativeai.type.SafetySetting
import com.google.ai.client.generativeai.type.content
import com.google.ai.client.generativeai.type.generationConfig
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.json.JSONException

import com.example.expensetracker.data.preferences.SettingsManager
import kotlinx.coroutines.flow.first

class GeminiService(private val settingsManager: SettingsManager) {

    private val noHarmSettings = listOf(
        SafetySetting(HarmCategory.HARASSMENT, BlockThreshold.NONE),
        SafetySetting(HarmCategory.HATE_SPEECH, BlockThreshold.NONE),
        SafetySetting(HarmCategory.SEXUALLY_EXPLICIT, BlockThreshold.NONE),
        SafetySetting(HarmCategory.DANGEROUS_CONTENT, BlockThreshold.NONE)
    )

    suspend fun categorizeExpense(description: String): String = withContext(Dispatchers.IO) {
        val apiKey = settingsManager.apiKeyFlow.first() ?: ""
        val modelName = settingsManager.modelFlow.first() ?: "gemini-1.5-flash"
        if (apiKey.isBlank()) return@withContext "other"

        try {
            val model = GenerativeModel(
                modelName = modelName,
                apiKey = apiKey,
                generationConfig = generationConfig {
                    temperature = 0.0f
                    maxOutputTokens = 20
                },
                safetySettings = noHarmSettings,
                systemInstruction = content { text("Определи категорию расхода. Возможные категории (Название -> slug): ${Category.entries.joinToString(", ") { "${it.label} -> ${it.slug}" }}. Ответь СТРОГО ОДНИМ СЛОВОМ — slug категории на английском языке (например: food, entertainment). Никаких знаков препинания, переводов или объяснений. Если не можешь определить, ответь other.") }
            )

            val response = model.generateContent(description)
            val result = response.text?.trim()?.trimEnd('.', ',', '!')?.lowercase() ?: "other"
            
            // Validate that the returned slug actually exists
            if (Category.entries.any { it.slug == result }) result else "other"
        } catch (e: Exception) {
            "other"
        }
    }

    suspend fun analyzeReceipt(bitmap: Bitmap): List<ParsedExpense> = withContext(Dispatchers.IO) {
        val apiKey = settingsManager.apiKeyFlow.first() ?: ""
        val modelName = settingsManager.modelFlow.first() ?: "gemini-1.5-flash"
        if (apiKey.isBlank()) return@withContext emptyList()

        try {
            val model = GenerativeModel(
                modelName = modelName,
                apiKey = apiKey,
                generationConfig = generationConfig {
                    temperature = 0.1f
                    maxOutputTokens = 1024
                    responseMimeType = "application/json"
                },
                safetySettings = noHarmSettings,
                systemInstruction = content { 
                    text("Проанализируй этот чек или скриншот перевода. Извлеки все траты как JSON массив. Формат: [{\"amount\": 100.5, \"description\": \"название\", \"categorySlug\": \"slug\"}]. Допустимые категории: ${Category.entries.joinToString(", ") { it.slug }}.") 
                }
            )

            val input = content { image(bitmap) }
            val response = model.generateContent(input)
            val jsonText = response.text?.trim() ?: "[]"
            
            // Basic JSON parsing
            parseJsonArray(jsonText)
        } catch (e: Exception) {
            e.printStackTrace()
            emptyList()
        }
    }

    private fun parseJsonArray(jsonString: String): List<ParsedExpense> {
        val result = mutableListOf<ParsedExpense>()
        try {
            // Strip markdown formatting if any
            val cleanJson = jsonString.replace("```json", "").replace("```", "").trim()
            val array = JSONArray(cleanJson)
            for (i in 0 until array.length()) {
                val item = array.getJSONObject(i)
                result.add(
                    ParsedExpense(
                        amount = item.optDouble("amount", 0.0),
                        description = item.optString("description", "Без описания"),
                        categorySlug = item.optString("categorySlug", "other")
                    )
                )
            }
        } catch (e: JSONException) {
            e.printStackTrace()
        }
        return result
    }

    suspend fun chat(message: String, history: List<ChatMessage>): String = withContext(Dispatchers.IO) {
        val apiKey = settingsManager.apiKeyFlow.first() ?: ""
        val modelName = settingsManager.modelFlow.first() ?: "gemini-1.5-flash"
        if (apiKey.isBlank()) return@withContext "API ключ не настроен. Пожалуйста, добавьте его в настройках."

        try {
            val model = GenerativeModel(
                modelName = modelName,
                apiKey = apiKey,
                generationConfig = generationConfig {
                    temperature = 0.7f
                    maxOutputTokens = 2048
                },
                safetySettings = noHarmSettings,
                systemInstruction = content { text("Ты дружелюбный финансовый AI-ассистент в приложении для учёта расходов. Отвечай на русском языке кратко и по делу. КАТЕГОРИЧЕСКИ ЗАПРЕЩАЕТСЯ писать свои внутренние рассуждения, логику, мета-промпты или мысли (например, не пиши 'User said...' или 'Constraint: ...'). Выдавай ТОЛЬКО финальный человечный ответ пользователю.") }
            )

            val chatHistory = history.map {
                content(role = if (it.isUser) "user" else "model") { text(it.content) }
            }
            
            val chat = model.startChat(chatHistory)
            val response = chat.sendMessage(message)
            response.text ?: "Не удалось получить ответ"
        } catch (e: Exception) {
            e.printStackTrace()
            "Ошибка связи с сервером AI. Проверьте интернет или API ключ."
        }
    }
}
