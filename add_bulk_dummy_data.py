import os
import django
import random
from faker import Faker

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "finance_tracker.settings")
django.setup()

from transactions.models import Transaction, Category

faker = Faker()

# Fetch all categories
all_categories = list(Category.objects.all())

# Number of dummy records you want to create
num_records = 100

for _ in range(num_records):
    # Randomly decide if it's an income or an expense
    transaction_type = random.choice([Transaction.INCOME, Transaction.EXPENSE])

    # For simplicity, set a random amount between 1 and 500
    amount = round(random.uniform(1, 500), 2)

    # Select a random item name
    item = faker.unique.first_name()

    # Select a random number of categories (between 1 and 4 for this example)
    num_categories = random.randint(1, 4)
    selected_categories = random.sample(all_categories, num_categories)

    transaction = Transaction(
        date=faker.date_this_year(),
        amount=amount,
        type=transaction_type,
        item=item,
        qty=random.randint(1, 10),
        payment_method=faker.random_element(
            elements=("Cash", "Credit Card", "Debit Card", "Bank Transfer")
        ),
        comment=faker.sentence(),
    )
    transaction.save()

    # Assign the random categories to the transaction
    transaction.categories.set(selected_categories)

print(f"Added {num_records} dummy transactions to the database!")
