"""Module with serializers for bank app."""
from rest_framework import serializers

from banks.models import Bank, PaymentSystem


class BanksSerializer(serializers.ModelSerializer):
    """Serializer for banks."""

    class Meta:
        """Meta."""

        model = Bank
        fields = ["id", "name", "bank_type", "number"]


class DetailedBankSerializer(serializers.ModelSerializer):
    """Detail serializer for banks."""

    number_of_clients = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        """Meta."""

        model = Bank
        fields = ["id", "name", "bank_type", "number", "number_of_clients"]


class PaymentSystemSerializer(serializers.ModelSerializer):
    """Payment system serializer."""

    class Meta:
        """Meta."""

        model = PaymentSystem
        fields = ["id", "name", "number"]
