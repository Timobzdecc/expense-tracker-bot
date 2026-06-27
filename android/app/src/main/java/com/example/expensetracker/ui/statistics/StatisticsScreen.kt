package com.example.expensetracker.ui.statistics

import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.example.expensetracker.R

@Composable
fun StatisticsScreen(
    viewModel: StatisticsViewModel,
    modifier: Modifier = Modifier
) {
    val uiState by viewModel.uiState.collectAsState()

    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text(
            text = stringResource(R.string.nav_statistics),
            style = MaterialTheme.typography.headlineMedium,
            modifier = Modifier.padding(bottom = 16.dp)
        )

        if (uiState.isLoading) {
            CircularProgressIndicator(modifier = Modifier.align(Alignment.CenterHorizontally))
        } else if (uiState.stats.isEmpty()) {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                Text(stringResource(R.string.no_expenses), color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
        } else {
            // Total amount card
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 24.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer)
            ) {
                Column(
                    modifier = Modifier.padding(24.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        text = "Всего за месяц",
                        color = MaterialTheme.colorScheme.onPrimaryContainer,
                        style = MaterialTheme.typography.titleMedium
                    )
                    Text(
                        text = "${String.format("%.0f", uiState.totalAmount)} ₽",
                        color = MaterialTheme.colorScheme.onPrimaryContainer,
                        style = MaterialTheme.typography.headlineLarge,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(top = 8.dp)
                    )
                }
            }

            Text(
                text = "Траты по категориям",
                style = MaterialTheme.typography.titleLarge,
                modifier = Modifier.padding(bottom = 16.dp)
            )

            LazyColumn(verticalArrangement = Arrangement.spacedBy(16.dp)) {
                items(uiState.stats) { stat ->
                    CategoryStatRow(stat)
                }
            }
        }
    }
}

@Composable
fun CategoryStatRow(stat: CategoryStatItem) {
    var animationPlayed by remember { mutableStateOf(false) }
    LaunchedEffect(Unit) { animationPlayed = true }
    
    val animatedPercentage by animateFloatAsState(
        targetValue = if (animationPlayed) stat.percentage else 0f,
        animationSpec = tween(durationMillis = 1000),
        label = "progress_animation"
    )

    Column(modifier = Modifier.fillMaxWidth()) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(text = stat.category.emoji, style = MaterialTheme.typography.titleMedium)
                Spacer(modifier = Modifier.width(8.dp))
                Text(text = stat.category.label, style = MaterialTheme.typography.bodyLarge)
            }
            Text(
                text = "${String.format("%.0f", stat.amount)} ₽",
                style = MaterialTheme.typography.bodyLarge,
                fontWeight = FontWeight.Medium
            )
        }
        
        Spacer(modifier = Modifier.height(8.dp))
        
        // Custom progress bar to use category specific color
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(12.dp)
                .clip(RoundedCornerShape(6.dp))
                .background(MaterialTheme.colorScheme.surfaceVariant)
        ) {
            Box(
                modifier = Modifier
                    .fillMaxWidth(animatedPercentage.coerceIn(0f, 1f))
                    .height(12.dp)
                    .clip(RoundedCornerShape(6.dp))
                    .background(stat.category.color)
            )
        }
        
        Text(
            text = "${String.format("%.1f", stat.percentage * 100)}%",
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier
                .align(Alignment.End)
                .padding(top = 4.dp)
        )
    }
}
