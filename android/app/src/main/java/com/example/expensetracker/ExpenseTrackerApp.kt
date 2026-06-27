package com.example.expensetracker

import android.app.Application
import com.example.expensetracker.data.local.AppDatabase
import com.example.expensetracker.data.preferences.SettingsManager
import com.example.expensetracker.data.repository.BudgetRepository
import com.example.expensetracker.data.repository.ExpenseRepository

class ExpenseTrackerApp : Application() {

    lateinit var database: AppDatabase
        private set

    lateinit var expenseRepository: ExpenseRepository
        private set

    lateinit var budgetRepository: BudgetRepository
        private set

    lateinit var settingsManager: SettingsManager
        private set

    override fun onCreate() {
        super.onCreate()
        instance = this

        database = AppDatabase.getInstance(this)
        expenseRepository = ExpenseRepository(database.expenseDao())
        budgetRepository = BudgetRepository(database.budgetDao())
        settingsManager = SettingsManager(this)
    }

    companion object {
        lateinit var instance: ExpenseTrackerApp
            private set
    }
}
