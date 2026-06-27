package com.example.expensetracker.ui.main

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.ime
import androidx.compose.foundation.layout.statusBars
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.fillMaxSize
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
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.material3.MaterialTheme
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

enum class AppRoute(val titleResId: Int, val iconEmoji: String, val navKey: NavKey) {
    DASHBOARD(R.string.nav_dashboard, "🏠", Main),
    STATISTICS(R.string.nav_statistics, "📊", StatisticsNav),
    HISTORY(R.string.nav_history, "⏳", HistoryNav),
    BUDGETS(R.string.nav_budgets, "💰", BudgetsNav),
    CHAT(R.string.ai_chat, "🤖", ChatNav),
    SETTINGS(R.string.nav_settings, "⚙️", SettingsNav)
}

@Composable
fun rememberIsKeyboardVisible(): Boolean {
    return WindowInsets.ime.getBottom(LocalDensity.current) > 0
}

@Composable
fun MainScreen(
    onItemClick: (NavKey) -> Unit,
    onAddExpenseClick: () -> Unit,
    factory: AppViewModelFactory,
    modifier: Modifier = Modifier
) {
    var selectedRoute by rememberSaveable { mutableStateOf(AppRoute.DASHBOARD) }
    val isKeyboardVisible = rememberIsKeyboardVisible()

    Scaffold(
        modifier = modifier,
        contentWindowInsets = WindowInsets.statusBars,
        bottomBar = {
            if (!isKeyboardVisible) {
                NavigationBar {
                    AppRoute.entries.forEach { route ->
                        NavigationBarItem(
                            selected = selectedRoute == route,
                            onClick = { selectedRoute = route },
                            icon = {
                                Text(
                                    text = route.iconEmoji,
                                    fontSize = 22.sp
                                )
                            },
                            label = {
                                Text(
                                    text = stringResource(route.titleResId),
                                    style = MaterialTheme.typography.labelSmall.copy(fontSize = 10.sp),
                                    maxLines = 1,
                                    softWrap = false
                                )
                            }
                        )
                    }
                }
            }
        }
    ) { paddingValues ->
        val topPadding = paddingValues.calculateTopPadding()
        val bottomPadding = if (isKeyboardVisible) 0.dp else paddingValues.calculateBottomPadding()
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(
                    top = topPadding,
                    bottom = bottomPadding
                )
                .imePadding()
        ) {
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
