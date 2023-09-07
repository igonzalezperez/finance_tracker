from rest_framework import serializers
from .models import Transaction, Category


class CategorySerializer(serializers.ModelSerializer):
    """
    Category Serializer

    Serializes the Category model to expose category name in the API.
    """

    class Meta:
        model = Category
        fields = ["id", "name", "color"]


class TransactionSerializer(serializers.ModelSerializer):
    """
    Transaction Serializer

    Serializes the Transaction model to expose necessary fields in the API. It
    uses CategorySerializer to convert category IDs to human-readable names.
    """

    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "date",
            "created_at",
            "amount",
            "type",
            "item",
            "qty",
            "receipt",
            "payment_method",
            "comment",
            "user",
            "currency",
            "vendor",
            "linked_transaction",
            "categories",
        ]

    def create(self, validated_data):
        """
        Create Transaction instance.

        Overriding the create method to handle nested categories data.
        """
        categories_data = validated_data.pop("categories")
        transaction = Transaction.objects.create(**validated_data)

        for category_data in categories_data:
            Category.objects.create(transaction=transaction, **category_data)
        return transaction

    def update(self, instance, validated_data):
        """
        Update Transaction instance.

        Overriding the update method to handle nested categories data.
        """
        categories_data = validated_data.pop("categories")

        # Updating standard fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Handling categories update
        for category_data in categories_data:
            category_id = category_data.get("id")
            category = instance.categories.get(id=category_id)
            for attr, value in category_data.items():
                setattr(category, attr, value)
            category.save()

        return instance
