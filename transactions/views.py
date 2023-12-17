"""
Transaction views from serializers
"""
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Transaction
from .serializers import TransactionSerializer


class TransactionListCreateView(ListCreateAPIView):
    """
    Handles the creation of new transactions and the listing of all
    transactions.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer

    def get_queryset(self):
        return Transaction.objects.filter(
            user=self.request.user,
        ).prefetch_related("tags")

    def perform_create(self, serializer):
        """
        Override the creation method to add the user who created the
        transaction.

        :param serializer: Transaction serializer instance
        """
        serializer.save(created_by=self.request.user)


class TransactionRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """
    Handles retrieving, updating and destroying a single transaction.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer

    def get_queryset(self):
        return Transaction.objects.filter(
            user=self.request.user,
        ).prefetch_related("tags")

    def update(self, request, *args, **kwargs):
        """
        Custom update method to handle soft delete and undelete.
        """
        instance = self.get_object()

        is_deleted = request.data.get("is_deleted", None)
        if is_deleted is not None:
            if is_deleted:
                instance.soft_delete(deleted_by=request.user)
            else:
                instance.undelete(undeleted_by=request.user)

            return Response(status=status.HTTP_204_NO_CONTENT)

        # If not a soft delete or undelete operation, proceed as normal
        return super().update(request, *args, **kwargs)

    def perform_update(self, serializer):
        """
        Override the update method to handle soft delete and updating user
        details.

        :param serializer: Transaction serializer instance
        """
        if self.request.data.get("is_deleted", None) is None:
            serializer.save(updated_by=self.request.user)
