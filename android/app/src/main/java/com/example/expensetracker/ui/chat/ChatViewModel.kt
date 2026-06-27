package com.example.expensetracker.ui.chat

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.expensetracker.data.ai.GeminiService
import com.example.expensetracker.domain.model.ChatMessage
import com.example.expensetracker.data.repository.ChatRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

data class ChatUiState(
    val messages: List<ChatMessage> = emptyList(),
    val isTyping: Boolean = false,
    val error: String? = null
)

class ChatViewModel(
    private val geminiService: GeminiService,
    private val chatRepository: ChatRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(ChatUiState())
    val uiState: StateFlow<ChatUiState> = _uiState.asStateFlow()

    init {
        viewModelScope.launch {
            chatRepository.getChatHistory().collect { history ->
                if (history.isEmpty()) {
                    val greeting = ChatMessage("Привет! Я твой финансовый AI-ассистент. Чем могу помочь?", isUser = false)
                    chatRepository.saveMessage(greeting)
                } else {
                    // Clean up history dynamically so bad formatting is stripped out retroactively!
                    val cleanedHistory = history.map { msg ->
                        if (msg.isUser) {
                            msg
                        } else {
                            var clean = msg.content.trim()
                            if (clean.contains("</think>")) {
                                clean = clean.substringAfter("</think>").trim()
                            }
                            if (clean.startsWith("*") || clean.contains("\n* ")) {
                                val lines = clean.split("\n")
                                val cleanLines = lines.dropWhile { it.trim().startsWith("*") || it.trim().startsWith("-") || it.isBlank() }
                                if (cleanLines.isNotEmpty()) {
                                    clean = cleanLines.joinToString("\n").trim()
                                }
                            }
                            msg.copy(content = clean)
                        }
                    }
                    _uiState.value = _uiState.value.copy(messages = cleanedHistory)
                }
            }
        }
    }

    fun sendMessage(text: String) {
        if (text.isBlank()) return

        val userMessage = ChatMessage(text, isUser = true)
        
        viewModelScope.launch {
            chatRepository.saveMessage(userMessage)
            _uiState.value = _uiState.value.copy(isTyping = true)
            
            try {
                val currentHistory = _uiState.value.messages
                val responseText = geminiService.chat(text, currentHistory)
                
                val aiMessage = ChatMessage(responseText, isUser = false)
                chatRepository.saveMessage(aiMessage)
                _uiState.value = _uiState.value.copy(isTyping = false)
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isTyping = false,
                    error = e.message ?: "Ошибка при получении ответа"
                )
            }
        }
    }
}
