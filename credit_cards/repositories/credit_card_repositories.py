"""repositories module for credit cards app."""

from collections import OrderedDict
from datetime import timedelta

from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from django.utils import timezone

from credit_cards.models import CreditCard


class CreditCardRepository:
    """Repository for working with credit card instances."""

    model = CreditCard

    def create_credit_card(self, credit_card_data: OrderedDict) -> CreditCard:
        """Create credit card."""
        credit_card_data["number"] = self.model.card_number_generator(
            credit_card_data["bank"].number,
            credit_card_data["payment_system"].number
        )
        credit_card_data["cvv"] = self.model.cvv_generator()
        credit_card_data["expiration_date"] = (
                timezone.now().date() + timedelta(days=1825)
        )
        credit_card = self.model(**credit_card_data)
        credit_card.full_clean()
        credit_card.save()
        return credit_card

    def update_credit_card_currency(
        self,
        credit_card_instance: CreditCard,
        currency_data: OrderedDict
    ) -> CreditCard:
        """Update credit card currency."""
        balance = self.model.change_balance_by_currency(
            credit_card_instance.currency,
            currency_data["currency"],
            credit_card_instance.balance
        )
        credit_card_instance.currency = currency_data["currency"]
        credit_card_instance.balance = balance
        credit_card_instance.full_clean()
        credit_card_instance.save(update_fields=["currency", "balance"])
        return credit_card_instance

    def replenish_credit_card_balance(
        self,
        credit_card_instance: CreditCard,
        credit_card_data: OrderedDict
    ) -> CreditCard:
        """Update balance of a credit card."""
        credit_card_instance.balance = (
                credit_card_instance.balance + credit_card_data["balance"]
        )
        credit_card_instance.full_clean()
        credit_card_instance.save(update_fields=["balance"])
        return credit_card_instance

    def get_credit_card_by_number(self, card_number: int) -> CreditCard:
        """Return credit card instance by it`s number."""
        return get_object_or_404(self.model, number=card_number)

    @atomic
    def transfer_money_from_one_card_to_another(
        self,
        to_card: CreditCard,
        from_card: CreditCard,
        operation_data: OrderedDict
    ):
        """Transfer money from one card to another."""
        from_card.balance = from_card.balance - operation_data["sum_of_money"]
        from_card.full_clean()
        from_card.save(update_fields=["balance"])
        sum_of_money = self.model.change_balance_by_currency(
            from_card.currency,
            to_card.currency,
            operation_data["sum_of_money"]
        ) if to_card.currency != from_card.currency else operation_data[
            "sum_of_money"
        ]
        to_card.balance = to_card.balance + sum_of_money
        to_card.full_clean()
        to_card.save(update_fields=["balance"])
        return to_card
