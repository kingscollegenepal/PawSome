# Generated by Django 4.2.4 on 2023-09-12 15:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0011_alter_order_user"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="order",
            name="subtotal",
        ),
        migrations.RemoveField(
            model_name="order",
            name="user",
        ),
    ]
