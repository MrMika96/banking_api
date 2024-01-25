from django.db.models import Count
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from banks.models import Bank, PaymentSystem
from banks.serializers import (
    BanksSerializer,
    PaymentSystemSerializer,
    DetailedBankSerializer,
)


class BanksViewSet(viewsets.ModelViewSet):
    queryset = Bank.objects.all()
    pagination_class = None
    serializer_class = BanksSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "put", "delete"]

    def get_queryset(self):
        qs = super().get_queryset()

        if self.action == "retrieve":
            qs = qs.prefetch_related("cards", "cards__owner").annotate(
                number_of_clients=Count("cards__owner", distinct=True)
            )
        return qs

    def get_serializer_class(self):
        if self.action == "retrieve":
            return DetailedBankSerializer

        return super().get_serializer_class()


class PaymentSystemViewSet(viewsets.ModelViewSet):
    queryset = PaymentSystem.objects.all()
    pagination_class = None
    serializer_class = PaymentSystemSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "put"]
