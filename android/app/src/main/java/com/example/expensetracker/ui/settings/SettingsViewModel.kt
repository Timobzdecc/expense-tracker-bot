package com.example.expensetracker.ui.settings

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.expensetracker.data.preferences.SettingsManager
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch

data class SettingsUiState(
    val apiKey: String = "",
    val modelName: String = "gemini-1.5-flash",
    val isSaved: Boolean = false
)

class SettingsViewModel(
    private val settingsManager: SettingsManager
) : ViewModel() {

    private val _uiState = MutableStateFlow(SettingsUiState())
    val uiState: StateFlow<SettingsUiState> = _uiState.asStateFlow()

    init {
        viewModelScope.launch {
            val apiKey = settingsManager.apiKeyFlow.first() ?: ""
            val modelName = settingsManager.modelFlow.first()
            _uiState.value = SettingsUiState(apiKey = apiKey, modelName = modelName)
        }
    }

    fun updateApiKey(apiKey: String) {
        _uiState.value = _uiState.value.copy(apiKey = apiKey, isSaved = false)
    }

    fun updateModelName(modelName: String) {
        _uiState.value = _uiState.value.copy(modelName = modelName, isSaved = false)
    }

    fun saveSettings() {
        viewModelScope.launch {
            settingsManager.saveApiKey(_uiState.value.apiKey)
            settingsManager.saveModel(_uiState.value.modelName)
            _uiState.value = _uiState.value.copy(isSaved = true)
        }
    }
}
