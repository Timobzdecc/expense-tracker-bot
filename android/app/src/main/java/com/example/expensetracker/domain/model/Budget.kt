package com.example.expensetracker.domain.model

data class Budget(
    val id: Long = 0,
    val categorySlug: String,
    val monthlyLimit: Double
) {
    val category: Category
        get() = Category.fromSlug(categorySlug)
}
