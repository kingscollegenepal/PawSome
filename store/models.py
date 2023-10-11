from django.db import models,  transaction
from django.db.models import F
from django.contrib.auth.models import User
import uuid
from django.db.models import Avg
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator
   
# Create your models here.
class Vendor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)

    def __str__(self):
        return self.user.username

class Product(models.Model):
    CATEGORY_CHOICES = (
        ('Dog', 'Dog'),
        ('Cat', 'Cat'),
    )

    SUBCATEGORY_CHOICES = (
        ('D - Beds & Mats', 'D - Beds & Mats'),
        ('D - Healthcare', 'D - Healthcare'),
        ('D - Treats & Chews', 'D - Treats & Chews'),
        ('D - Food', 'D - Food'),
        ('D - Bowls & Feeders', 'D - Bowls & Feeders'),
        ('D - Toys', 'D - Toys'),
        ('D - Collar & Leashes', 'D - Collar & Leashes'),
        ('D - Training Aids', 'D - Training Aids'),
        ('D - Grooming Supplies', 'D - Grooming Supplies'),
        ('D - Crates & Carriers', 'D - Crates & Carriers'),
        ('C - Food', 'C - Food'),
        ('C - Grooming', 'C - Grooming'),
        ('C - Toys', 'C - Toys'),
        ('C - Treats', 'C - Treats'),
        ('C - Transport', 'C - Transport'),
        ('C - Bedding', 'C - Bedding'),
        ('C - Collors & Harness', 'C - Collors & Harness'),
        ('C - Training Aids', 'C - Training Aids'),
        ('C - Bowls', 'C - Bowls'),
        ('C - Kernels', 'C - Kernels'),
    )

    CATEGORY_BRAND_CHOICES = (
        ('Pedigree', 'Pedigree'),
        ('Whiskas', 'Whiskas'),
        ('Royal Canin', 'Royal Canin'),
        ('Drools', 'Drools'),
        ('Farmina', 'Farmina'),
        ('Sheba', 'Sheba'),
        ('Brunos Wild', 'Brunos Wild'),
        ('Catsan', 'Catsan'),
    )
    
    name = models.CharField(max_length=100)
    price = models.IntegerField()
    picture = models.ImageField(upload_to="img", default="")
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='Dog')
    brand = models.CharField(max_length=20, choices=CATEGORY_BRAND_CHOICES, default='Sheba')
    subcategory = models.CharField(max_length=30, choices=SUBCATEGORY_CHOICES, default='Food')
    description = models.TextField(default="No description available")
    ingredients = models.TextField(default="No ingredients listed")
    direction_to_use = models.TextField(default="No direction to use provided")
    in_stock = models.BooleanField(default=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, null=True, blank=True)

    def average_rating(self):
        total_ratings = self.ratings.all().aggregate(avg=Avg('value'))
        return total_ratings['avg'] or 0

    def __str__(self):
        return self.name
    
class Rating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    value = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])  # Assuming a 1-5 rating scale

    def __str__(self):
        return f"{self.product.name} - {self.value}"
    
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    review_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name}"


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
    ("Khalti", "Khalti"),
    ("Cash On Delivery", "Cash On Delivery"),
)

class Customer(models.Model):
    name = models.CharField(max_length=255)
    shipping_address = models.TextField()
    mobile = models.CharField(max_length=10)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name
    
class Order(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE)
    ordered_by = models.CharField(max_length=200)
    shipping_address = models.CharField(max_length=200)
    mobile = models.CharField(max_length=10)
    email = models.EmailField(null=True,blank=True)
    discount = models.PositiveIntegerField(default=0, blank=True)
    total = models.PositiveIntegerField(default=0, blank=True)
    order_status = models.CharField(max_length=50, choices=ORDER_STATUS)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(
        max_length=20, choices=METHOD, default="Khalti")
    payment_completed = models.BooleanField(
        default=False, null=True, blank=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return "Order: " + str(self.id)
    
    def display_items(self):
        return ", ".join([str(item) for item in self.order_items.all()])
    
    def save(self, *args, **kwargs):
            super().save(*args, **kwargs)  # Call the "real" save() method
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
    
class SalesRecord(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    quantity_sold = models.PositiveIntegerField()
    individual_product_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    cost_based_on_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    sale_date = models.DateField(auto_now_add=True)

