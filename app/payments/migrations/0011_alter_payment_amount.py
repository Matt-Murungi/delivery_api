# Generated by Django 3.2.15 on 2022-11-21 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0010_auto_20221117_2030"),
    ]

    operations = [
        migrations.AlterField(
            model_name="payment",
            name="amount",
            field=models.FloatField(default=0.0),
        ),
    ]
