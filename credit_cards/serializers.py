import datetime

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from banks.models import Bank, PaymentSystem
from credit_cards.models import CreditCard


class CreditCardSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    bank = serializers.CharField(default="", write_only=True, required=False)
    payment_system = serializers.CharField(default="", write_only=True, required=False)
    bank_name = serializers.CharField(source='bank.name', read_only=True)
    payment_system_name = serializers.CharField(source='payment_system.name', read_only=True)

    class Meta:
        model = CreditCard
        fields = [
            'id', 'owner', 'number',
            'expiration_date', 'cvv', 'bank',
            'payment_system', 'currency', 'balance',
            'bank_name', 'payment_system_name', 'is_expired'
        ]
        read_only_fields = [
            'is_expired'
        ]

    def validate_bank(self, bank):
        split_number = self.initial_data["number"]
        bank_number = ""
        for i in range(1, 7):
            bank_number = bank_number + split_number[i]
        if Bank.objects.filter(number=bank_number).exists():
            return Bank.objects.get(number=bank_number)
        else:
            raise ValidationError("Bank not found")

    def validate_payment_system(self, payment_system):
        split_number = self.initial_data["number"]
        payment_number = split_number[0]
        if PaymentSystem.objects.filter(number=payment_number).exists():
            return PaymentSystem.objects.get(number=payment_number)
        else:
            raise ValidationError("Payment system not found")


class CreditCardCreateSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    expiration_date = serializers.DateField(allow_null=True, required=False)
    bank_name = serializers.CharField(source='bank.name', read_only=True)
    payment_system_name = serializers.CharField(source='payment_system.name', read_only=True)
    bank = serializers.PrimaryKeyRelatedField(queryset=Bank.objects.all(), write_only=True)
    payment_system = serializers.PrimaryKeyRelatedField(queryset=PaymentSystem.objects.all(), write_only=True)
    balance = serializers.FloatField(default=0, required=False)

    class Meta:
        model = CreditCard
        fields = [
            'id', 'owner', 'number',
            'expiration_date', 'cvv', 'bank', 'bank_name',
            'payment_system', 'payment_system_name', 'currency', 'balance'
        ]
        read_only_fields = [
            'number', 'cvv', 'is_expired'
        ]

    def create(self, validated_data):
        validated_data['number'] = CreditCard.card_number_generator(
            validated_data['bank'].number, validated_data['payment_system'].number
        )
        validated_data['cvv'] = CreditCard.cvv_generator()
        validated_data['expiration_date'] = datetime.datetime.utcnow().date() + datetime.timedelta(days=1825)
        return CreditCard.objects.create(**validated_data)
