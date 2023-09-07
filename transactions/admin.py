from django.contrib import admin
from django.utils.html import format_html
from .models import Transaction, Category, Currency


class TransactionAdmin(admin.ModelAdmin):
    ordering = ["-date"]  # Show latest transactions first
    # Define the fields to be displayed in the list view
    list_display = (
        "id",
        "formatted_date",
        "amount",
        "type",
        "item",
        "qty",
        "vendor",
        "categories_list",
        "payment_method",
        "currency",
        "comment",
        "formatted_created_at",
    )

    # Provide filtering options in the admin list view
    list_filter = (
        "type",
        "date",
        "categories__name",
    )

    # Define search fields for the search bar in the admin interface
    search_fields = ("item", "comment", "categories__name")

    def formatted_date(self, obj):
        return format_html("<span>{}</span>", obj.date.strftime("%Y-%m-%d"))

    formatted_date.short_description = "Date"

    def formatted_created_at(self, obj):
        return format_html(
            "<span>{}</span>", obj.created_at.strftime("%Y-%m-%d %H:%M:%S")
        )

    formatted_created_at.short_description = "Created At"

    # This method joins the related categories and displays them as a comma-separated list
    def categories_list(self, obj):
        return ", ".join([category.name for category in obj.categories.all()])

    categories_list.short_description = "Categories"


class CategoryAdmin(admin.ModelAdmin):
    # Define the fields to be displayed in the list view for categories
    list_display = ("id", "name", "color")

    # Define search fields for the search bar in the admin interface
    search_fields = ("name",)


# Register the models and their associated admin classes
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Currency)
