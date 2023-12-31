# Generated by Django 3.2.15 on 2022-10-23 13:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("bookings", "0004_alter_receiverdetails_booking"),
    ]

    operations = [
        migrations.AlterField(
            model_name="products",
            name="booking",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="booking_product",
                to="bookings.bookings",
            ),
        ),
    ]
