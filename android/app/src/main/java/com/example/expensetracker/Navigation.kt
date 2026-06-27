package com.example.expensetracker

import androidx.compose.foundation.layout.padding
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation3.runtime.entryProvider
import androidx.navigation3.runtime.rememberNavBackStack
import androidx.navigation3.ui.NavDisplay
import com.example.expensetracker.ui.addexpense.AddExpenseScreen
import com.example.expensetracker.ui.addexpense.AddExpenseViewModel
import com.example.expensetracker.ui.main.MainScreen
import com.example.expensetracker.ui.utils.AppViewModelFactory

@Composable
fun MainNavigation() {
    val backStack = rememberNavBackStack(Main)
    val factory = AppViewModelFactory()

    NavDisplay(
        backStack = backStack,
        onBack = { backStack.removeLastOrNull() },
        entryProvider = entryProvider {
            entry<Main> {
                MainScreen(
                    onItemClick = { navKey -> backStack.add(navKey) },
                    onAddExpenseClick = { backStack.add(AddExpenseNav) },
                    factory = factory,
                    modifier = Modifier
                )
            }
            
            entry<AddExpenseNav> {
                val viewModel: AddExpenseViewModel = viewModel(factory = factory)
                AddExpenseScreen(
                    viewModel = viewModel,
                    onBack = { backStack.removeLastOrNull() },
                    modifier = Modifier
                )
            }
        },
    )
}
