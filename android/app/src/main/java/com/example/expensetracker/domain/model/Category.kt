package com.example.expensetracker.domain.model

import androidx.compose.ui.graphics.Color
import com.example.expensetracker.theme.*

enum class Category(val slug: String, val label: String, val emoji: String, val color: Color) {
    FOOD("food", "Еда", "🍔", CategoryFood),
    TRANSPORT("transport", "Транспорт", "⛽", CategoryTransport),
    HOUSING("housing", "Жильё", "🏠", CategoryHousing),
    CLOTHING("clothing", "Одежда", "👕", CategoryClothing),
    HEALTH("health", "Здоровье", "💊", CategoryHealth),
    ENTERTAINMENT("entertainment", "Развлечения", "🎭", CategoryEntertainment),
    COMMUNICATION("communication", "Связь", "📱", CategoryCommunication),
    EDUCATION("education", "Образование", "🎓", CategoryEducation),
    SHOPPING("shopping", "Покупки", "🛒", CategoryShopping),
    FINANCE("finance", "Финансы", "💰", CategoryFinance),
    PETS("pets", "Питомцы", "🐾", CategoryPets),
    OTHER("other", "Прочее", "🔧", CategoryOther);

    companion object {
        fun fromSlug(slug: String): Category {
            return entries.find { it.slug == slug } ?: OTHER
        }
    }
}
