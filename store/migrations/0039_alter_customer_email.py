# Generated by Django 4.2.4 on 2023-09-30 03:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0038_product_stock_quantity"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customer",
            name="email",
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]
