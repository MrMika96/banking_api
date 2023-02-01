from rest_framework import serializers

from banks.models import Bank, PaymentSystem


class BanksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = [
            'id', 'name', 'type', 'number'
        ]


class DetailedBankSerializer(serializers.ModelSerializer):
    number_of_clients = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Bank
        fields = [
            'id', 'name', 'type',
            'number', 'number_of_clients'
        ]


class PaymentSystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentSystem
        fields = [
            'id', 'name', 'number'
        ]
