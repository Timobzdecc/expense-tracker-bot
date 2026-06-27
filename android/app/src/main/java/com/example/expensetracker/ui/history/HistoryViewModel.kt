package com.example.expensetracker.ui.history

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.expensetracker.data.repository.ExpenseRepository
import com.example.expensetracker.domain.model.Expense
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.launch

data class HistoryUiState(
    val expenses: List<Expense> = emptyList(),
    val isLoading: Boolean = true
)

class HistoryViewModel(
    private val expenseRepository: ExpenseRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(HistoryUiState())
    val uiState: StateFlow<HistoryUiState> = _uiState.asStateFlow()

    init {
        loadExpenses()
    }

    private fun loadExpenses() {
        viewModelScope.launch {
            expenseRepository.getAllExpenses().collectLatest { expenses ->
                _uiState.value = HistoryUiState(
                    expenses = expenses,
                    isLoading = false
                )
            }
        }
    }

    fun deleteExpense(id: Long) {
        viewModelScope.launch {
            expenseRepository.deleteExpense(id)
        }
    }

    fun changeCategory(id: Long, categorySlug: String) {
        viewModelScope.launch {
            expenseRepository.updateExpenseCategory(id, categorySlug)
        }
    }
}
