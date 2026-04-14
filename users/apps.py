"""Config module."""
from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Config for user app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "users"
