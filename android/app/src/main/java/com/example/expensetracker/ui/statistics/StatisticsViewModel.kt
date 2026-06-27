package com.example.expensetracker.ui.statistics

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.expensetracker.data.repository.ExpenseRepository
import com.example.expensetracker.domain.model.Category
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.util.Calendar

data class CategoryStatItem(
    val category: Category,
    val amount: Double,
    val percentage: Float
)

data class StatisticsUiState(
    val stats: List<CategoryStatItem> = emptyList(),
    val totalAmount: Double = 0.0,
    val isLoading: Boolean = true
)

class StatisticsViewModel(
    private val expenseRepository: ExpenseRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(StatisticsUiState())
    val uiState: StateFlow<StatisticsUiState> = _uiState.asStateFlow()

    init {
        loadStatistics()
    }

    private fun loadStatistics() {
        viewModelScope.launch {
            val calendar = Calendar.getInstance()
            calendar.set(Calendar.DAY_OF_MONTH, 1)
            calendar.set(Calendar.HOUR_OF_DAY, 0)
            calendar.set(Calendar.MINUTE, 0)
            calendar.set(Calendar.SECOND, 0)
            val firstDayOfMonth = calendar.timeInMillis

            val categoryStats = expenseRepository.getCategoryStats(firstDayOfMonth)
            val total = expenseRepository.getTotalAmount(firstDayOfMonth)

            val statItems = categoryStats.map { stat ->
                val category = Category.entries.find { it.slug == stat.categorySlug } ?: Category.OTHER
                CategoryStatItem(
                    category = category,
                    amount = stat.amount,
                    percentage = if (total > 0) (stat.amount / total).toFloat() else 0f
                )
            }.sortedByDescending { it.amount }

            _uiState.value = StatisticsUiState(
                stats = statItems,
                totalAmount = total,
                isLoading = false
            )
        }
    }
}
