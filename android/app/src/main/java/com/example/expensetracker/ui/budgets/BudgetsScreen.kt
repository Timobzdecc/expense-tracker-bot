package com.example.expensetracker.ui.budgets

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import com.example.expensetracker.R
import com.example.expensetracker.domain.model.Category

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun BudgetsScreen(
    viewModel: BudgetsViewModel,
    modifier: Modifier = Modifier
) {
    val uiState by viewModel.uiState.collectAsState()
    var showAddDialog by remember { mutableStateOf(false) }

    Scaffold(
        floatingActionButton = {
            FloatingActionButton(onClick = { showAddDialog = true }) {
                Icon(Icons.Default.Add, contentDescription = stringResource(R.string.set_budget))
            }
        },
        modifier = modifier
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(16.dp)
        ) {
            Text(
                text = stringResource(R.string.nav_budgets),
                style = MaterialTheme.typography.headlineMedium,
                modifier = Modifier.padding(bottom = 16.dp)
            )

            if (uiState.isLoading) {
                CircularProgressIndicator(modifier = Modifier.align(Alignment.CenterHorizontally))
            } else if (uiState.budgets.isEmpty()) {
                Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    Text("У вас пока нет настроенных бюджетов.", color = MaterialTheme.colorScheme.onSurfaceVariant)
                }
            } else {
                LazyColumn(verticalArrangement = Arrangement.spacedBy(16.dp)) {
                    items(uiState.budgets) { budget ->
                        BudgetCard(budget)
                    }
                }
            }
        }
    }

    if (showAddDialog) {
        AddBudgetDialog(
            onDismiss = { showAddDialog = false },
            onConfirm = { category, limit ->
                viewModel.setBudget(category, limit)
                showAddDialog = false
            }
        )
    }
}

@Composable
fun BudgetCard(progress: BudgetProgress) {
    val progressColor = when {
        progress.isExceeded -> MaterialTheme.colorScheme.error
        progress.isWarning -> com.example.expensetracker.theme.WarningOrange
        else -> com.example.expensetracker.theme.SuccessGreen
    }

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(text = progress.category.emoji, style = MaterialTheme.typography.titleLarge)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(text = progress.category.label, style = MaterialTheme.typography.titleMedium)
                }
                Text(
                    text = "${String.format("%.0f", progress.spent)} / ${String.format("%.0f", progress.limit)} ₽",
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.Bold
                )
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            
            LinearProgressIndicator(
                progress = { progress.percentage.coerceIn(0f, 1f) },
                modifier = Modifier.fillMaxWidth().height(8.dp),
                color = progressColor,
                trackColor = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.1f)
            )
            
            if (progress.isExceeded) {
                Text(
                    text = stringResource(R.string.budget_exceeded),
                    color = MaterialTheme.colorScheme.error,
                    style = MaterialTheme.typography.bodySmall,
                    modifier = Modifier.padding(top = 8.dp)
                )
            } else if (progress.isWarning) {
                Text(
                    text = stringResource(R.string.budget_warning),
                    color = com.example.expensetracker.theme.WarningOrange,
                    style = MaterialTheme.typography.bodySmall,
                    modifier = Modifier.padding(top = 8.dp)
                )
            }
        }
    }
}

@Composable
fun AddBudgetDialog(onDismiss: () -> Unit, onConfirm: (Category, Double) -> Unit) {
    var expanded by remember { mutableStateOf(false) }
    var selectedCategory by remember { mutableStateOf(Category.FOOD) }
    var limitStr by remember { mutableStateOf("") }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(stringResource(R.string.set_budget)) },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
                // Category Dropdown
                Box {
                    Button(onClick = { expanded = true }, modifier = Modifier.fillMaxWidth()) {
                        Text("${selectedCategory.emoji} ${selectedCategory.label}")
                    }
                    DropdownMenu(expanded = expanded, onDismissRequest = { expanded = false }) {
                        Category.entries.forEach { category ->
                            DropdownMenuItem(
                                text = { Text("${category.emoji} ${category.label}") },
                                onClick = {
                                    selectedCategory = category
                                    expanded = false
                                }
                            )
                        }
                    }
                }
                
                OutlinedTextField(
                    value = limitStr,
                    onValueChange = { limitStr = it },
                    label = { Text(stringResource(R.string.monthly_limit)) },
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                    modifier = Modifier.fillMaxWidth()
                )
            }
        },
        confirmButton = {
            TextButton(onClick = {
                val limit = limitStr.toDoubleOrNull()
                if (limit != null && limit > 0) {
                    onConfirm(selectedCategory, limit)
                }
            }) {
                Text(stringResource(R.string.save))
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text(stringResource(R.string.cancel))
            }
        }
    )
}
