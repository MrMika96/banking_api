from rest_framework import serializers

from credit_cards.models import CreditCard


class CreditCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditCard
        fields = [
            'id', 'owner', 'number',
            'expiration_date', 'cvv', 'bank', 'payment_system'
        ]