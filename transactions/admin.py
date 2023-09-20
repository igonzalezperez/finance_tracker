from django.contrib import admin
from .models import (
    Vendor,
    CurrencyCode,
    CurrencyData,
    Tag,
    Transaction,
    TransactionTag,
    Category,
    ParentCategory,
    Branch,
)


class ParentCategoryAdmin(admin.ModelAdmin):
    ordering = ["name"]
    list_display = ("uuid", "name", "created_at")


class CategoryAdmin(admin.ModelAdmin):
    ordering = ["parent", "name"]
    list_display = ("uuid", "parent", "name", "created_at")


class VendorAdmin(admin.ModelAdmin):
    ordering = ["name"]
    list_display = ("uuid", "name", "created_at")


class BranchAdmin(admin.ModelAdmin):
    ordering = ["name"]
    list_display = ("uuid", "name", "get_vendor", "created_at")

    def get_vendor(self, obj):
        return obj.vendor.name

    get_vendor.short_description = "Vendor"


class CurrencyCodeAdmin(admin.ModelAdmin):
    ordering = ["code"]
    list_display = ("uuid", "code")


class CurrencyDataAdmin(admin.ModelAdmin):
    ordering = ["currency_code__code"]
    list_display = ("uuid", "country", "currency_name", "currency_code")


class TagAdmin(admin.ModelAdmin):
    ordering = ["name"]
    list_display = ("uuid", "name", "created_at")


# Admin views for the Transaction model
class TransactionAdmin(admin.ModelAdmin):
    ordering = ["-date"]
    list_display = (
        "uuid",
        "user",
        "date",
        "amount",
        "type",
        "currency",
        "item",
        "quantity",
        "brand",
        "vendor",
        "branch",
        "category",
        "tag_list",
        "linked_transaction",
        "payment_method",
        "comment",
    )
    list_filter = [
        "type",
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("transactiontag_set__tag")

    def tag_list(self, obj):
        return ", ".join(
            [
                str(transaction_tag.tag.name)
                for transaction_tag in obj.transactiontag_set.all()
            ]
        )


# Admin views for the TransactionTag model
class TransactionTagAdmin(admin.ModelAdmin):
    list_display = ("uuid", "transaction", "tag", "created_at")
    list_filter = ("tag",)


# Register the models and their associated admin classes
admin.site.register(ParentCategory, ParentCategoryAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Branch, BranchAdmin)
admin.site.register(Vendor, VendorAdmin)
admin.site.register(CurrencyCode, CurrencyCodeAdmin)
admin.site.register(CurrencyData, CurrencyDataAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(TransactionTag, TransactionTagAdmin)
