# Generated by Django 4.1.6 on 2023-07-24 09:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoiceitem',
            name='sub_total',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]