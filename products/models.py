from django.db import models

# Create your models here.
class ProductModel(models.Model):
    product_name = models.CharField()
    product_price = models.IntegerField()
    pet_type = models.CharField(max_length = 20)
    product_brand = models.CharField(max_length = 20)
    pet_picture = models.ImageField()

    class Meta:
        db_table = "products_productmodel"



