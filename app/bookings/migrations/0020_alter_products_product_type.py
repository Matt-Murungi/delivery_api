# Generated by Django 3.2.15 on 2023-04-03 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0019_auto_20230330_1218'),
    ]

    operations = [
        migrations.AlterField(
            model_name='products',
            name='product_type',
            field=models.CharField(choices=[('1', 'ELectronics'), ('2', 'Gift'), ('3', 'Document'), ('4', 'Package'), ('5', 'Food'), ('6', 'Other')], default=1, max_length=1),
        ),
    ]
