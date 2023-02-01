from django.db.models import Count
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from banks.models import Bank, PaymentSystem
from banks.serializers import (
    BanksSerializer, PaymentSystemSerializer,
    DetailedBankSerializer
)


class BanksViewSet(viewsets.ModelViewSet):
    queryset = Bank.objects.all()
    pagination_class = None
    serializer_class = BanksSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.kwargs.get('pk') and self.request.method == 'GET':
            self.queryset = self.queryset.prefetch_related('cards', 'cards__owner').annotate(
                number_of_clients=Count('cards__owner', distinct=True)
            )
        return self.queryset

    def get_serializer_class(self):
        if self.kwargs.get('pk') and self.request.method == 'GET':
            return DetailedBankSerializer
        return self.serializer_class


class PaymentSystemViewSet(viewsets.ModelViewSet):
    queryset = PaymentSystem.objects.all()
    pagination_class = None
    serializer_class = PaymentSystemSerializer
    permission_classes = [IsAuthenticated]
