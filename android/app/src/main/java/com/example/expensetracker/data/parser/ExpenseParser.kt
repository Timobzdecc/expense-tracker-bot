package com.example.expensetracker.data.parser

object ExpenseParser {

    /**
     * Parses a text input into an amount and description.
     * Handles formats:
     * - "бензин 300" (description then amount)
     * - "300 бензин" (amount then description)
     * - "1 500 кофе" (spaces in numbers)
     * - "350.50" or "350,50" (decimals)
     *
     * Returns Pair(amount, description) or null if parsing fails.
     */
    fun parse(text: String): Pair<Double, String>? {
        val trimmed = text.trim()
        if (trimmed.isEmpty()) return null

        // 1. Try format: Description + Amount
        // e.g. "Бензин 1 500,50" -> match1="Бензин", match2="1 500,50"
        val descAmountRegex = Regex("""^(.*?)\s+((?:\d[\d\s]*)(?:[.,]\d+)?)$""")
        val matchDescAmount = descAmountRegex.find(trimmed)
        if (matchDescAmount != null) {
            val (desc, amountStr) = matchDescAmount.destructured
            val amount = parseNumber(amountStr)
            if (amount != null && desc.isNotBlank()) {
                return Pair(amount, desc.trim())
            }
        }

        // 2. Try format: Amount + Description
        // e.g. "1 500,50 Бензин" -> match1="1 500,50", match2="Бензин"
        val amountDescRegex = Regex("""^((?:\d[\d\s]*)(?:[.,]\d+)?)\s+(.*)$""")
        val matchAmountDesc = amountDescRegex.find(trimmed)
        if (matchAmountDesc != null) {
            val (amountStr, desc) = matchAmountDesc.destructured
            val amount = parseNumber(amountStr)
            if (amount != null && desc.isNotBlank()) {
                return Pair(amount, desc.trim())
            }
        }

        // 3. Fallback: just a number (no description)
        val amount = parseNumber(trimmed)
        if (amount != null) {
             return Pair(amount, "Без описания")
        }

        return null
    }

    private fun parseNumber(str: String): Double? {
        return try {
            val normalized = str.replace(" ", "").replace(",", ".")
            normalized.toDouble()
        } catch (e: NumberFormatException) {
            null
        }
    }
}
