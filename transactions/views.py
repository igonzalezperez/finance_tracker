"""
API views for transactions.
"""
from django.apps import apps
from django.http import JsonResponse
from django.views import View
from rest_framework import generics, permissions, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Transaction
from .serializers import TransactionSerializer
from rest_framework import permissions
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title="API")


class ModelMetadataView(View):
    def get(self, request, model_name):
        try:
            model = apps.get_model("transactions", model_name)
        except LookupError:
            return JsonResponse({"error": "Model not found"}, status=404)

        fields_data = []

        for field in model._meta.get_fields():
            field_data = {
                "name": field.name,
                "type": field.get_internal_type(),
            }
            if hasattr(field, "verbose_name"):
                vrb_name = field.verbose_name
            elif hasattr(field, "related_model") and field.related_model:
                related_model = field.related_model
                vrb_name = related_model._meta.verbose_name
            field_data["verbose_name"] = vrb_name

            if field.get_internal_type() == "ForeignKey":
                if field.related_model == model:
                    continue
                field_data["related_model"] = field.related_model.__name__
            field_data["auto_created"] = field.auto_created
            fields_data.append(field_data)

        return JsonResponse(fields_data, safe=False)


class FieldsMetadataView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        fields_metadata = {}
        for field in Transaction._meta.get_fields():
            if hasattr(field, "verbose_name"):
                vrb_name = field.verbose_name
            elif hasattr(field, "related_model") and field.related_model:
                related_model = field.related_model
                vrb_name = related_model._meta.verbose_name
            fields_metadata[field.name] = {
                "verbose_name": vrb_name,
                "type": field.get_internal_type(),
            }
        return Response(fields_metadata)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class ValidateTokenView(APIView):
    def get(self, request):
        return Response({"message": "Token is valid"}, status=status.HTTP_200_OK)


# DRF API views
class TransactionList(generics.ListCreateAPIView):
    """
    List all transactions or create a new transaction.
    Only authenticated users can create a transaction.
    """

    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


class TransactionDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a specific transaction by its ID.
    Only authenticated users can update or delete.
    """

    queryset = Transaction.objects.all()  # pylint: disable=no-member
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class AddTransactionView(generics.CreateAPIView):
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()
