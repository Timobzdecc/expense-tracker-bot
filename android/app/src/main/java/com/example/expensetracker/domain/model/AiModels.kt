package com.example.expensetracker.domain.model

data class ParsedExpense(
    val amount: Double,
    val description: String,
    val categorySlug: String
)

data class ChatMessage(
    val content: String,
    val isUser: Boolean
)
