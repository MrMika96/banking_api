from django.core.management.base import BaseCommand, CommandError
from django.db.transaction import atomic

from tenants.models import Tenant, Domain


class Command(BaseCommand):
    help = "Creates new tenants for database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--schema_name",
            default="public",
            type=str,
            help="Name of a tenant schema in your database"
        )
        parser.add_argument(
            "--name",
            default="Public Tenant",
            type=str,
            help="Name of a tenant we are creating"
        )
        parser.add_argument(
            "--domain",
            default="localhost",
            type=str,
            help="The domain of our tenant"
        )

    @atomic
    def handle(self, *args, **options):
        if not Tenant.objects.filter(schema_name=options["schema_name"]).exists():
            tenant = Tenant(
                schema_name=options["schema_name"],
                name=options["name"]
            )
            tenant.full_clean()
            tenant.save()
        else:
            raise CommandError(
                f"Tenant {options['schema_name']} already exists"
            )

        if not Domain.objects.filter(domain=options["domain"]).exists():
            domain = Domain()
            domain.domain = options["domain"]
            domain.tenant = tenant
            domain.is_primary = True
            domain.full_clean()
            domain.save()
        else:
            raise CommandError(f"Domain {options['domain']} already exists")
        self.stdout.write(
            self.style.SUCCESS(
                f"Tenant {options['schema_name']} successfully created"
            )
        )
