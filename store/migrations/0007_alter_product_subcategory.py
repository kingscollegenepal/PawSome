# Generated by Django 4.2.4 on 2023-09-10 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0006_product_subcategory_alter_order_payment_method_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="subcategory",
            field=models.CharField(
                choices=[
                    ("Pens", "Pens"),
                    ("Beds", "Beds"),
                    ("Crates", "Crates"),
                    ("Gates", "Gates"),
                    ("Cameras", "Cameras"),
                    ("Treats", "Treats"),
                    ("Food", "Food"),
                    ("Bowls & Feeders", "Bowls & Feeders"),
                    ("Food Storage & Accessories", "Food Storage & Accessories"),
                    ("Toys", "Toys"),
                    ("Collar & Leashes", "Collar & Leashes"),
                    ("Training Aids", "Training Aids"),
                    ("Vitamins & Supplements", "Vitamins & Supplements"),
                    ("Grooming Supplies", "Grooming Supplies"),
                ],
                default="Pens",
                max_length=30,
            ),
        ),
    ]
