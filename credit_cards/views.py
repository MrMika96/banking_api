"""Module with views for credit cards app."""
from drf_spectacular.utils import extend_schema_view
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from credit_cards.models import CreditCard
from credit_cards.serializers import (
    CardBalanceReplenishmentSerializer,
    ChangeCardCurrencySerializer,
    CreditCardCreateSerializer,
    CreditCardSerializer,
    TransferFromCardToCardSerializer,
)
from . import docs
from .services.credit_card_services import update_credit_card_currency


@extend_schema_view(**docs.get_credit_card_docs())
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


@extend_schema_view(**docs.get_credit_card_transfer_docs())
class CreditCardMoneyTransferView(generics.CreateAPIView):
    """Transfer money from one card to another."""

    queryset = CreditCard.objects.all()
    serializer_class = TransferFromCardToCardSerializer
    permission_classes = [IsAuthenticated]


@extend_schema_view(**docs.get_credit_card_currency_change_docs())
class CreditCardChangeCurrencyView(generics.GenericAPIView):
    """Change credit card currency."""

    queryset = CreditCard.objects.all()
    serializer_class = ChangeCardCurrencySerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["put"]

    def put(self, request, pk):
        """Return new currency of a credit card after it got changed."""
        currency_data = self.get_serializer(data=request.data)
        currency_data.is_valid(raise_exception=True)

        return Response(
            data=self.get_serializer(
                update_credit_card_currency(
                    credit_card_pk=pk,
                    currency_data=currency_data.validated_data
                )
            ).data,
            status=200
        )


@extend_schema_view(**docs.get_credit_card_balance_replenishment_docs())
class CreditCardBalanceReplenishmentView(generics.UpdateAPIView):
    """Replenish credit card balance."""

    queryset = CreditCard.objects.all()
    serializer_class = CardBalanceReplenishmentSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["put"]
