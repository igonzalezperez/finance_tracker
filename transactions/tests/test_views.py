import logging
import uuid
from typing import Any, Dict, List, Optional, Set

from django.db import models
from django.db.models import Manager, QuerySet
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from transactions.models import Transaction

from .factories import (
    BranchFactory,
    CategoryFactory,
    CurrencyCodeFactory,
    ParentCategoryFactory,
    TransactionFactory,
    UserFactory,
    VendorFactory,
)

logger = logging.getLogger(__name__)


class TransactionBaseTestCase(APITestCase):
    """
    Base test case for Transaction-related tests.

    This class provides common setup logic and helper methods to create mock
    Transaction objects and Transaction payload data for reuse across different
    test classes that inherit from it.
    """

    endpoint_create = "api:transaction-list-create"
    endpoint_list = endpoint_create
    endpoint_retrieve = "api:transaction-retrieve-update-destroy"
    endpoint_update = endpoint_retrieve
    endpoint_delete = endpoint_retrieve
    fields = [
        *Transaction._meta.fields,
        *Transaction._meta.many_to_many,  # type: ignore
    ]
    input_fields = [
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
        "payment_method",
        "currency",
        "linked_transaction",
        "comment",
    ]

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

    def get_value_for_field(self, value: Any, field_name: str) -> Any:
        """
        Get the appropriate value for a specific field.

        :param value: The field value
        :param field_name: The name of the field
        :return: The processed field value
        """
        if isinstance(
            value, (QuerySet[models.Model], Manager)  # type: ignore
        ):  # Handle Many-to-Many and reverse Foreign Key fields
            items = value.all()
            return [item.name if hasattr(item, "name") else None for item in items]
        elif isinstance(
            value, models.Model
        ):  # Handle Foreign Key and One-to-One fields
            return self.handle_related_model(value, field_name)
        elif isinstance(value, uuid.UUID):
            return str(value)
        else:
            return value

    def handle_related_model(
        self,
        value: models.Model,
        field_name: str,
    ) -> Any:
        """
        Handle related model fields and return a processed value.

        :param value: The related model instance
        :param field_name: The name of the field
        :return: The processed value for the related model field
        """
        if field_name in ("user", "created_by", "updated_by", "deleted_by"):
            return value.username if hasattr(value, "username") else None
        if field_name == "currency":
            return value.code if hasattr(value, "code") else None
        return value.name if hasattr(value, "name") else None

    def model_to_dict(self, obj: models.Model) -> Dict[str, Any]:
        """
        Convert a Django model instance to a dictionary.

        :param obj: The Django model instance
        :return: A dictionary representation of the instance
        """
        data = {}
        for field in self.fields:
            try:
                value = getattr(obj, field.name)
            except AttributeError:
                continue  # Skip if the attribute doesn't exist

            if value is not None:
                data[field.name] = self.get_value_for_field(value, field.name)

        return data

    def create_transaction_data(self):
        """
        Return a dictionary containing fields from a `TransactionFactory`
        instance.
        """
        transaction_data = TransactionFactory.create(
            user=self.user,
            vendor=self.vendor,
            branch=self.branch,
            category=self.category,
            currency=self.currency_code,
        )
        return {
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

    def assert_equal_fields(
        self,
        obj_1: models.Model,
        obj_2: models.Model,
        exclude_fields: Optional[List[str]] = None,
        include_fields: Optional[List[str]] = None,
    ) -> None:
        """
        Assert equality of specified fields between two Django model objects.

        :param obj_1: The first Django model object to compare.
        :param obj_2: The second Django model object to compare.
        :param Optional[List[str]] exclude_fields: A list of field names to be
        excluded during comparison, defaults to None.
        :param Optional[List[str]] include_fields: A list of field names to be
        included during comparison, defaults to None.
        """
        if exclude_fields is None:
            exclude_fields = []
        else:
            exclude_fields = list(set(exclude_fields))

        if include_fields is None:
            include_fields = list(set(field.name for field in self.fields))
        else:
            include_fields = list(set(include_fields))

        # Compute the set of fields to actually check
        fields_to_check: Set[str] = set(include_fields) - set(exclude_fields)

        for field_name in fields_to_check:
            self.assertEqual(
                getattr(obj_1, field_name),
                getattr(obj_2, field_name),
            )


class TransactionCRUDTests(TransactionBaseTestCase):
    """
    Test case for CRUD operations on Transactions.

    This class extends TransactionBaseTestCase to inherit its setup and helper
    methods. It verifies the successful Create, Read, Update (including soft
    deletes and undeletes), and Delete operations on Transactions when accessed
    by an authenticated user.
    """

    def test_list_transactions(self):
        url = reverse(self.endpoint_list)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)

    def test_retrieve_transaction(self):
        tr = Transaction.objects.get(uuid=self.transactions[0].uuid)
        url = reverse(
            self.endpoint_retrieve,
            kwargs={"pk": tr.pk},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["uuid"], str(tr.uuid))

    def test_create_transaction(self):
        url = reverse(self.endpoint_create)

        data = self.create_transaction_data()
        response = self.client.post(url, data, format="json")

        if response.status_code != status.HTTP_201_CREATED:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_tr = Transaction.objects.get(uuid=response.data["uuid"])
        self.assertGreaterEqual(created_tr.tags.count(), 1)
        self.assertLessEqual(created_tr.tags.count(), 3)

    def test_update_transaction(self):
        tr = Transaction.objects.get(uuid=self.transactions[0].uuid)
        new_data = Transaction.objects.get(uuid=self.transactions[2].uuid)
        data = self.model_to_dict(new_data)
        data = {k: v for k, v in data.items() if k in self.input_fields}
        response = self.update_transaction(tr, data)

        if response.status_code != status.HTTP_200_OK:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        new_tr = Transaction.objects.get(uuid=tr.uuid)

        self.assertEqual(tr.uuid, new_tr.uuid)
        self.assertEqual(tr.created_by, new_tr.created_by)
        self.assertEqual(tr.created_at, new_tr.created_at)
        self.assertNotEqual(tr.updated_at, new_tr.updated_at)

    def update_transaction(self, tr, data):
        url = reverse(
            self.endpoint_update,
            kwargs={"pk": str(tr.uuid)},
        )
        response = self.client.patch(url, data, format="json")
        return response

    def soft_delete_assertions(self, response, tr):
        if response.status_code != status.HTTP_204_NO_CONTENT:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        new_tr = Transaction.objects.get(uuid=tr.uuid)

        self.assert_equal_fields(
            tr,
            new_tr,
            ["is_deleted", "deleted_at", "updated_at"],
        )

        self.assertTrue(new_tr.is_deleted)
        self.assertIsNotNone(new_tr.updated_at)
        self.assertNotEqual(tr.updated_at, new_tr.updated_at)

    def test_soft_delete_transaction(self):
        tr = Transaction.objects.get(uuid=self.transactions[0].uuid)
        data = {
            "is_deleted": True,
        }
        response = self.update_transaction(tr, data)
        self.soft_delete_assertions(response, tr)

    def test_undelete_transaction(self):
        tr = Transaction.objects.get(uuid=self.transactions[0].uuid)
        # Soft delete the transaction first
        soft_delete_data = {
            "is_deleted": True,
        }
        response_0 = self.update_transaction(tr, soft_delete_data)
        self.soft_delete_assertions(response_0, tr)

        tr.refresh_from_db()
        data = {
            "is_deleted": False,
        }
        response = self.update_transaction(tr, data)

        if response.status_code != status.HTTP_204_NO_CONTENT:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Confirm the transaction is undeleted
        undeleted_tr = Transaction.objects.get(pk=tr.pk)

        for field in self.fields:
            if field.name not in ("is_deleted", "deleted_at", "updated_at"):
                self.assertEqual(
                    getattr(tr, field.name), getattr(undeleted_tr, field.name)
                )

        self.assertFalse(undeleted_tr.is_deleted)

        self.assertIsNotNone(undeleted_tr.updated_at)
        self.assertNotEqual(tr.updated_at, undeleted_tr.updated_at)

        self.assertIsNotNone(tr.deleted_at)
        self.assertIsNone(undeleted_tr.deleted_at)

    def test_hard_delete_transaction(self):
        tr = Transaction.objects.get(uuid=self.transactions[0].uuid)
        url = reverse(
            self.endpoint_delete,
            kwargs={"pk": tr.uuid},
        )
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Transaction.objects.filter(pk=tr.pk).exists(),
        )


