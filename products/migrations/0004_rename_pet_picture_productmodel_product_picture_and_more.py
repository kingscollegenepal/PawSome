# Generated by Django 4.2.4 on 2023-08-13 03:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0003_rename_pet_brand_productmodel_product_brand"),
    ]

    operations = [
        migrations.RenameField(
            model_name="productmodel",
            old_name="pet_picture",
            new_name="product_picture",
        ),
        migrations.AlterModelTable(
            name="productmodel",
            table="products_productmodel",
        ),
    ]
