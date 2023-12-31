# Generated by Django 3.2.15 on 2022-10-20 16:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("bookings", "0003_auto_20221018_1046"),
    ]

    operations = [
        migrations.AlterField(
            model_name="receiverdetails",
            name="booking",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="boooking_receiver",
                to="bookings.bookings",
            ),
        ),
    ]
