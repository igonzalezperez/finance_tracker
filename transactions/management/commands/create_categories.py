from django.core.management.base import BaseCommand
from transactions.models import Category


class Command(BaseCommand):
    help = "Create predefined categories"

    def handle(self, *args, **kwargs):
        categories = [
            "Groceries",
            "Dining Out",
            "Transportation",
            "Entertainment",
            "Utilities",
            "Rent/Mortgage",
            "Healthcare",
            "Vacation",
            "Electronics",
            "Clothing",
            "Gifts",
            "Miscellaneous",
        ]

        for cat_name in categories:
            Category.objects.create(name=cat_name)

        self.stdout.write(self.style.SUCCESS("Successfully created categories!"))
