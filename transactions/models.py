from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid


class BaseModel(models.Model):
    uuid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    deleted_at = models.DateTimeField(null=True, blank=True, editable=False)
    is_deleted = models.BooleanField(default=False, editable=False)
    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created_by",
        editable=False,
    )
    updated_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_updated_by",
        editable=False,
    )

    class Meta:
        abstract = True

    def soft_delete(self, deleted_by=None):
        if not self.is_deleted:
            self.is_deleted = True
            self.deleted_at = timezone.now()
            if deleted_by:
                self.updated_by = deleted_by
            self.save()

    def undelete(self):
        if self.is_deleted:
            self.is_deleted = False
            self.deleted_at = None
            self.updated_by = None
            self.save()


class Vendor(BaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Branch(BaseModel):
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name="branches",
        to_field="uuid",
    )
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Branches"

    def __str__(self):
        return f"{self.name} - {self.vendor.name}"


class CurrencyCode(BaseModel):
    code = models.CharField(max_length=3, unique=True)

    class Meta:
        verbose_name_plural = "CurrencyCodes"

    def __str__(self):
        return self.code


class CurrencyData(BaseModel):
    country = models.CharField(max_length=100)
    currency_name = models.CharField(max_length=100)
    currency_code = models.ForeignKey(CurrencyCode, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("country", "currency_name", "currency_code")
        verbose_name_plural = "CurrenciesData"

    def __str__(self):
        return f"{self.country} - {self.currency_name} - {self.currency_code}"


class ParentCategory(BaseModel):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = "Parent Categories"

    def __str__(self):
        return self.name


class Category(BaseModel):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey(
        ParentCategory,
        on_delete=models.CASCADE,
        related_name="child_categories",
    )

    class Meta:
        verbose_name_plural = "Categories"
        unique_together = ("parent", "name")

    def __str__(self):
        return self.name


class Tag(BaseModel):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Tags"

    def __str__(self):
        return f"{self.name}"


class Transaction(BaseModel):
    # Choices for the transaction type
    INCOME = "Income"
    EXPENSE = "Expense"
    TRANSACTION_TYPE_CHOICES = [
        (INCOME, "Income"),
        (EXPENSE, "Expense"),
    ]
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        verbose_name="User",
    )

    date = models.DateField(verbose_name="Date")
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
        CurrencyCode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Currency",
        to_field="uuid",
    )
    item = models.CharField(
        max_length=255,
        verbose_name="Item",
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="Quantity",
    )
    brand = models.CharField(
        max_length=255,
        verbose_name="Brand",
    )
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Vendor",
        to_field="uuid",
    )
    branch = models.ForeignKey(
        Branch,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Branch",
        to_field="uuid",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Category",
        to_field="uuid",
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        verbose_name="Tags",
        related_name="transactions",
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
        to_field="uuid",
    )  # Link to another transaction if needed
    payment_method = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Payment Method",
    )  # Can be expanded with choices if required
    comment = models.TextField(
        blank=True,
        verbose_name="Comment",
    )

    @property
    def verbose_names(self):
        return {f.name: f.verbose_name for f in Transaction._meta.fields}

    def __str__(self):
        return f"{self.date} - {self.amount} - {self.item} - {self.type}"


class TransactionTag(BaseModel):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
