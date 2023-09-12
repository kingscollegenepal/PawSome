from django.contrib import admin
from store.models import Product, Cart, CartItem, Order, Review, Rating

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'subcategory']
    list_filter = ['category', 'subcategory']

# Register your models here.
admin.site.register(Product, ProductAdmin)
admin.site.register([Cart, CartItem, Order, Review, Rating])
