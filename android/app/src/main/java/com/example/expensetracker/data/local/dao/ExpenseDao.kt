package com.example.expensetracker.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.Query
import com.example.expensetracker.data.local.entity.ExpenseEntity
import com.example.expensetracker.domain.model.CategoryStat
import kotlinx.coroutines.flow.Flow

@Dao
interface ExpenseDao {
    @Insert
    suspend fun insertExpense(expense: ExpenseEntity): Long

    @Query("DELETE FROM expenses WHERE id = :id")
    suspend fun deleteExpense(id: Long)

    @Query("UPDATE expenses SET categorySlug = :newCategorySlug WHERE id = :id")
    suspend fun updateExpenseCategory(id: Long, newCategorySlug: String)

    @Query("SELECT * FROM expenses ORDER BY createdAt DESC LIMIT :limit")
    fun getLastExpenses(limit: Int): Flow<List<ExpenseEntity>>

    @Query("SELECT * FROM expenses ORDER BY createdAt DESC")
    fun getAllExpenses(): Flow<List<ExpenseEntity>>

    @Query("SELECT categorySlug, SUM(amount) as amount, COUNT(*) as count FROM expenses WHERE createdAt >= :since GROUP BY categorySlug")
    suspend fun getCategoryStats(since: Long): List<CategoryStat>

    @Query("SELECT SUM(amount) FROM expenses WHERE createdAt >= :since")
    suspend fun getTotalAmount(since: Long): Double?

    @Query("SELECT COUNT(*) FROM expenses WHERE createdAt >= :since")
    suspend fun getCount(since: Long): Int

    @Query("SELECT SUM(amount) FROM expenses WHERE categorySlug = :categorySlug AND createdAt >= :since")
    suspend fun getMonthlySpentByCategory(categorySlug: String, since: Long): Double?
}