class TransactionUnauthorizedTests(TransactionBaseTestCase):
    """
    Test case for unauthorized access to Transactions.

    This class extends TransactionBaseTestCase to inherit its setup and helper
    methods. It verifies that unauthenticated access to CRUD operations on
    Transactions results in a 401 Unauthorized status.
    """

    def setUp(self):
        super().setUp()  # run the setUp from TransactionBaseTestCase
        logger.info("Unauthorized transactions tests.")
        self.client.logout()  # then log out the user
        # Do not authenticate, to test unauthorized access

    def test_list_transactions_unauthenticated(self):
        url = reverse(self.endpoint_list)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_transaction_unauthenticated(self):
        tr = Transaction.objects.get(uuid=self.transactions[0].uuid)
        url = reverse(self.endpoint_retrieve, kwargs={"pk": tr.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_transaction_unauthenticated(self):
        url = reverse(self.endpoint_create)
        data = self.create_transaction_data()
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_transaction_unauthenticated(self):
        tr = Transaction.objects.get(uuid=self.transactions[0].uuid)
        url = reverse(self.endpoint_update, kwargs={"pk": tr.pk})
        data = self.create_transaction_data()
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_transaction_unauthenticated(self):
        tr = Transaction.objects.get(uuid=self.transactions[0].uuid)
        url = reverse(self.endpoint_delete, kwargs={"pk": tr.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
