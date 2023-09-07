"""
Models for the Finance Tracker application.

This module defines the core data structures for the application,
including Vendors, Currencies, Categories, and Transactions.
Each model represents a table in the database and encapsulates
the relationships and attributes specific to its respective entity.

- `Vendor`: Represents businesses or individuals where transactions take place.
- `Currency`: Defines various currencies using ISO 4217 codes.
- `Category`: Categorizes transactions (e.g., groceries, utilities).
- `Transaction`: Core entity representing individual financial transactions.

"""
from django.db import models
from django.contrib.auth.models import User


class Vendor(models.Model):
    """
    Represents a vendor or a supplier.
    """

    name = models.CharField(max_length=255, unique=True)
    details = models.TextField(blank=True)

    def __str__(self):
        return str(self.name)


class Currency(models.Model):
    """
    Represents an ISO 4217 currency code and its full name.
    """

    # ISO 4217 currency codes
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return str(self.code)

    class Meta:
        """
        Meta configuration for the Currency model.
        """

        verbose_name_plural = "Currencies"


class Category(models.Model):
    """
    Represents a category that a transaction can belong to.
    """

    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default="#FFFFFF")  # Hex color code

    def __str__(self):
        return str(self.name)

    class Meta:
        """
        Meta configuration for the Category model.
        """

        verbose_name_plural = "Categories"


class Transaction(models.Model):
    """
    Represents a financial transaction.
    """

    # Choices for the transaction type
    INCOME = "Income"
    EXPENSE = "Expense"
    TRANSACTION_TYPE_CHOICES = [
        (INCOME, "Income"),
        (EXPENSE, "Expense"),
    ]
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="User",
    )

    date = models.DateField(verbose_name="Date")
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Amount",
    )
    type = models.CharField(
        max_length=7,
        choices=TRANSACTION_TYPE_CHOICES,
        default=EXPENSE,
        verbose_name="Type",
    )
    currency = models.ForeignKey(
        Currency,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Currency",
    )
    item = models.CharField(
        max_length=255,
        verbose_name="Item",
    )
    qty = models.PositiveIntegerField(
        default=1,
        verbose_name="Quantity",
    )
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Vendor",
    )
    categories = models.ManyToManyField(
        Category,
        related_name="transactions",
        verbose_name="Categories",
    )
    receipt = models.FileField(
        upload_to="receipts/",
        blank=True,
        null=True,
        verbose_name="Receipt",
    )  # Assuming image receipts
    linked_transaction = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Linked Transaction",
    )  # Link to another transaction if needed
    payment_method = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Payment Method",
    )  # Can be expanded with choices if required
    comment = models.TextField(
        blank=True,
        verbose_name="Method",
    )

    @property
    def verbose_names(self):
        return {field.name: field.verbose_name for field in Transaction._meta.fields}

    def __str__(self):
        return f"{self.item} - {self.amount} ({self.date})"
