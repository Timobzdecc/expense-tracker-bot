package com.example.expensetracker.ui.budgets

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.expensetracker.data.repository.BudgetRepository
import com.example.expensetracker.data.repository.ExpenseRepository
import com.example.expensetracker.domain.model.Budget
import com.example.expensetracker.domain.model.Category
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.launch
import java.util.Calendar

data class BudgetProgress(
    val category: Category,
    val limit: Double,
    val spent: Double
) {
    val percentage: Float get() = if (limit > 0) (spent / limit).toFloat() else 0f
    val isExceeded: Boolean get() = spent >= limit
    val isWarning: Boolean get() = spent >= limit * 0.8 && spent < limit
}

data class BudgetsUiState(
    val budgets: List<BudgetProgress> = emptyList(),
    val isLoading: Boolean = true
)

class BudgetsViewModel(
    private val budgetRepository: BudgetRepository,
    private val expenseRepository: ExpenseRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(BudgetsUiState())
    val uiState: StateFlow<BudgetsUiState> = _uiState.asStateFlow()

    init {
        loadBudgets()
    }

    private fun loadBudgets() {
        viewModelScope.launch {
            val calendar = Calendar.getInstance()
            calendar.set(Calendar.DAY_OF_MONTH, 1)
            calendar.set(Calendar.HOUR_OF_DAY, 0)
            calendar.set(Calendar.MINUTE, 0)
            calendar.set(Calendar.SECOND, 0)
            val firstDayOfMonth = calendar.timeInMillis

            budgetRepository.getAllBudgets().collectLatest { savedBudgets ->
                val progressList = savedBudgets.map { budget ->
                    val spent = expenseRepository.getMonthlySpentByCategory(budget.categorySlug, firstDayOfMonth)
                    BudgetProgress(
                        category = budget.category,
                        limit = budget.monthlyLimit,
                        spent = spent
                    )
                }
                
                _uiState.value = BudgetsUiState(
                    budgets = progressList,
                    isLoading = false
                )
            }
        }
    }

    fun setBudget(category: Category, limit: Double) {
        viewModelScope.launch {
            budgetRepository.setBudget(Budget(categorySlug = category.slug, monthlyLimit = limit))
        }
    }
}
