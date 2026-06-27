package com.example.expensetracker.ui.chat

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.expensetracker.data.ai.GeminiService
import com.example.expensetracker.domain.model.ChatMessage
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
    private val geminiService: GeminiService
) : ViewModel() {

    private val _uiState = MutableStateFlow(ChatUiState())
    val uiState: StateFlow<ChatUiState> = _uiState.asStateFlow()

    init {
        // Add initial greeting message
        _uiState.value = ChatUiState(
            messages = listOf(ChatMessage("Привет! Я твой финансовый AI-ассистент. Чем могу помочь?", isUser = false))
        )
    }

    fun sendMessage(text: String) {
        if (text.isBlank()) return

        val userMessage = ChatMessage(text, isUser = true)
        val currentHistory = _uiState.value.messages
        
        _uiState.value = _uiState.value.copy(
            messages = currentHistory + userMessage,
            isTyping = true
        )

        viewModelScope.launch {
            try {
                // Pass history excluding the message we just added
                val responseText = geminiService.chat(text, currentHistory)
                
                val aiMessage = ChatMessage(responseText, isUser = false)
                _uiState.value = _uiState.value.copy(
                    messages = _uiState.value.messages + aiMessage,
                    isTyping = false
                )
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isTyping = false,
                    error = e.message ?: "Ошибка при получении ответа"
                )
            }
        }
    }
}
