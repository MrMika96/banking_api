"""Module with views for banks app."""
from django.db.models import Count
from drf_spectacular.utils import extend_schema_view
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from banks.models import Bank, PaymentSystem
from banks.serializers import (
    BanksSerializer,
    DetailedBankSerializer,
    PaymentSystemSerializer,
)
from . import docs


@extend_schema_view(**docs.get_bank_view_set_docs())
class BanksViewSet(viewsets.ModelViewSet):
    """View set for banks."""

    queryset = Bank.objects.all()
    pagination_class = None
    serializer_class = BanksSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "put", "delete"]

    def get_queryset(self):
        """Return queryset."""
        qs = super().get_queryset()
        if self.action == "retrieve":
            return qs.prefetch_related("cards", "cards__owner").annotate(
                number_of_clients=Count(
                    "cards__owner", distinct=True
                )
            )
        return qs

    def get_serializer_class(self):
        """Return serializer based on action."""
        if self.action == "retrieve":
            return DetailedBankSerializer
        return super().get_serializer_class()


@extend_schema_view(**docs.get_payment_system_docs())
class PaymentSystemViewSet(viewsets.ModelViewSet):
    """View set for payment system."""

    queryset = PaymentSystem.objects.all()
    pagination_class = None
    serializer_class = PaymentSystemSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "put"]
