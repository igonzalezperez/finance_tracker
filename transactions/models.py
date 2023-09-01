from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Transaction(models.Model):
    # Choices for the transaction type
    INCOME = "Income"
    EXPENSE = "Expense"
    TRANSACTION_TYPE_CHOICES = [
        (INCOME, "Income"),
        (EXPENSE, "Expense"),
    ]

    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(
        max_length=7, choices=TRANSACTION_TYPE_CHOICES, default=EXPENSE
    )
    item = models.CharField(max_length=255)
    qty = models.PositiveIntegerField(default=1)
    categories = models.ManyToManyField(Category, related_name="transactions")
    receipt = models.FileField(
        upload_to="receipts/", blank=True, null=True
    )  # assuming image receipts
    linked_transaction = models.ForeignKey(
        "self", on_delete=models.SET_NULL, blank=True, null=True
    )  # Link to another transaction if needed
    payment_method = models.CharField(
        max_length=50, blank=True, null=True
    )  # Can be expanded with choices if required
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.item} - {self.amount} ({self.date})"
