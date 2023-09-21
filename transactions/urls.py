from django.urls import path, include
from .views import (
    TransactionListCreateView,
    TransactionRetrieveUpdateDestroyView,
)

app_name = "transactions"

urlpatterns = [
    path(
        "api/v1/",
        include(
            [
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
            ]
        ),
    ),
    path(
        "", TransactionListCreateView.as_view(), name="home-transaction-list"
    ),  # Adding the base endpoint as another path to the list view
]
