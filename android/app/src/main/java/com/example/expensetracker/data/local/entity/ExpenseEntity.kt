package com.example.expensetracker.data.local.entity

import androidx.room.Entity
import androidx.room.PrimaryKey
import com.example.expensetracker.domain.model.Expense
import java.util.Date

@Entity(tableName = "expenses")
data class ExpenseEntity(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val amount: Double,
    val description: String,
    val categorySlug: String,
    val createdAt: Date = Date(),
    val photoUrl: String? = null
) {
    fun toDomainModel(): Expense {
        return Expense(
            id = id,
            amount = amount,
            description = description,
            categorySlug = categorySlug,
            createdAt = createdAt,
            photoUrl = photoUrl
        )
    }

    companion object {
        fun fromDomainModel(expense: Expense): ExpenseEntity {
            return ExpenseEntity(
                id = expense.id,
                amount = expense.amount,
                description = expense.description,
                categorySlug = expense.categorySlug,
                createdAt = expense.createdAt,
                photoUrl = expense.photoUrl
            )
        }
    }
}
