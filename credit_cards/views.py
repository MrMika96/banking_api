from rest_framework import viewsets
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated

from credit_cards.models import CreditCard
from credit_cards.serializers import CreditCardSerializer, CreditCardCreateSerializer, ChangeCardCurrencySerializer


class CreditCardViewSet(viewsets.ModelViewSet):
    queryset = CreditCard.objects.all()
    serializer_class = CreditCardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.method == "GET":
            self.queryset = self.queryset.filter(owner=self.request.user)
        return self.queryset.prefetch_related('bank', 'owner')


class CreateCreditCardViewSet(CreateAPIView):
    queryset = CreditCard.objects.all()
    serializer_class = CreditCardCreateSerializer
    permission_classes = [IsAuthenticated]


class ChangeCardCurrencyView(UpdateAPIView):
    queryset = CreditCard.objects.all()
    serializer_class = ChangeCardCurrencySerializer
    permission_classes = [IsAuthenticated]
