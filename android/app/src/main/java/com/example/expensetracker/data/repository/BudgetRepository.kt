package com.example.expensetracker.data.repository

import com.example.expensetracker.data.local.dao.BudgetDao
import com.example.expensetracker.data.local.entity.BudgetEntity
import com.example.expensetracker.domain.model.Budget
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

class BudgetRepository(private val budgetDao: BudgetDao) {

    suspend fun setBudget(budget: Budget) {
        budgetDao.upsertBudget(BudgetEntity.fromDomainModel(budget))
    }

    fun getAllBudgets(): Flow<List<Budget>> {
        return budgetDao.getAllBudgets().map { entities ->
            entities.map { it.toDomainModel() }
        }
    }

    suspend fun getBudgetByCategory(categorySlug: String): Budget? {
        return budgetDao.getBudgetByCategory(categorySlug)?.toDomainModel()
    }
}
