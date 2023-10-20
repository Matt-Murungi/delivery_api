# Generated by Django 3.2.15 on 2023-06-09 06:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0023_bookings_partner'),
    ]

    operations = [
        migrations.AddField(
            model_name='products',
            name='name',
            field=models.CharField(blank=True, max_length=207, null=True),
        ),
        migrations.AddField(
            model_name='products',
            name='quantity',
            field=models.CharField(blank=True, max_length=207, null=True),
        ),
        migrations.AlterField(
            model_name='products',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='products'),
        ),
        migrations.AlterField(
            model_name='products',
            name='product_type',
            field=models.CharField(choices=[('1', 'ELectronics'), ('2', 'Gift'), ('3', 'Document'), ('4', 'Package'), ('5', 'Food'), ('6', 'Other')], default=6, max_length=1),
        ),
    ]