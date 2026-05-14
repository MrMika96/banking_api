"""Service module for credit card app."""
from collections import OrderedDict
from typing import TYPE_CHECKING

from ..repositories.credit_card_repositories import CreditCardRepository

if TYPE_CHECKING:
    from ..models import CreditCard


def create_credit_card(credit_card_data: OrderedDict) -> "CreditCard":
    """Return newly created credit card object."""
    return CreditCardRepository().create_credit_card(
        credit_card_data=credit_card_data
    )


def update_credit_card_currency(
    credit_card_pk: int, currency_data: OrderedDict
) -> "CreditCard":
    """Return credit card instance after currency update."""
    card_repo = CreditCardRepository()
    credit_card_instance = card_repo.get_credit_card_by_pk(credit_card_pk)
    return card_repo.update_credit_card_currency(
        credit_card_instance, currency_data
    )


def replenish_credit_card_balance(
    credit_card_pk: int, credit_card_data: OrderedDict
) -> "CreditCard":
    """Return credit card instance with replenished balance."""
    card_repo = CreditCardRepository()
    credit_card_instance = card_repo.get_credit_card_by_pk(credit_card_pk)
    return card_repo.replenish_credit_card_balance(
        credit_card_instance, credit_card_data
    )


def transfer_money_from_one_card_to_another(
    money_transaction_data: OrderedDict
):
    """Transfer money from one card to another by their numbers."""
    card_repo = CreditCardRepository()
    non_existent_card_number = 0
    from_card = card_repo.get_credit_card_by_number(
        money_transaction_data.pop(
            "from_card_number",
            non_existent_card_number
        )
    )
    to_card = card_repo.get_credit_card_by_number(
        money_transaction_data.pop(
            "to_card_number",
            non_existent_card_number
        )
    )
    card_repo.transfer_money_from_one_card_to_another(
        to_card, from_card, money_transaction_data
    )
