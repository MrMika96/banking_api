"""Config module."""
from django.apps import AppConfig


class ImagesConfig(AppConfig):
    """Config for image app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "images"
