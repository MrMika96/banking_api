from django.apps import apps
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db.transaction import atomic


class Command(BaseCommand):
    help = 'Add test data in database'

    @atomic
    def handle(self, *args, **options):
        for app_name in apps.get_app_configs():
            try:
                call_command('loaddata', f"""{str(app_name.verbose_name).lower()}/fixtures/initial_data.json""")
            except:
                continue
        self.stdout.write(self.style.SUCCESS("Complete!"))

