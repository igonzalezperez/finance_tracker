from rest_framework import serializers
from .models import (
    Transaction,
    CurrencyCode,
    Vendor,
    Branch,
    Category,
    Tag,
    TransactionTag,
)
from django.contrib.auth import get_user_model


class CurrencyCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyCode
        fields = ["code"]


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ["name"]


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ["name"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["name"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["name"]


class TransactionTagSerializer(serializers.ModelSerializer):
    tag = TagSerializer()

    class Meta:
        model = TransactionTag
        fields = ["tag"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["username"]


class TransactionSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    currency = CurrencyCodeSerializer()
    vendor = VendorSerializer()
    branch = BranchSerializer()
    category = CategorySerializer()
    tags = serializers.SerializerMethodField()
    linked_transaction = serializers.PrimaryKeyRelatedField(
        queryset=Transaction.objects.all(), allow_null=True
    )

    class Meta:
        model = Transaction
        single_fields = [
            "user",
            "currency",
            "vendor",
            "branch",
            "category",
            "linked_transaction",
        ]
        multi_fields = ["tags"]
        fields = single_fields + multi_fields

    def to_representation(self, obj):
        representation = super().to_representation(obj)
        for field in self.Meta.single_fields:
            field_obj = getattr(obj, field, None)
            if field == "user":
                representation[field] = getattr(field_obj, "username", None)
            elif field == "currency":
                representation[field] = getattr(field_obj, "code", None)
            else:
                if field_obj:
                    representation[field] = getattr(field_obj, "name", None)
        return representation

    def get_tags(self, obj):
        return [tag_rel.tag.name for tag_rel in obj.transactiontag_set.all()]

    def create(self, validated_data):
        tags_data = validated_data.pop("tags")
        transaction = Transaction.objects.create(**validated_data)
        for tag_data in tags_data:
            tag, _ = Tag.objects.get_or_create(**tag_data)
            transaction.tags.add(tag)
        return transaction

    def update(self, instance, validated_data):
        tags_data = validated_data.pop("tags")
        instance = super().update(instance, validated_data)

        instance.tags.clear()
        for tag_data in tags_data:
            tag, _ = Tag.objects.get_or_create(**tag_data)
            instance.tags.add(tag)

        return instance
