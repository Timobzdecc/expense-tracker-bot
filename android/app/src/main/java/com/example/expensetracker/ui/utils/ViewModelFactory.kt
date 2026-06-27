package com.example.expensetracker.ui.utils

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import com.example.expensetracker.ExpenseTrackerApp
import com.example.expensetracker.ui.addexpense.AddExpenseViewModel
import com.example.expensetracker.ui.budgets.BudgetsViewModel
import com.example.expensetracker.ui.chat.ChatViewModel
import com.example.expensetracker.ui.dashboard.DashboardViewModel
import com.example.expensetracker.ui.history.HistoryViewModel
import com.example.expensetracker.ui.settings.SettingsViewModel
import com.example.expensetracker.ui.statistics.StatisticsViewModel
import com.example.expensetracker.data.ai.GeminiService
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.runBlocking

class AppViewModelFactory : ViewModelProvider.Factory {
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        val app = ExpenseTrackerApp.instance
        val geminiService = GeminiService(app.settingsManager)
        
        return when {
            modelClass.isAssignableFrom(SettingsViewModel::class.java) -> {
                SettingsViewModel(app.settingsManager) as T
            }
            modelClass.isAssignableFrom(DashboardViewModel::class.java) -> {
                DashboardViewModel(app.expenseRepository) as T
            }
            modelClass.isAssignableFrom(AddExpenseViewModel::class.java) -> {
                AddExpenseViewModel(app.expenseRepository, geminiService) as T
            }
            modelClass.isAssignableFrom(ChatViewModel::class.java) -> {
                ChatViewModel(geminiService) as T
            }
            modelClass.isAssignableFrom(BudgetsViewModel::class.java) -> {
                BudgetsViewModel(app.budgetRepository, app.expenseRepository) as T
            }
            modelClass.isAssignableFrom(HistoryViewModel::class.java) -> {
                HistoryViewModel(app.expenseRepository) as T
            }
            modelClass.isAssignableFrom(StatisticsViewModel::class.java) -> {
                StatisticsViewModel(app.expenseRepository) as T
            }
            else -> throw IllegalArgumentException("Unknown ViewModel class: ${modelClass.name}")
        }
    }
}
