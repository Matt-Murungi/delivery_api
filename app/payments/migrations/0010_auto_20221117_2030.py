# Generated by Django 3.2.15 on 2022-11-17 17:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0009_order_is_paid"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="driverbankinginformation",
            name="card_code",
        ),
        migrations.RemoveField(
            model_name="driverbankinginformation",
            name="card_number",
        ),
        migrations.RemoveField(
            model_name="driverbankinginformation",
            name="expiration_date",
        ),
        migrations.AddField(
            model_name="driverbankinginformation",
            name="account_name",
            field=models.CharField(max_length=70, null=True),
        ),
        migrations.AddField(
            model_name="driverbankinginformation",
            name="account_number",
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name="driverbankinginformation",
            name="bank_branch",
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name="driverbankinginformation",
            name="bank_name",
            field=models.CharField(max_length=50, null=True),
        ),
    ]