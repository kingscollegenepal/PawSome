# Generated by Django 4.2.4 on 2023-09-12 16:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0015_remove_order_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="subtotal",
            field=models.PositiveIntegerField(blank=True, default=False),
        ),
    ]
