# Generated by Django 3.2.15 on 2023-01-13 17:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("bookings", "0016_auto_20221111_1212"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="bookings",
            options={"verbose_name_plural": "Bookings"},
        ),
        migrations.AlterModelOptions(
            name="products",
            options={"verbose_name_plural": "Products"},
        ),
        migrations.AlterModelOptions(
            name="receiverdetails",
            options={"verbose_name_plural": "Receiver Details"},
        ),
    ]
