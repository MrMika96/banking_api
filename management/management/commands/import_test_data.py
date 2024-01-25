from django.apps import apps
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db.transaction import atomic


class Command(BaseCommand):
    help = "Adding test data to the database"

    @atomic
    def handle(self, *args, **options):
        for app_name in apps.get_app_configs():
            try:
                call_command(
                    "loaddata",
                    f"""{str(app_name.verbose_name).lower()}/fixtures/initial_data.json""",
                )
            except CommandError:
                continue
        self.stdout.write(self.style.SUCCESS("Complete!"))
