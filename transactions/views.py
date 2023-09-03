from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Transaction


class TransactionListView(ListView):
    model = Transaction
    template_name = "transactions/transaction_list.html"


class TransactionCreateView(CreateView):
    model = Transaction
    template_name = "transactions/transaction_form.html"
    fields = [
        "date",
        "amount",
        "type",
        "item",
    ]  # List all fields you want in the form

    success_url = reverse_lazy("transaction_list")


class TransactionUpdateView(UpdateView):
    model = Transaction
    template_name = "transactions/transaction_form.html"
    fields = ["date", "amount", "type", "item"]

    success_url = reverse_lazy("transaction_list")


class TransactionDeleteView(DeleteView):
    model = Transaction
    template_name = "transactions/transaction_confirm_delete.html"

    success_url = reverse_lazy("transaction_list")
