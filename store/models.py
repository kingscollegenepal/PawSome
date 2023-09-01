from django.db import models
from django.contrib.auth.models import User
import uuid

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=50)
    price = models.IntegerField()
    picture = models.ImageField(upload_to="img", default="")

    def __str__(self):
        return self.name

class Cart(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)
    
    @property
    def total_price(self):
        cartitems = self.cartitems.all()
        total = sum([item.price for item in cartitems])
        return total
    
    @property
    def num_of_items(self):
        cartitems = self.cartitems.all()
        quantity = sum([item.quantity for item in cartitems])
        return quantity

class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='items')
    cart = models.ForeignKey(Cart, on_delete= models.CASCADE, related_name='cartitems')
    quantity = models.IntegerField(default=0)

    def __str__ (self):
        return self.product.name
    
    @property
    def price(self):
        new_price = self.product.price * self.quantity
        return new_price

ORDER_STATUS = (
    ("Order Received", "Order Received"),
    ("Order Processing", "Order Processing"),
    ("On the way", "On the way"),
    ("Order Completed", "Order Completed"),
    ("Order Canceled", "Order Canceled"),
)

METHOD = (
    ("Cash On Delivery", "Cash On Delivery"),
    ("Khalti", "Khalti"),
)

class Order(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE)
    ordered_by = models.CharField(max_length=200)
    shipping_address = models.CharField(max_length=200)
    mobile = models.CharField(max_length=10)
    email = models.EmailField(null=True,blank=True)
    subtotal = models.PositiveIntegerField(default=False, blank=True)
    discount = models.PositiveIntegerField(default=False, blank=True)
    total = models.PositiveIntegerField(default=False, blank=True)
    order_status = models.CharField(max_length=50, choices=ORDER_STATUS)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(
        max_length=20, choices=METHOD, default="Cash On Delivery")
    payment_completed = models.BooleanField(
        default=False, null=True, blank=True)
    
    def __str__(self):
        return "Order: " + str(self.id)
    
