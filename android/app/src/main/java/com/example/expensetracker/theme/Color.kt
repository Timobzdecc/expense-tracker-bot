package com.example.expensetracker.theme

import androidx.compose.ui.graphics.Color

// Dark theme - matching the Telegram bot's dark palette
val DarkBackground = Color(0xFF0F0F1E)
val DarkSurface = Color(0xFF1A1A2E)
val DarkCard = Color(0xFF16213E)
val DarkCardVariant = Color(0xFF1C2942)

// Primary accent - vibrant blue-purple gradient feel
val PrimaryBlue = Color(0xFF4A7DFF)
val PrimaryPurple = Color(0xFF7C4DFF)
val PrimaryLight = Color(0xFF82B1FF)

// Status colors
val SuccessGreen = Color(0xFF00E676)
val WarningOrange = Color(0xFFFF9100)
val ErrorRed = Color(0xFFFF5252)

// Text
val TextPrimary = Color(0xFFE8EAF0)
val TextSecondary = Color(0xFF9EA4B0)
val TextMuted = Color(0xFF6B7280)

// Category colors (12 distinct colors for expense categories)
val CategoryFood = Color(0xFFFF6B6B)
val CategoryTransport = Color(0xFF4ECDC4)
val CategoryHousing = Color(0xFF45B7D1)
val CategoryClothing = Color(0xFFFFA07A)
val CategoryHealth = Color(0xFF98D8C8)
val CategoryEntertainment = Color(0xFFF7DC6F)
val CategoryCommunication = Color(0xFFBB8FCE)
val CategoryEducation = Color(0xFF85C1E9)
val CategoryShopping = Color(0xFFE74C3C)
val CategoryFinance = Color(0xFF2ECC71)
val CategoryPets = Color(0xFFFF8A65)
val CategoryOther = Color(0xFF95A5A6)

// Chart colors
val ChartColors = listOf(
    CategoryFood, CategoryTransport, CategoryHousing, CategoryClothing,
    CategoryHealth, CategoryEntertainment, CategoryCommunication,
    CategoryEducation, CategoryShopping, CategoryFinance,
    CategoryPets, CategoryOther
)
