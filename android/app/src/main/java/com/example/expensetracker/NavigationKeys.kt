package com.example.expensetracker

import androidx.navigation3.runtime.NavKey
import kotlinx.serialization.Serializable

@Serializable data object Main : NavKey
@Serializable data object StatisticsNav : NavKey
@Serializable data object HistoryNav : NavKey
@Serializable data object BudgetsNav : NavKey
@Serializable data object ChatNav : NavKey
@Serializable data object SettingsNav : NavKey
@Serializable data object AddExpenseNav : NavKey
