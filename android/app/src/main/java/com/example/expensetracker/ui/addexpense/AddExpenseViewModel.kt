package com.example.expensetracker.ui.addexpense

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.expensetracker.data.ai.GeminiService
import com.example.expensetracker.data.parser.ExpenseParser
import com.example.expensetracker.data.repository.ExpenseRepository
import com.example.expensetracker.domain.model.Expense
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

data class AddExpenseUiState(
    val isProcessing: Boolean = false,
    val error: String? = null,
    val success: Boolean = false
)

class AddExpenseViewModel(
    private val expenseRepository: ExpenseRepository,
    private val geminiService: GeminiService
) : ViewModel() {

    private val _uiState = MutableStateFlow(AddExpenseUiState())
    val uiState: StateFlow<AddExpenseUiState> = _uiState.asStateFlow()

    fun processTextInput(text: String) {
        if (text.isBlank()) return

        viewModelScope.launch {
            _uiState.value = AddExpenseUiState(isProcessing = true)

            try {
                // 1. Parse text using our Regex parser (same as Python bot)
                val parsed = ExpenseParser.parse(text)
                if (parsed == null) {
                    _uiState.value = AddExpenseUiState(
                        isProcessing = false, 
                        error = "Не удалось распознать сумму. Формат: 'описание сумма' или 'сумма описание'"
                    )
                    return@launch
                }

                val (amount, description) = parsed

                // 2. Use Gemini AI to categorize the expense based on description
                val categorySlug = geminiService.categorizeExpense(description)

                // 3. Save to database
                val expense = Expense(
                    amount = amount,
                    description = description,
                    categorySlug = categorySlug
                )
                
                val id = expenseRepository.addExpense(expense)
                
                // Fetch image in background
                viewModelScope.launch {
                    val photoUrl = com.example.expensetracker.data.remote.ImageFetcher.fetchImageFor(description)
                    if (photoUrl != null) {
                        expenseRepository.updateExpensePhoto(id, photoUrl)
                    }
                }
                
                _uiState.value = AddExpenseUiState(isProcessing = false, success = true)

            } catch (e: Exception) {
                _uiState.value = AddExpenseUiState(
                    isProcessing = false, 
                    error = e.message ?: "Произошла ошибка при добавлении расхода"
                )
            }
        }
    }

    fun processReceiptImage(bitmap: android.graphics.Bitmap) {
        viewModelScope.launch {
            _uiState.value = AddExpenseUiState(isProcessing = true)

            try {
                // Parse image with Gemini
                val expenses = geminiService.analyzeReceipt(bitmap)
                
                if (expenses.isEmpty()) {
                    _uiState.value = AddExpenseUiState(
                        isProcessing = false, 
                        error = "Не удалось распознать траты на чеке."
                    )
                    return@launch
                }

                // Save all parsed expenses
                expenses.forEach { parsed ->
                    val expense = Expense(
                        amount = parsed.amount,
                        description = parsed.description,
                        categorySlug = parsed.categorySlug
                    )
                    val id = expenseRepository.addExpense(expense)
                    // Fetch image in background
                    viewModelScope.launch {
                        val photoUrl = com.example.expensetracker.data.remote.ImageFetcher.fetchImageFor(parsed.description)
                        if (photoUrl != null) {
                            expenseRepository.updateExpensePhoto(id, photoUrl)
                        }
                    }
                }
                
                _uiState.value = AddExpenseUiState(isProcessing = false, success = true)

            } catch (e: Exception) {
                _uiState.value = AddExpenseUiState(
                    isProcessing = false, 
                    error = e.message ?: "Произошла ошибка при анализе чека"
                )
            }
        }
    }

    fun resetState() {
        _uiState.value = AddExpenseUiState()
    }
}
