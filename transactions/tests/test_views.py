from django.db import models
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from transactions.models import Transaction
from .factories import (
    UserFactory,
    VendorFactory,
    BranchFactory,
    CategoryFactory,
    CurrencyCodeFactory,
    TransactionFactory,
    ParentCategoryFactory,
)


class TransactionTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.vendor = VendorFactory()
        cls.branch = BranchFactory(vendor=cls.vendor)
        cls.parent_category = ParentCategoryFactory()
        cls.category = CategoryFactory(parent=cls.parent_category)
        cls.currency_code = CurrencyCodeFactory()
        cls.transactions = TransactionFactory.create_batch(
            5,
            user=cls.user,
            created_by=cls.user,
            updated_by=cls.user,
        )

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        # Cleanup code if necessary
        pass

    def test_list_transactions(self):
        url = reverse("api:transaction-list-create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)  # we created 5 transactions

    def test_retrieve_transaction(self):
        transaction = self.transactions[0]
        url = reverse(
            "api:transaction-retrieve-update-destroy",
            kwargs={"pk": transaction.pk},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["uuid"], str(transaction.uuid))

    def test_create_transaction(self):
        url = reverse("api:transaction-list-create")

        # Build a new transaction object using factories but don't save it to the database
        transaction_data = TransactionFactory.create(
            user=self.user,
            vendor=self.vendor,
            branch=self.branch,
            category=self.category,
            currency=self.currency_code,
        )

        data = {
            "user": transaction_data.user.username,
            "date": transaction_data.date,
            "type": transaction_data.type,
            "amount": transaction_data.amount,
            "item": transaction_data.item,
            "quantity": transaction_data.quantity,
            "brand": transaction_data.brand,
            "vendor": transaction_data.vendor.name,
            "branch": transaction_data.branch.name,
            "category": transaction_data.category.name,
            "tags": [tag.name for tag in transaction_data.tags.all()],
            "payment_method": transaction_data.payment_method,
            "currency": transaction_data.currency.code,
            "comment": transaction_data.comment,
        }
        response = self.client.post(url, data, format="json")

        if response.status_code != status.HTTP_201_CREATED:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_transaction = Transaction.objects.get(uuid=response.data["uuid"])
        self.assertGreaterEqual(created_transaction.tags.count(), 1)
        self.assertLessEqual(created_transaction.tags.count(), 3)

    def test_update_transaction(self):
        transaction = self.transactions[0]
        all_fields = [*transaction._meta.fields, *transaction._meta.many_to_many]
        old_data = {}
        for field in all_fields:
            val = getattr(transaction, field.name)
            if isinstance(field, models.ManyToManyField):
                old_data[field.name] = [tag.name for tag in val.all()]
            else:
                old_data[field.name] = val
        new_data = self.transactions[2]
        url = reverse(
            "api:transaction-retrieve-update-destroy",
            kwargs={"pk": transaction.uuid},
        )
        data = {
            "date": new_data.date,
            "type": new_data.type,
            "amount": new_data.amount,
            "item": new_data.item,
            "quantity": new_data.quantity,
            "brand": new_data.brand,
            "vendor": new_data.vendor.name,
            "branch": new_data.branch.name,
            "category": new_data.category.name,
            "tags": [tag.name for tag in new_data.tags.all()],
            "payment_method": new_data.payment_method,
            "currency": new_data.currency.code,
            "linked_transaction": str(new_data.linked_transaction.uuid)
            if new_data.linked_transaction
            else None,
            "comment": new_data.comment,
        }

        response = self.client.put(url, data, format="json")

        if response.status_code != status.HTTP_200_OK:
            print(response.data)  # Debug line

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_transaction = Transaction.objects.get(uuid=transaction.uuid)

        self.assertEqual(old_data["uuid"], updated_transaction.uuid)
        self.assertEqual(old_data["created_by"], updated_transaction.created_by)
        self.assertEqual(old_data["created_at"], updated_transaction.created_at)
        self.assertNotEqual(old_data["updated_at"], updated_transaction.updated_at)

    def test_soft_delete_transaction(self):
        transaction = self.transactions[0]
        transaction.soft_delete(deleted_by=self.user)

        self.assertTrue(transaction.is_deleted)
        self.assertIsNotNone(transaction.deleted_at)
        self.assertEqual(transaction.updated_by, self.user)

        # Assert the object is still in the database
        self.assertTrue(Transaction.objects.filter(pk=transaction.pk).exists())

    def test_undelete_transaction(self):
        transaction = self.transactions[0]
        transaction.soft_delete(deleted_by=self.user)

        # Now undelete
        transaction.undelete()

        self.assertFalse(transaction.is_deleted)
        self.assertIsNone(transaction.deleted_at)
        self.assertIsNone(transaction.updated_by)

    def test_hard_delete_transaction(self):
        transaction = self.transactions[0]
        url = reverse(
            "api:transaction-retrieve-update-destroy",
            kwargs={"pk": transaction.pk},
        )
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Make sure the object was actually deleted from the DB
        self.assertFalse(Transaction.objects.filter(pk=transaction.pk).exists())
