from rest_framework import generics
from rest_framework.response import Response
from .models import Transaction
from .serializers import TransactionSerializer


class TransactionListCreateView(generics.ListCreateAPIView):
    queryset = Transaction.objects.all().prefetch_related("tags")
    serializer_class = TransactionSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TransactionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Transaction.objects.prefetch_related("tags")
    serializer_class = TransactionSerializer

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
