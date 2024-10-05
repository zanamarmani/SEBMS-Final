# Generated by Django 5.1 on 2024-10-04 02:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SDO', '0002_alter_tariff_tariff_type'),
        ('consumer', '0005_alter_consumer_tariff'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consumer',
            name='tariff',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='SDO.tariff'),
        ),
    ]
