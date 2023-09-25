import random
import factory
from django.contrib.auth import get_user_model
from transactions.models import (
    Vendor,
    Branch,
    CurrencyCode,
    CurrencyData,
    ParentCategory,
    Category,
    Tag,
    Transaction,
    TransactionTag,
)


class VendorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Vendor

    name = factory.Sequence(lambda n: f"vendor_{n}")


class BranchFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Branch

    name = factory.Sequence(lambda n: f"branch_{n}")
    vendor = factory.SubFactory(VendorFactory)


class CurrencyCodeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CurrencyCode

    code = factory.Sequence(lambda n: f"CR{n}")


class CurrencyDataFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CurrencyData

    country = factory.Sequence(lambda n: f"country_{n}")
    currency_name = factory.Sequence(lambda n: f"currency_name_{n}")
    currency_code = factory.SubFactory(CurrencyCodeFactory)


class ParentCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ParentCategory

    name = factory.Sequence(lambda n: f"parent_category_{n}")


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"category_{n}")
    parent = factory.SubFactory(ParentCategoryFactory)


class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tag

    name = factory.Sequence(lambda n: f"tag_{n}")


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.Sequence(lambda n: f"user_{n}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "password")


class TransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transaction

    user = factory.SubFactory(UserFactory)
    date = factory.Faker("date")
    amount = factory.Faker(
        "pydecimal",
        left_digits=8,
        right_digits=2,
        positive=True,
    )
    type = factory.Iterator(["Income", "Expense"])
    currency = factory.SubFactory(CurrencyCodeFactory)
    item = factory.Faker("word")
    quantity = factory.Faker("pyint")
    brand = factory.Faker("company")
    vendor = factory.SubFactory(VendorFactory)
    branch = factory.SubFactory(BranchFactory)
    category = factory.SubFactory(CategoryFactory)
    payment_method = factory.Faker("credit_card_provider")
    comment = factory.Faker("text")

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted is not None:
            for tag in extracted:
                self.tags.add(tag)
        else:
            num_tags = random.choice([1, 2, 3])
            for _ in range(num_tags):
                tag = TagFactory()
                self.tags.add(tag)


class TransactionTagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TransactionTag

    transaction = factory.SubFactory(TransactionFactory)
    tag = factory.SubFactory(TagFactory)
