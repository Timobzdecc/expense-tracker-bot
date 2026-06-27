package com.example.expensetracker.ui.history

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.example.expensetracker.R
import com.example.expensetracker.domain.model.Category
import com.example.expensetracker.domain.model.Expense
import com.example.expensetracker.ui.dashboard.ExpenseItem

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HistoryScreen(
    viewModel: HistoryViewModel,
    modifier: Modifier = Modifier
) {
    val uiState by viewModel.uiState.collectAsState()
    var expenseToEdit by remember { mutableStateOf<Expense?>(null) }
    var expenseToDelete by remember { mutableStateOf<Expense?>(null) }

    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text(
            text = stringResource(R.string.nav_history),
            style = MaterialTheme.typography.headlineMedium,
            modifier = Modifier.padding(bottom = 16.dp)
        )

        if (uiState.isLoading) {
            CircularProgressIndicator(modifier = Modifier.align(Alignment.CenterHorizontally))
        } else if (uiState.expenses.isEmpty()) {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                Text(stringResource(R.string.no_expenses), color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
        } else {
            LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                items(uiState.expenses, key = { it.id }) { expense ->
                    SwipeableExpenseItem(
                        expense = expense,
                        onDeleteClick = { expenseToDelete = expense },
                        onEditClick = { expenseToEdit = expense }
                    )
                }
            }
        }
    }

    if (expenseToDelete != null) {
        AlertDialog(
            onDismissRequest = { expenseToDelete = null },
            title = { Text("Удалить расход?") },
            text = { Text("Вы уверены, что хотите удалить расход '${expenseToDelete?.description}' на сумму ${expenseToDelete?.amount} ₽?") },
            confirmButton = {
                TextButton(onClick = {
                    viewModel.deleteExpense(expenseToDelete!!.id)
                    expenseToDelete = null
                }) {
                    Text(stringResource(R.string.delete), color = MaterialTheme.colorScheme.error)
                }
            },
            dismissButton = {
                TextButton(onClick = { expenseToDelete = null }) {
                    Text(stringResource(R.string.cancel))
                }
            }
        )
    }

    if (expenseToEdit != null) {
        ChangeCategoryDialog(
            expense = expenseToEdit!!,
            onDismiss = { expenseToEdit = null },
            onConfirm = { category ->
                viewModel.changeCategory(expenseToEdit!!.id, category.slug)
                expenseToEdit = null
            }
        )
    }
}

@Composable
fun SwipeableExpenseItem(
    expense: Expense,
    onDeleteClick: () -> Unit,
    onEditClick: () -> Unit
) {
    // Keeping it simple without actual swipe gesture for now, using a row with action buttons
    Column {
        ExpenseItem(expense)
        Row(
            modifier = Modifier.fillMaxWidth().padding(horizontal = 8.dp, vertical = 4.dp),
            horizontalArrangement = Arrangement.End
        ) {
            TextButton(onClick = onEditClick) {
                Icon(Icons.Default.Edit, contentDescription = null, modifier = Modifier.size(16.dp))
                Spacer(Modifier.width(4.dp))
                Text("Категория")
            }
            TextButton(onClick = onDeleteClick, colors = ButtonDefaults.textButtonColors(contentColor = MaterialTheme.colorScheme.error)) {
                Icon(Icons.Default.Delete, contentDescription = null, modifier = Modifier.size(16.dp))
                Spacer(Modifier.width(4.dp))
                Text("Удалить")
            }
        }
        Divider(color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.1f))
    }
}

@Composable
fun ChangeCategoryDialog(
    expense: Expense,
    onDismiss: () -> Unit,
    onConfirm: (Category) -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(stringResource(R.string.change_category)) },
        text = {
            LazyColumn {
                items(Category.entries.chunked(2)) { rowCategories ->
                    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceEvenly) {
                        for (category in rowCategories) {
                            Button(
                                onClick = { onConfirm(category) },
                                colors = ButtonDefaults.buttonColors(
                                    containerColor = if (expense.category == category) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.surfaceVariant,
                                    contentColor = if (expense.category == category) MaterialTheme.colorScheme.onPrimary else MaterialTheme.colorScheme.onSurfaceVariant
                                ),
                                modifier = Modifier.weight(1f).padding(4.dp)
                            ) {
                                Text("${category.emoji} ${category.label}")
                            }
                        }
                    }
                }
            }
        },
        confirmButton = {
            TextButton(onClick = onDismiss) {
                Text(stringResource(R.string.cancel))
            }
        }
    )
}
