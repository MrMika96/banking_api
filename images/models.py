"""Module with models for image app."""
import os

from django.conf import settings
from django.db import connection, models

from banking_api.settings import LOCAL


def get_upload_to(instance, filename):
    """Return path where image was uploaded."""
    return os.path.join("images", connection.schema_name, filename)


class Image(models.Model):
    """Model for images in database."""

    image = models.ImageField(upload_to=get_upload_to, null=False, blank=False)

    class Meta:
        """Meta."""

        db_table = "images"

    def __str__(self):
        """Return image filename as string representation."""
        return self.image.name

    @property
    def url(self):
        """Return image url."""
        if LOCAL:
            return (
                f"http://{connection.schema_name}."
                f"{settings.BASE_HOST}{self.image.url}"
            )
        return (
            f"https://{connection.schema_name}."
            f"{settings.BASE_HOST}/api{self.image.url}"
        )
