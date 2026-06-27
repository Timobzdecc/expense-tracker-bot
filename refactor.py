import re

with open("handlers.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Remove CATEGORY_BY_SLUG and CATEGORIES from imports
content = re.sub(r'from config import CATEGORY_BY_SLUG, CURRENCY, CATEGORIES', 'from config import CURRENCY', content)

# 2. Replace cat_name = CATEGORY_BY_SLUG.get(...) with cat_name = cat["slug"] or similar
content = re.sub(r'cat_name = CATEGORY_BY_SLUG\.get\(cat\["slug"\], f"❓ \{cat\[\'slug\'\]\}"\)', 'cat_name = cat["slug"]', content)
content = re.sub(r'cat_name = CATEGORY_BY_SLUG\.get\(exp\["category_slug"\], "❓"\)', 'cat_name = exp["category_slug"]', content)
content = re.sub(r'cat_name = CATEGORY_BY_SLUG\.get\(b\["category_slug"\], "❓"\)', 'cat_name = b["category_slug"]', content)
content = re.sub(r'cat_name = CATEGORY_BY_SLUG\.get\(slug, slug\)', 'cat_name = slug', content)
content = re.sub(r'cat_name = CATEGORY_BY_SLUG\.get\(item\["category"\], "❓ Прочее"\)', 'cat_name = item["category"]', content)
content = re.sub(r'cat_name = CATEGORY_BY_SLUG\.get\(result\["category"\], "❓ Прочее"\)', 'cat_name = result["category"]', content)
content = re.sub(r'cat_name = CATEGORY_BY_SLUG\.get\(row\["category_slug"\], "❓"\)', 'cat_name = row["category_slug"]', content)

# 3. Update keyboard calls to pass user_id
content = re.sub(r'budget_categories_keyboard\(\)', 'budget_categories_keyboard(message.from_user.id)', content)
content = re.sub(r'category_select_keyboard\(expense_id\)', 'category_select_keyboard(expense_id, callback.from_user.id)', content)

# 4. Update parse_expense_from_image call
content = re.sub(r'parse_expense_from_image\(image_data\)', 'parse_expense_from_image(message.from_user.id, image_data)', content)

# 5. Update parse_expense call
content = re.sub(r'parse_expense\(message\.text\)', 'parse_expense(message.from_user.id, message.text)', content)

with open("handlers.py", "w", encoding="utf-8") as f:
    f.write(content)
