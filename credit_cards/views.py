from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from credit_cards.models import CreditCard
from credit_cards.serializers import (
    CreditCardSerializer,
    CreditCardCreateSerializer,
    ChangeCardCurrencySerializer,
    CardBalanceReplenishmentSerializer,
    TransferFromCardToCardSerializer
)


class CreditCardViewSet(viewsets.ModelViewSet):
    queryset = CreditCard.objects.all()
    serializer_class = CreditCardSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_queryset(self):
        qs = super().get_queryset()

        if self.request.method == "GET":
            qs = qs.filter(owner=self.request.user)
        return qs.select_related('bank', 'owner')

    def get_serializer_class(self):
        if self.action == 'create':
            return CreditCardCreateSerializer
        if self.action == 'money_transfer':
            return TransferFromCardToCardSerializer
        if self.action == 'change_currency':
            return ChangeCardCurrencySerializer
        if self.action == 'change_currency':
            return ChangeCardCurrencySerializer

        return super().get_serializer_class()

    @extend_schema(
        request=CreditCardSerializer,
        responses=CreditCardSerializer
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        request=TransferFromCardToCardSerializer,
        responses=TransferFromCardToCardSerializer
    )
    @action(
        url_name='money_transfer', url_path='money_transfer',
        methods=['post'], detail=False
    )
    def money_transfer(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        request=ChangeCardCurrencySerializer,
        responses=ChangeCardCurrencySerializer
    )
    @action(
        url_name='change_currency',
        url_path='change_currency/(?P<pk>[^/.]+)',
        methods=['put'], detail=False
    )
    def change_currency(self, request, pk: int, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        request=CardBalanceReplenishmentSerializer,
        responses=CardBalanceReplenishmentSerializer
    )
    @action(
        url_name='balance_replenishment',
        url_path='balance_replenishment/(?P<pk>[^/.]+)',
        methods=['put'], detail=False
    )
    def balance_replenishment(self, request, pk: int, *args, **kwargs):
        return super().update(request, *args, **kwargs)
