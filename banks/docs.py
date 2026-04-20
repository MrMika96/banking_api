"""Module with documentation for banks."""
from drf_spectacular.utils import extend_schema

BANK_TAG = "Banks"


def get_bank_view_set_docs() -> dict:
    """Return documentation for bank view set."""
    return {
        "list": extend_schema(
            tags=[BANK_TAG],
            description="Get the full list of banks available in API",
            summary="Get list of banks"
        ),
        "retrieve": extend_schema(
            tags=[BANK_TAG],
            description="Get a specific bank by it ID",
            summary="Get a single bank"
        ),
        "create": extend_schema(
            tags=[BANK_TAG],
            description="Create completely new bank object in API",
            summary="Create a bank"
        ),
        "update": extend_schema(
            tags=[BANK_TAG],
            description="Update a specific bank by it's ID",
            summary="Update a bank"
        ),
        "destroy": extend_schema(
            tags=[BANK_TAG],
            description="Remove bank instance from system by it's ID",
            summary="Delete a bank"
        )
    }


def get_payment_system_docs() -> dict:
    """Return documentation for payment system view set."""
    return {
        "list": extend_schema(
            tags=[BANK_TAG],
            description="Get the full list of "
                        "payment systems available in API",
            summary="Get list of payment systems"
        ),
        "retrieve": extend_schema(
            tags=[BANK_TAG],
            description="Get a specific payment system by it's ID",
            summary="Get a single payment system"
        ),
        "create": extend_schema(
            tags=[BANK_TAG],
            description="Create completely new payment system object in API",
            summary="Create a payment system"
        ),
        "update": extend_schema(
            tags=[BANK_TAG],
            description="Update a specific payment system by it's ID",
            summary="Update a payment system"
        )
    }
