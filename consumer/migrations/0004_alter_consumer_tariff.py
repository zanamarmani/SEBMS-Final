# Generated by Django 5.1 on 2024-10-02 03:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SDO', '0001_initial'),
        ('consumer', '0003_alter_consumer_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consumer',
            name='tariff',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='SDO.tariff'),
        ),
    ]
