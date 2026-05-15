"""Module with documentation for credit cards."""
from drf_spectacular.utils import extend_schema, OpenApiResponse

CREDIT_CARDS_TAG = "Credit cards"


def get_credit_card_docs() -> dict:
    """Return documentation for credit card view set."""
    return {
        "list": extend_schema(
            tags=[CREDIT_CARDS_TAG],
            description="Get list of every credit card "
                        "available to authenticated user",
            summary="Get list of credit cards"
        ),
        "retrieve": extend_schema(
            tags=[CREDIT_CARDS_TAG],
            description="Get specific credit card "
                        "available to authenticated user",
            summary="Get credit card by ID"
        ),
        "create": extend_schema(
            tags=[CREDIT_CARDS_TAG],
            description="Create new credit card, what will be "
                        "added to authenticated users relation",
            summary="Create a credit card"
        ),
        "partial_update": extend_schema(
            tags=[CREDIT_CARDS_TAG],
            description="Update authenticated users credit card data",
            summary="Update credit card info"
        ),
        "destroy": extend_schema(
            tags=[CREDIT_CARDS_TAG],
            description="Delete authenticated users credit card",
            summary="Delete credit card"
        )
    }


def get_credit_card_transfer_docs() -> dict:
    """Return documentation for credit card transfer view."""
    return {
        "post": extend_schema(
            tags=[CREDIT_CARDS_TAG],
            description="Transfer money from one credit card to another",
            summary="Transfer money",
            responses={
                204: OpenApiResponse(response=None)
            }
        )
    }


def get_credit_card_currency_change_docs() -> dict:
    """Return documentation for credit card currency change view."""
    return {
        "put": extend_schema(
            tags=[CREDIT_CARDS_TAG],
            description="Change currency of a credit card what "
                        "is owned by authenticated user",
            summary="Change credit card currency"
        )
    }


def get_credit_card_balance_replenishment_docs() -> dict:
    """Return for credit card balance replenishment view."""
    return {
        "put": extend_schema(
            tags=[CREDIT_CARDS_TAG],
            description="Replenish balance of a users credit card",
            summary="Replenish balance"
        )
    }
