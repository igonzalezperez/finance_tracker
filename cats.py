import os
import django

from transactions.models import Category


os.environ["DJANGO_SETTINGS_MODULE"] = "finance_tracker.settings"
django.setup()

categories = [
    "Housing",
    "Groceries",
    "Transportation",
    "Health",
    "Utilities",
    "Dining & Takeout",
    "Entertainment",
    "Shopping",
    "Hobbies & Sports",
    "Travel",
    "Emergency Fund",
    "Retirement",
    "Investments",
    "Credit Cards",
    "Loans",
    "Salary",
    "Freelance/Part-time Income",
    "Investment Returns",
    "Gifts",
    "Donations",
    "Gifts & Celebrations",
    "Education",
    "Insurance",
    "Vacation",
]

for cat_name in categories:
    Category.objects.create(name=cat_name)
