"""Config module."""
from django.apps import AppConfig


class BanksConfig(AppConfig):
    """Config for bank app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "banks"
