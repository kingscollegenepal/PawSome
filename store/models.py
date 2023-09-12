from django.db import models
from django.contrib.auth.models import User
import uuid
from django.db.models import Avg
from django.core.validators import MinValueValidator, MaxValueValidator
   
# Create your models here.
class Product(models.Model):
    CATEGORY_CHOICES = (
        ('Dog', 'Dog'),
        ('Cat', 'Cat'),
    )

    CATEGORY_SIZE_CHOICES = (
        ('Small', 'Small'),
        ('Medium', 'Medium'),
        ('Large', 'Large'),
    )

    SUBCATEGORY_CHOICES = (
        ('Pens', 'Pens'),
        ('Beds', 'Beds'),
        ('Crates', 'Crates'),
        ('Gates', 'Gates'),
        ('Cameras', 'Cameras'),
        ('Treats', 'Treats'),
        ('Food', 'Food'),
        ('Bowls & Feeders', 'Bowls & Feeders'),
        ('Food Storage & Accessories', 'Food Storage & Accessories'),
        ('Toys', 'Toys'),
        ('Collar & Leashes', 'Collar & Leashes'),
        ('Training Aids', 'Training Aids'),
        ('Vitamins & Supplements', 'Vitamins & Supplements'),
        ('Grooming Supplies', 'Grooming Supplies'),
    )
    
    name = models.CharField(max_length=50)
    price = models.IntegerField()
    picture = models.ImageField(upload_to="img", default="")
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='Dog')
    subcategory = models.CharField(max_length=30, choices=SUBCATEGORY_CHOICES, default='Pens')
    size = models.CharField(max_length=10, choices=CATEGORY_SIZE_CHOICES, default='Small')
    description = models.TextField(default="No description available")
    ingredients = models.TextField(default="No ingredients listed")
    direction_to_use = models.TextField(default="No direction to use provided")
    in_stock = models.BooleanField(default=True)

    def average_rating(self):
        total_ratings = self.ratings.all().aggregate(avg=Avg('value'))
        return total_ratings['avg'] or 0

    def __str__(self):
        return self.name
    
class Rating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])  # Assuming a 1-5 rating scale

    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.value}"
    
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    review_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class Cart(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.id}"
    
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
)

class Order(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE)
    ordered_by = models.CharField(max_length=200)
    shipping_address = models.CharField(max_length=200)
    subtotal = models.PositiveIntegerField(default=False, blank=True)
    mobile = models.CharField(max_length=10)
    email = models.EmailField(null=True,blank=True)
    discount = models.PositiveIntegerField(default=False, blank=True)
    total = models.PositiveIntegerField(default=False, blank=True)
    order_status = models.CharField(max_length=50, choices=ORDER_STATUS)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(
        max_length=20, choices=METHOD, default="Khalti")
    payment_completed = models.BooleanField(
        default=False, null=True, blank=True)
    
    def __str__(self):
        return "Order: " + str(self.id)




