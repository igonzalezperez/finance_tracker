from django.urls import path

from .views import TransactionListCreateView, TransactionRetrieveUpdateDestroyView

app_name = "transactions"

urlpatterns = [
    path(
        "transactions/",
        TransactionListCreateView.as_view(),
        name="transaction-list-create",
    ),
    path(
        "transactions/<uuid:pk>/",
        TransactionRetrieveUpdateDestroyView.as_view(),
        name="transaction-retrieve-update-destroy",
    ),
    path("", TransactionListCreateView.as_view(), name="transaction-home"),
]
