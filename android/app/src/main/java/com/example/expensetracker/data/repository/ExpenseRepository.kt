package com.example.expensetracker.data.repository

import com.example.expensetracker.data.local.dao.ExpenseDao
import com.example.expensetracker.data.local.entity.ExpenseEntity
import com.example.expensetracker.domain.model.CategoryStat
import com.example.expensetracker.domain.model.Expense
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

class ExpenseRepository(private val expenseDao: ExpenseDao) {

    suspend fun addExpense(expense: Expense): Long {
        return expenseDao.insertExpense(ExpenseEntity.fromDomainModel(expense))
    }

    suspend fun deleteExpense(id: Long) {
        expenseDao.deleteExpense(id)
    }

    suspend fun updateExpenseCategory(id: Long, newCategorySlug: String) {
        expenseDao.updateExpenseCategory(id, newCategorySlug)
    }

    fun getLastExpenses(limit: Int = 5): Flow<List<Expense>> {
        return expenseDao.getLastExpenses(limit).map { entities ->
            entities.map { it.toDomainModel() }
        }
    }

    fun getAllExpenses(): Flow<List<Expense>> {
        return expenseDao.getAllExpenses().map { entities ->
            entities.map { it.toDomainModel() }
        }
    }

    suspend fun getCategoryStats(sinceTimestamp: Long): List<CategoryStat> {
        return expenseDao.getCategoryStats(sinceTimestamp)
    }

    suspend fun getTotalAmount(sinceTimestamp: Long): Double {
        return expenseDao.getTotalAmount(sinceTimestamp) ?: 0.0
    }

    suspend fun getCount(sinceTimestamp: Long): Int {
        return expenseDao.getCount(sinceTimestamp)
    }

    suspend fun getMonthlySpentByCategory(categorySlug: String, sinceTimestamp: Long): Double {
        return expenseDao.getMonthlySpentByCategory(categorySlug, sinceTimestamp) ?: 0.0
    }
}
