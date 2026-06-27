package com.example.expensetracker.data.local.entity

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey
import com.example.expensetracker.domain.model.Budget

@Entity(
    tableName = "budgets",
    indices = [Index(value = ["categorySlug"], unique = true)]
)
data class BudgetEntity(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val categorySlug: String,
    val monthlyLimit: Double
) {
    fun toDomainModel(): Budget {
        return Budget(
            id = id,
            categorySlug = categorySlug,
            monthlyLimit = monthlyLimit
        )
    }

    companion object {
        fun fromDomainModel(budget: Budget): BudgetEntity {
            return BudgetEntity(
                id = budget.id,
                categorySlug = budget.categorySlug,
                monthlyLimit = budget.monthlyLimit
            )
        }
    }
}
