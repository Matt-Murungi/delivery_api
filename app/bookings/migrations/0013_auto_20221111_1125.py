# Generated by Django 3.2.15 on 2022-11-11 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bookings", "0012_auto_20221111_1123"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bookings",
            name="formated_address",
            field=models.CharField(max_length=207),
        ),
        migrations.AlterField(
            model_name="receiverdetails",
            name="formated_address",
            field=models.CharField(max_length=207),
        ),
    ]
