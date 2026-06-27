package com.example.expensetracker.data.repository

import com.example.expensetracker.data.local.dao.ChatDao
import com.example.expensetracker.data.local.entity.ChatMessageEntity
import com.example.expensetracker.domain.model.ChatMessage
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

class ChatRepository(private val chatDao: ChatDao) {

    fun getChatHistory(): Flow<List<ChatMessage>> {
        return chatDao.getAllMessages().map { entities ->
            entities.map { 
                ChatMessage(content = it.content, isUser = it.isUser)
            }
        }
    }

    suspend fun saveMessage(message: ChatMessage) {
        chatDao.insertMessage(
            ChatMessageEntity(
                content = message.content,
                isUser = message.isUser,
                timestamp = System.currentTimeMillis()
            )
        )
    }
    
    suspend fun clearHistory() {
        chatDao.clearHistory()
    }
}
