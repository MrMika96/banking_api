from rest_framework import serializers
from rest_framework.exceptions import NotFound

from banks.models import Bank, PaymentSystem
from credit_cards.models import CreditCard


class CreditCardSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    bank = serializers.HiddenField(default="")
    payment_system = serializers.HiddenField(default="")

    class Meta:
        model = CreditCard
        fields = [
            'id', 'owner', 'number',
            'expiration_date', 'cvv', 'bank', 'payment_system'
        ]
        read_only_fields = [
            'bank', 'payment_system'
        ]

    def validate_bank(self, bank):
        split_number = self.initial_data["number"]
        bank_number = ""
        for i in range(1, 7):
            bank_number = bank_number + split_number[i]
        if Bank.objects.filter(number=bank_number).exists():
            return Bank.objects.get(number=bank_number)
        else:
            raise NotFound(detail="Bank not found")

    def validate_payment_system(self, payment_system):
        split_number = self.initial_data["number"]
        payment_number = split_number[0]
        if PaymentSystem.objects.filter(number=payment_number).exists():
            return PaymentSystem.objects.get(number=payment_number)
        else:
            raise NotFound(detail="Payment system not found")
