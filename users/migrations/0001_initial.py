# Generated by Django 4.1.5 on 2023-01-16 08:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
            ],
            options={
                "db_table": "users",
                "ordering": ["id"],
            },
        ),
        migrations.CreateModel(
            name="Profile",
            fields=[
                ("last_name", models.CharField(blank=True, max_length=64)),
                ("first_name", models.CharField(blank=True, max_length=64)),
                ("middle_name", models.CharField(blank=True, max_length=64)),
                ("phone", models.CharField(blank=True, max_length=64)),
                ("birth_date", models.DateField(blank=True, null=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        related_name="profile",
                        serialize=False,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "profiles",
                "ordering": ["last_name"],
            },
        ),
        migrations.AddIndex(
            model_name="profile",
            index=models.Index(
                fields=["first_name"], name="profiles_first_n_bd5776_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="profile",
            index=models.Index(
                fields=["middle_name"], name="profiles_middle__423760_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="profile",
            index=models.Index(
                fields=["last_name"], name="profiles_last_na_284a31_idx"
            ),
        ),
    ]
