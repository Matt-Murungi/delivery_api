# Generated by Django 3.2.15 on 2023-01-16 12:50

from django.conf import settings
import django.core.validators
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
                (
                    "email",
                    models.EmailField(
                        max_length=255, unique=True, verbose_name="email address"
                    ),
                ),
                ("first_name", models.CharField(blank=True, max_length=207, null=True)),
                ("last_name", models.CharField(blank=True, max_length=207, null=True)),
                (
                    "image",
                    models.ImageField(default="users.png", upload_to="users/%Y/%m"),
                ),
                ("phonenumber", models.CharField(max_length=17, unique=True)),
                ("is_admin", models.BooleanField(default=False)),
                ("is_driver", models.BooleanField(default=False)),
                ("is_superuser", models.BooleanField(default=False)),
                ("is_confirmed", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("date_joined", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Profile",
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
                ("is_approved", models.BooleanField(default=False)),
                (
                    "driving_license",
                    models.FileField(
                        blank=True, null=True, upload_to="driving_license/%Y/%m"
                    ),
                ),
                (
                    "insurance",
                    models.FileField(
                        blank=True, null=True, upload_to="insurance/%Y/%m"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_owner",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="OTP",
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
                (
                    "phonenumber",
                    models.CharField(
                        max_length=17,
                        null=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Phone number must be entered in the format +254700000000. Up to 14 digits allowed.",
                                regex="^\\+?1?\\d{9,10}$",
                            )
                        ],
                    ),
                ),
                ("otp", models.CharField(blank=True, max_length=9, null=True)),
                (
                    "count",
                    models.IntegerField(default=0, help_text="Number of otp_sent"),
                ),
                (
                    "is_validated",
                    models.BooleanField(
                        default=False,
                        help_text="If it is true, that means user have validate otp correctly in second API",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="DriverLocation",
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
                ("latitude", models.FloatField(blank=True, null=True)),
                ("longitude", models.FloatField(blank=True, null=True)),
                (
                    "formated_address",
                    models.CharField(blank=True, max_length=207, null=True),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]