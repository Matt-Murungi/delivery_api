# Generated by Django 3.2.15 on 2023-04-27 09:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0007_remove_partner_owner'),
        ('users', '0002_user_partner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(default='', max_length=207),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='user',
            name='partner',
            field=models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='partners.partner'),
        ),
    ]