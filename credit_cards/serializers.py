from rest_framework import serializers

from credit_cards.models import CreditCard


class CreditCardSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = CreditCard
        fields = [
            'id', 'owner', 'number',
            'expiration_date', 'cvv', 'bank', 'payment_system'
        ]
        read_only_fields = [
            'bank', 'payment_system'
        ]
