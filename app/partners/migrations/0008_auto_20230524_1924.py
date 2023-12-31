# Generated by Django 3.2.15 on 2023-05-24 16:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0007_remove_partner_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='partner',
            name='close_at',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='partner',
            name='date_deleted',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='partner',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='partner',
            name='open_at',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='PartnerProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_deleted', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(blank=True, max_length=207, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='partner_products')),
                ('price', models.FloatField(default=0.0)),
                ('partner', models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='partners.partner')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
