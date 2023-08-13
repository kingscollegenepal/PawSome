from django.db import models

# Create your models here.
class Product(models.Model):
    product_name = models.CharField()
    product_price = models.IntegerField()
    pet_type = models.CharField(max_length = 20)
    product_brand = models.CharField(max_length = 20)
    product_picture = models.ImageField()

    def __str__(self) -> str:
        return self.product_name

    class Meta:
        db_table = "products_productmodel"



