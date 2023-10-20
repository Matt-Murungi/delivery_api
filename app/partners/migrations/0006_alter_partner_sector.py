# Generated by Django 3.2.15 on 2023-04-24 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0005_alter_partner_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='partner',
            name='sector',
            field=models.CharField(choices=[('1', 'Fashion'), ('2', 'Bakery'), ('3', 'Pharmacy'), ('4', 'Supermarket'), ('5', 'Manufacturing'), ('6', 'Restaurants')], default=1, max_length=1),
        ),
    ]
