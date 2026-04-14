"""Module for management command what will fill database with test data."""
import os

from django.apps import apps
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db.transaction import atomic


class Command(BaseCommand):
    """Adding test data to the database."""

    help = "Adding test data to the database" # noqa A003

    @atomic
    def handle(self, *args, **options):
        """Fill database with test data."""
        for app_name in apps.get_app_configs():
            try:
                call_command(
                    "loaddata",
                    os.path.join(
                        app_name.verbose_name.lower(),
                        "fixtures",
                        "initial_data.json"
                    )
                )
            except CommandError:
                continue
        self.stdout.write(self.style.SUCCESS("Complete!"))
