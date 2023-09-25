from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from .models import Branch, Category, CurrencyCode, Tag, Transaction, Vendor


class TransactionSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field="username",
        queryset=get_user_model().objects.all(),
    )
    currency = serializers.SlugRelatedField(
        slug_field="code", queryset=CurrencyCode.objects.all()
    )
    vendor = serializers.SlugRelatedField(
        slug_field="name", queryset=Vendor.objects.all()
    )
    branch = serializers.SlugRelatedField(
        slug_field="name", queryset=Branch.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field="name", queryset=Category.objects.all()
    )
    tags = serializers.SlugRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        slug_field="name",
    )
    linked_transaction = serializers.PrimaryKeyRelatedField(
        queryset=Transaction.objects.all(), allow_null=True, required=False
    )

    class Meta:
        model = Transaction
        fields = [
            "uuid",
            "date",
            "type",
            "amount",
            "item",
            "quantity",
            "brand",
            "vendor",
            "branch",
            "category",
            "tags",
            "currency",
            "payment_method",
            "receipt",
            "linked_transaction",
            "comment",
            "user",
            "created_at",
            "updated_at",
            "is_deleted",
            "deleted_at",
            "created_by",
            "updated_by",
        ]

    def __init__(self, *args, **kwargs):
        super(TransactionSerializer, self).__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.method == "PUT":
            self.fields["user"].read_only = True

    @transaction.atomic
    def create(self, validated_data):
        tag_names = validated_data.pop("tags")
        transaction = Transaction.objects.create(**validated_data)

        tags_to_add = []

        for tag_name in tag_names:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            tags_to_add.append(tag)

        transaction.tags.add(*tags_to_add)
        return transaction

    def update(self, instance, validated_data):
        tag_names = []
        if "tags" in validated_data:
            tag_names = validated_data.pop("tags")
        instance = super().update(instance, validated_data)
        if tag_names:
            instance.tags.clear()
            for tag_name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                instance.tags.add(tag)
        return instance
