from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from credit_cards.models import CreditCard
from credit_cards.serializers import CreditCardSerializer


class CreditCardViewSet(viewsets.ModelViewSet):
    queryset = CreditCard.objects.all()
    serializer_class = CreditCardSerializer
    permission_classes = [IsAuthenticated]
