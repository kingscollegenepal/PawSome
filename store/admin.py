from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Sum
from django import forms
from django.urls import path
from django.http import HttpResponse
from django.db.models import Count, Case, When, IntegerField
from datetime import timedelta
from django.shortcuts import render, redirect
from store.models import Product, Cart, CartItem, Order, Review, Rating, Vendor, Customer, SalesRecord
import datetime
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.db.models import Sum
from django.db import models
from django.db.models import Subquery, OuterRef
from calendar import monthrange


class VendorProductListFilter(admin.SimpleListFilter):
    title = _('product')
    parameter_name = 'product'

    def lookups(self, request, model_admin):
        if request.user.is_superuser:
            products = Product.objects.all()
        else:
            vendor = Vendor.objects.get(user=request.user)
            products = Product.objects.filter(vendor=vendor)
        return [(product.id, product.name) for product in products]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(product__id=self.value())
        else:
            return queryset
    
class VendorCategoryListFilter(admin.SimpleListFilter):
    title = _('category')
    parameter_name = 'category'

    def lookups(self, request, model_admin):
        if request.user.is_superuser:
            return Product.CATEGORY_CHOICES

        vendor = Vendor.objects.get(user=request.user)
        categories = set(Product.objects.filter(vendor=vendor).values_list('category', flat=True))
        return [(category, category) for category in categories]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(category=self.value())
        return queryset


class VendorSubcategoryListFilter(admin.SimpleListFilter):
    title = _('subcategory')
    parameter_name = 'subcategory'

    def lookups(self, request, model_admin):
        if request.user.is_superuser:
            return Product.SUBCATEGORY_CHOICES

        vendor = Vendor.objects.get(user=request.user)
        subcategories = set(Product.objects.filter(vendor=vendor).values_list('subcategory', flat=True))
        return [(subcategory, subcategory) for subcategory in subcategories]


    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(subcategory=self.value())
        return queryset

class OrderCountFilter(admin.SimpleListFilter):
    title = 'Order Count'
    parameter_name = 'order_count'

    def lookups(self, request, model_admin):
        return (
            ('ascending', 'Ascending'),
            ('descending', 'Descending'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'ascending':
            return queryset.order_by('order_count')
        if self.value() == 'descending':
            return queryset.order_by('-order_count')

class SalesDateListFilter(admin.SimpleListFilter):
    title = _('Sale Date')
    parameter_name = 'sale_date'

    def lookups(self, request, model_admin):
        return (
            ('daily_asc', _('Daily Ascending')),
            ('daily_desc', _('Daily Descending')),
            ('weekly_asc', _('Weekly Ascending')),
            ('weekly_desc', _('Weekly Descending')),
            ('monthly_asc', _('Monthly Ascending')),
            ('monthly_desc', _('Monthly Descending')),
            ('yearly_asc', _('Yearly Ascending')),
            ('yearly_desc', _('Yearly Descending')),
        )

    def queryset(self, request, queryset):
        today = timezone.now()
        ordering = None
        filter_value = self.value()
        filter_date = None  # Initialize filter_date here

        if not filter_value:  # If filter is not set, return the original queryset.
            return queryset

        # Filtering based on selected timeframe
        if 'yearly' in filter_value:
            start_year = today.replace(month=1, day=1)
            end_year = today.replace(month=12, day=31)
            filter_date = (start_year.date(), end_year.date())
        elif 'monthly' in filter_value:
            start_month = today.replace(day=1)
            _, last_day = monthrange(today.year, today.month)
            end_month = today.replace(day=last_day)
            filter_date = (start_month.date(), end_month.date())
        elif 'weekly' in filter_value:
            start_week = today - timedelta(days=today.weekday())
            end_week = start_week + timedelta(days=6)
            filter_date = (start_week.date(), end_week.date())
        elif 'daily' in filter_value:
            filter_date = today.date()

        # Ordering
        if '_desc' in filter_value:
            ordering = '-quantity_sold'
        elif '_asc' in filter_value:
            ordering = 'quantity_sold'

        # Apply filtering and ordering to the queryset
        if 'daily' in filter_value:
            return queryset.filter(sale_date=filter_date).order_by(ordering)
        elif filter_date:
            return queryset.filter(sale_date__range=filter_date).order_by(ordering)
        else:
            return queryset.order_by(ordering)
        
class VendorCustomerListFilter(admin.SimpleListFilter):
    title = _('customer')
    parameter_name = 'customer'

    def lookups(self, request, model_admin):
        # If the user is a superuser, return all customers
        if request.user.is_superuser:
            return Customer.objects.all().values_list('id', 'name')

        # If the user is a vendor, return customers who have placed orders with products from this vendor
        vendor = Vendor.objects.get(user=request.user)
        customers = Customer.objects.filter(order__order_items__product__vendor=vendor).distinct()
        return customers.values_list('id', 'name')

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(customer__id=self.value())
        return queryset
    

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock_quantity', 'category', 'subcategory']
    search_fields = ['name', 'category', 'subcategory']
    list_filter = [VendorCategoryListFilter, VendorSubcategoryListFilter]  # Updated this line

    
    def get_queryset(self, request):
        
        qs = super().get_queryset(request)
        qs = qs.annotate(order_count=Sum('items__quantity'))
        if request.user.is_superuser:
            return qs
        return qs.filter(vendor__user=request.user)
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.vendor = Vendor.objects.get(user=request.user)
        super().save_model(request, obj, form, change)
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        disabled_fields = set()  # type: Set[str]

        if not is_superuser:
            disabled_fields |= {
                'vendor',
            }

        for f in disabled_fields:
            if f in form.base_fields:
                form.base_fields[f].disabled = True

        return form
    
    def order_count(self, obj):
        return obj.order_count
    order_count.admin_order_field = 'order_count'
    order_count.short_description = 'Total Orders'

class RatingAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'value',)
    search_fields = ['product__name', 'user__username', 'value',]
    list_filter = (VendorProductListFilter,'value',)  
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        vendor = Vendor.objects.get(user=request.user)
        return qs.filter(product__vendor=vendor)

    ordering = ['value']

# Check if the model is already registered
if admin.site.is_registered(Rating):
    # Unregister the model
    admin.site.unregister(Rating)

admin.site.register(Rating, RatingAdmin)


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'review_text', 'created_at',)
    search_fields = ['product__name', 'user__username']
    list_filter = (VendorProductListFilter,)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        vendor = Vendor.objects.get(user=request.user)
        return qs.filter(product__vendor=vendor)

