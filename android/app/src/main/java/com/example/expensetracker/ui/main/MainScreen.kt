package com.example.expensetracker.ui.main

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.isImeVisible
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AccountBalanceWallet
import androidx.compose.material.icons.filled.BarChart
import androidx.compose.material.icons.filled.Chat
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.List
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.res.stringResource
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation3.runtime.NavKey
import com.example.expensetracker.*
import com.example.expensetracker.R
import com.example.expensetracker.ui.budgets.BudgetsScreen
import com.example.expensetracker.ui.budgets.BudgetsViewModel
import com.example.expensetracker.ui.chat.ChatScreen
import com.example.expensetracker.ui.chat.ChatViewModel
import com.example.expensetracker.ui.dashboard.DashboardScreen
import com.example.expensetracker.ui.dashboard.DashboardViewModel
import com.example.expensetracker.ui.history.HistoryScreen
import com.example.expensetracker.ui.history.HistoryViewModel
import com.example.expensetracker.ui.settings.SettingsScreen
import com.example.expensetracker.ui.settings.SettingsViewModel
import com.example.expensetracker.ui.statistics.StatisticsScreen
import com.example.expensetracker.ui.statistics.StatisticsViewModel
import com.example.expensetracker.ui.utils.AppViewModelFactory

enum class AppRoute(val titleResId: Int, val icon: ImageVector, val navKey: NavKey) {
    DASHBOARD(R.string.nav_dashboard, Icons.Filled.Home, Main),
    STATISTICS(R.string.nav_statistics, Icons.Filled.BarChart, StatisticsNav),
    HISTORY(R.string.nav_history, Icons.Filled.List, HistoryNav),
    BUDGETS(R.string.nav_budgets, Icons.Filled.AccountBalanceWallet, BudgetsNav),
    CHAT(R.string.ai_chat, Icons.Filled.Chat, ChatNav),
    SETTINGS(R.string.nav_settings, Icons.Filled.Settings, SettingsNav)
}

@OptIn(ExperimentalLayoutApi::class)
@Composable
fun MainScreen(
    onItemClick: (NavKey) -> Unit,
    onAddExpenseClick: () -> Unit,
    factory: AppViewModelFactory,
    modifier: Modifier = Modifier
) {
    var selectedRoute by rememberSaveable { mutableStateOf(AppRoute.DASHBOARD) }

    Scaffold(
        modifier = modifier,
        bottomBar = {
            if (!WindowInsets.isImeVisible) {
                NavigationBar {
                    AppRoute.entries.forEach { route ->
                        NavigationBarItem(
                            selected = selectedRoute == route,
                            onClick = { selectedRoute = route },
                            icon = { Icon(route.icon, contentDescription = stringResource(route.titleResId)) },
                            label = { Text(stringResource(route.titleResId)) }
                        )
                    }
                }
            }
        }
    ) { paddingValues ->
        Box(modifier = Modifier.padding(paddingValues)) {
            when (selectedRoute) {
                AppRoute.DASHBOARD -> {
                    val viewModel: DashboardViewModel = viewModel(factory = factory)
                    DashboardScreen(viewModel = viewModel, onAddExpenseClick = onAddExpenseClick)
                }
                AppRoute.STATISTICS -> {
                    val viewModel: StatisticsViewModel = viewModel(factory = factory)
                    StatisticsScreen(viewModel = viewModel)
                }
                AppRoute.HISTORY -> {
                    val viewModel: HistoryViewModel = viewModel(factory = factory)
                    HistoryScreen(viewModel = viewModel)
                }
                AppRoute.BUDGETS -> {
                    val viewModel: BudgetsViewModel = viewModel(factory = factory)
                    BudgetsScreen(viewModel = viewModel)
                }
                AppRoute.CHAT -> {
                    val viewModel: ChatViewModel = viewModel(factory = factory)
                    ChatScreen(viewModel = viewModel)
                }
                AppRoute.SETTINGS -> {
                    val viewModel: SettingsViewModel = viewModel(factory = factory)
                    SettingsScreen(viewModel = viewModel)
                }
            }
        }
    }
}
