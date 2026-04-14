"""Config module."""
from django.apps import AppConfig


class TenantsConfig(AppConfig):
    """Config for tenant app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "tenants"
