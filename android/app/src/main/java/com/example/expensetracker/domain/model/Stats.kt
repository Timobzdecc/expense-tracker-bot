package com.example.expensetracker.domain.model

data class PeriodStats(
    val totalAmount: Double,
    val count: Int,
    val averageAmount: Double,
    val categoryBreakdown: List<CategoryStat>
)

data class CategoryStat(
    val categorySlug: String,
    val amount: Double,
    val count: Int
) {
    val category: Category
        get() = Category.fromSlug(categorySlug)
}

data class DailyBreakdown(
    val date: String, // Format: MM-dd or dd.MM
    val total: Double
)
