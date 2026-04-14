"""Config module."""
from django.apps import AppConfig


class CreditCardsConfig(AppConfig):
    """Config for credit card app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "credit_cards"
