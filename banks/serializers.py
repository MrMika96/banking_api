from rest_framework import serializers

from banks.models import Bank, PaymentSystem


class BanksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = [
            'id', 'name', 'type', 'number'
        ]


class PaymentSystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentSystem
        fields = [
            'id', 'name', 'number'
        ]