admin.site.register(Review, ReviewAdmin)
    
    
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'shipping_address', 'mobile', 'email', 'payment_method', 'order_status', 'customer','created_at')
    search_fields = ['ordered_by', 'email', 'payment_method', 'order_status', 'vendor__user__username', 'customer__name']
    list_filter = ('payment_method', 'order_status', 'created_at', VendorCustomerListFilter,)
    readonly_fields = ['display_items']

    def change_view(self, request, object_id, form_url='', extra_context=None):
        self.request = request
        return super(OrderAdmin, self).change_view(
            request, object_id, form_url='', extra_context=None,
        )

    def display_items(self, obj):
        # Check if the current user is a superuser
        if self.request.user.is_superuser:
            # If superuser, return all items in the order
            return obj.display_items()

        # If the user is a vendor, filter the items
        vendor = Vendor.objects.get(user=self.request.user)
        
        # Assuming `obj` is an Order and has a related set of items.
        vendor_related_items = obj.order_items.filter(product__vendor=vendor)

        # Convert the vendor-related items to a string representation or to an HTML format as needed
        display_text = ", ".join(str(item) for item in vendor_related_items)
        return display_text
    
    display_items.short_description = 'Items'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        
        # If superuser, return all orders
        if request.user.is_superuser:
            print("User is a superuser")
            return qs

        # If vendor, filter orders containing products belonging to this vendor
        try:
            vendor = Vendor.objects.get(user=request.user)
            print(f"Vendor: {vendor}")
        except Vendor.DoesNotExist:
            print("User is not related to any vendor")
            return qs.none()  # If the user isn't related to any vendor, return no records

        # Return only orders containing products from the current vendor
        vendor_orders = qs.filter(order_items__product__vendor=vendor).distinct()
        print(f"Total vendor orders: {vendor_orders.count()}")
        return vendor_orders



    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if request.user.is_superuser:
            return readonly_fields
        return readonly_fields + ['payment_method', 'payment_completed', 'total', 'discount','cart','vendor','id', 'ordered_by', 'shipping_address','mobile','email','customer']
    
admin.site.register(Order, OrderAdmin)


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'shipping_address', 'mobile', 'email', 'order_count')
    search_fields = ['name', 'email', 'mobile']

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # If superuser, return all customers with overall order count
        if request.user.is_superuser:
            return qs.annotate(order_count=Count('order'))

        # If vendor, annotate each customer with the count of orders they made for this vendor's products
        vendor = Vendor.objects.get(user=request.user)
        
        qs = qs.annotate(
            order_count=Count(
                'order', 
                filter=models.Q(order__vendor=vendor)
            )
        )

        # Filter the queryset to only include customers with an order count greater than zero
        return qs.filter(order_count__gt=0)


    def order_count(self, obj):
        return obj.order_count

    order_count.admin_order_field = '_order_count'  # Allows column order sorting
    order_count.short_description = 'Total Orders'

admin.site.register(Customer, CustomerAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register([Cart, CartItem])


class SalesRecordAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity_sold','individual_product_cost','cost_based_on_quantity', 'sale_date']
    search_fields = ['product__name']
    list_filter = (SalesDateListFilter,VendorProductListFilter)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            try:
                vendor = Vendor.objects.get(user=request.user)
                return qs.filter(vendor=vendor)
            except Vendor.DoesNotExist:
                return qs.none()  # If the user isn't related to any vendor, return no records


    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "product":
            if request.user.is_superuser:
                kwargs["queryset"] = Product.objects.all()
            else:
                vendor = Vendor.objects.get(user=request.user)
                kwargs["queryset"] = Product.objects.filter(vendor=vendor)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []  # no fields should be read-only for admin
        else:
            return ["product", "vendor", "quantity_sold"]
    
    def update_sales_record(self, order):
        for item in order.order_items.all():
            product = item.product
            vendor = product.vendor
            quantity = item.quantity

            # Assuming Product model has a 'cost' field that represents the cost of the product
            individual_cost = product.cost  

            # Get or create the SalesRecord
            sales_record, created = SalesRecord.objects.get_or_create(
                product=product, 
                vendor=vendor,
                defaults={
                    'quantity_sold': quantity,
                    'individual_product_cost': individual_cost,
                    'cost_based_on_quantity': individual_cost * quantity
                }
            )

            # If the SalesRecord already existed, increment the quantity sold and update the cost
            if not created:
                sales_record.quantity_sold += quantity
                sales_record.cost_based_on_quantity += individual_cost * quantity
                sales_record.save()



admin.site.register(SalesRecord, SalesRecordAdmin)



