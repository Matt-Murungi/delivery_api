# Generated by Django 3.2.15 on 2022-12-06 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0012_alter_driverbankinginformation_account_number"),
    ]

    operations = [
        migrations.AlterField(
            model_name="requestearnings",
            name="status",
            field=models.CharField(
                choices=[(1, "Pending"), (2, "Paid")], default="1", max_length=1
            ),
        ),
    ]
