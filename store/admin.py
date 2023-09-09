from django.contrib import admin
from store.models import *

# Register your models here.
admin.site.register([Product, Cart, CartItem, Order])

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category']
    list_filter = ['category']