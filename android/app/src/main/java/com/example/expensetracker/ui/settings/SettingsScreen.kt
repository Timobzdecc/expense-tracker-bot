package com.example.expensetracker.ui.settings

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.platform.LocalContext
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.runtime.mutableStateOf
import kotlinx.coroutines.launch
import com.example.expensetracker.R
import com.example.expensetracker.UpdateManager

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(
    viewModel: SettingsViewModel,
    modifier: Modifier = Modifier
) {
    val uiState by viewModel.uiState.collectAsState()
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()
    val updateManager = remember { UpdateManager(context) }
    
    var showUpdateDialog by remember { mutableStateOf(false) }
    var updateInfo by remember { mutableStateOf<UpdateManager.UpdateInfo?>(null) }
    var isCheckingUpdate by remember { mutableStateOf(false) }

    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Text(
            text = stringResource(R.string.settings),
            style = MaterialTheme.typography.headlineMedium
        )

        OutlinedTextField(
            value = uiState.apiKey,
            onValueChange = { viewModel.updateApiKey(it) },
            label = { Text(stringResource(R.string.gemini_api_key)) },
            visualTransformation = PasswordVisualTransformation(),
            modifier = Modifier.fillMaxWidth(),
            singleLine = true
        )
        
        Text(
            text = "API ключ нужен для автокатегоризации, анализа чеков и чата.",
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )

        OutlinedTextField(
            value = uiState.modelName,
            onValueChange = { viewModel.updateModelName(it) },
            label = { Text(stringResource(R.string.gemini_model)) },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true
        )

        Button(
            onClick = { viewModel.saveSettings() },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text(stringResource(R.string.save))
        }

        if (uiState.isSaved) {
            Text(
                text = "Настройки сохранены!",
                color = MaterialTheme.colorScheme.primary,
                style = MaterialTheme.typography.bodyMedium
            )
        }
        
        Spacer(modifier = Modifier.weight(1f))
        
        OutlinedButton(
            onClick = {
                isCheckingUpdate = true
                coroutineScope.launch {
                    val info = updateManager.checkForUpdates()
                    if (info != null) {
                        updateInfo = info
                        showUpdateDialog = true
                    }
                    isCheckingUpdate = false
                }
            },
            modifier = Modifier.fillMaxWidth(),
            enabled = !isCheckingUpdate
        ) {
            Text(if (isCheckingUpdate) "Проверка..." else "Проверить обновления")
        }
    }

    if (showUpdateDialog && updateInfo != null) {
        AlertDialog(
            onDismissRequest = { showUpdateDialog = false },
            title = { Text("Доступно обновление") },
            text = { Text("Доступна версия ${updateInfo!!.newVersionCode}.\n\nЧто нового:\n${updateInfo!!.releaseNotes}") },
            confirmButton = {
                Button(onClick = {
                    showUpdateDialog = false
                    updateManager.downloadAndInstallUpdate(updateInfo!!.downloadUrl)
                }) {
                    Text("Скачать и установить")
                }
            },
            dismissButton = {
                TextButton(onClick = { showUpdateDialog = false }) {
                    Text("Позже")
                }
            }
        )
    }
}
