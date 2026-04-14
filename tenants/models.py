"""Module with models for tenant app."""
from django.db import models
from django_tenants.models import DomainMixin, TenantMixin


class Tenant(TenantMixin):
    """Custom tenant model."""

    name = models.CharField(max_length=100)
    created_on = models.DateField(auto_now_add=True)

    auto_create_schema = True

    class Meta:
        """Meta."""

        db_table = "tenants"


class Domain(DomainMixin):
    """Model what stores information about tenant domain."""
