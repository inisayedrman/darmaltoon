# Generated by Django 4.1.6 on 2023-07-24 22:57

import dashboard.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_invoiceitem_sub_total'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='password_reset_token',
            field=models.CharField(default=dashboard.models.generate_token, editable=False, max_length=32),
        ),
    ]
