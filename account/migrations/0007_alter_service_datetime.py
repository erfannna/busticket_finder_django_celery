# Generated by Django 5.0.6 on 2024-05-16 18:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0006_alter_service_datetime'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='datetime',
            field=models.DateTimeField(blank=True),
        ),
    ]
