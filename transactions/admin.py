from django.contrib import admin
from .models import Transaction, Category


class TransactionAdmin(admin.ModelAdmin):
    # Define the fields to be displayed in the list view
    list_display = (
        "id",
        "type",
        "amount",
        "date",
        "comment",
        "payment_method",
        "qty",
        "receipt",
        "item",
        "linked_transaction_id",
    )

    # Provide filtering options in the admin list view
    list_filter = (
        "type",
        "date",
        "categories__name",
    )

    # Define search fields for the search bar in the admin interface
    search_fields = ("item", "comment", "categories__name")

    # This method joins the related categories and displays them as a comma-separated list
    def categories_list(self, obj):
        return ", ".join([category.name for category in obj.categories.all()])

    categories_list.short_description = "Categories"


class CategoryAdmin(admin.ModelAdmin):
    # Define the fields to be displayed in the list view for categories
    list_display = ("id", "name")

    # Define search fields for the search bar in the admin interface
    search_fields = ("name",)


# Register the models and their associated admin classes
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Category, CategoryAdmin)
