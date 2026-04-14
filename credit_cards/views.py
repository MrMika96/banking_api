"""Module with views for credit cards app."""
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated

from credit_cards.models import CreditCard
from credit_cards.serializers import (
    CardBalanceReplenishmentSerializer,
    ChangeCardCurrencySerializer,
    CreditCardCreateSerializer,
    CreditCardSerializer,
    TransferFromCardToCardSerializer,
)


class CreditCardViewSet(viewsets.ModelViewSet):
    """Credit card view set."""

    queryset = CreditCard.objects.all()
    serializer_class = CreditCardSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        """Return queryset."""
        qs = super().get_queryset()
        if self.request.method == "GET":
            qs = qs.filter(owner=self.request.user)
        return qs.select_related("bank", "owner")

    def get_serializer_class(self):
        """Return serializer based on action."""
        if self.action == "create": # noqa
            return CreditCardCreateSerializer
        return super().get_serializer_class()


class CreditCardMoneyTransferView(generics.CreateAPIView):
    """Transfer money from one card to another."""

    queryset = CreditCard.objects.all()
    serializer_class = TransferFromCardToCardSerializer
    permission_classes = [IsAuthenticated]


class CreditCardChangeCurrencyView(generics.UpdateAPIView):
    """Change credit card currency."""

    queryset = CreditCard.objects.all()
    serializer_class = ChangeCardCurrencySerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["put"]


class CreditCardBalanceReplenishmentView(generics.UpdateAPIView):
    """Replenish credit card balance."""

    queryset = CreditCard.objects.all()
    serializer_class = CardBalanceReplenishmentSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["put"]
