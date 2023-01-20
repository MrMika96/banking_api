from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from banks.models import Bank, PaymentSystem
from banks.serializers import BanksSerializer, PaymentSystemSerializer


class BanksViewSet(viewsets.ModelViewSet):
    queryset = Bank.objects.all()
    pagination_class = None
    serializer_class = BanksSerializer
    permission_classes = [IsAuthenticated]


class PaymentSystemViewSet(viewsets.ModelViewSet):
    queryset = PaymentSystem.objects.all()
    pagination_class = None
    serializer_class = PaymentSystemSerializer
    permission_classes = [IsAuthenticated]
