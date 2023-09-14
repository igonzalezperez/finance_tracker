from rest_framework import serializers
from .models import Transaction, Tag, CurrencyCode, Vendor


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "color"]


class TransactionSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)

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
            "tags",
        ]

    def create(self, validated_data):
        tags_data = validated_data.pop("tags")
        currency_data = validated_data.pop("currency")
        vendor_data = validated_data.pop("vendor")

        # Handle currency
        if currency_data and not isinstance(currency_data, CurrencyCode):
            currency, _ = CurrencyCode.objects.get_or_create(**currency_data)
            validated_data["currency"] = currency

        # Handle vendor
        if vendor_data and not isinstance(vendor_data, Vendor):
            vendor, _ = Vendor.objects.get_or_create(**vendor_data)
            validated_data["vendor"] = vendor

        transaction = Transaction.objects.create(**validated_data)

        # Handle tags
        for tag_data in tags_data:
            tag, _ = Tag.objects.get_or_create(**tag_data)
            transaction.tags.add(tag)

        return transaction

    def update(self, instance, validated_data):
        """
        Update Transaction instance.

        Overriding the update method to handle nested tags data.
        """
        tags_data = validated_data.pop("tags")

        # Updating standard fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Handling tags update
        for tag_data in tags_data:
            tag_id = tag_data.get("id")
            tag = instance.tags.get(id=tag_id)
            for attr, value in tag_data.items():
                setattr(tag, attr, value)
            tag.save()

        return instance
