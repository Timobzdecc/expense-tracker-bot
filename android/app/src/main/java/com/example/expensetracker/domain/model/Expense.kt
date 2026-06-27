package com.example.expensetracker.domain.model

import java.util.Date

data class Expense(
    val id: Long = 0,
    val amount: Double,
    val description: String,
    val categorySlug: String,
    val createdAt: Date = Date(),
    val photoUrl: String? = null
) {
    val category: Category
        get() = Category.fromSlug(categorySlug)
}
