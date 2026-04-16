"""Module with documentation for credit cards."""
from drf_spectacular.utils import extend_schema

CREDIT_CARDS_TAG = "Credit cards"


def get_credit_card_docs() -> dict:
    """Return documentation for credit card view set."""
    return {
        "list": extend_schema(
            description="Get list of every credit card "
                        "available to authenticated user",
            summary="Get list of credit cards"
        ),
        "retrieve": extend_schema(
            description="Get specific credit card "
                        "available to authenticated user",
            summary="Get credit card by ID"
        ),
        "create": extend_schema(
            description="Create new credit card, what will be "
                        "added to authenticated users relation",
            summary="Create a credit card"
        ),
        "partial_update": extend_schema(
            description="Update authenticated users credit card data",
            summary="Update credit card info"
        ),
        "destroy": extend_schema(
            description="Delete authenticated users credit card",
            summary="Delete credit card"
        )
    }


def get_credit_card_transfer_docs() -> dict:
    """Return documentation for credit card transfer view."""
    return {
        "post": extend_schema(
            description="Transfer money from one credit card to another",
            summary="Transfer money"
        )
    }


def get_credit_card_currency_change_docs() -> dict:
    """Return documentation for credit card currency change view."""
    return {
        "put": extend_schema(
            description="Change currency of a credit card what "
                        "is owned by authenticated user",
            summary="Change credit card currency"
        )
    }


def get_credit_card_balance_replenishment_docs() -> dict:
    """Return documentation for credit card balance replenishment view."""
    return {
        "put": extend_schema(
            description="Replenish balance of a users credit card",
            summary="Replenish balance"
        )
    }
