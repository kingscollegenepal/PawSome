from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Sum
from django import forms
from store.models import Product, Cart, CartItem, Order, Review, Rating, Vendor, Customer


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

    
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'subcategory']
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
    
    
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'shipping_address', 'mobile', 'email', 'payment_method', 'order_status', 'customer')
    search_fields = ['ordered_by', 'email', 'payment_method', 'order_status', 'vendor__user__username', 'customer__name']
    list_filter = ('payment_method', 'order_status', VendorCustomerListFilter,)
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
                return qs

            # If vendor, filter orders containing products belonging to this vendor
            vendor = Vendor.objects.get(user=request.user)
            return qs.filter(order_items__product__vendor=vendor).distinct()

    
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if request.user.is_superuser:
            return readonly_fields
        return readonly_fields + ['payment_method', 'payment_completed', 'total', 'discount','cart','vendor','id', 'ordered_by', 'shipping_address','mobile','email','customer']
    
admin.site.register(Order, OrderAdmin)


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

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'shipping_address', 'mobile', 'email', 'order_count')
    search_fields = ['name', 'email', 'mobile']
    list_filter = (OrderCountFilter,)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(order_count=Count('order'))

        # If superuser, return all customers
        if request.user.is_superuser:
            return qs

        # If vendor, filter customers who have placed orders containing products from this vendor
        vendor = Vendor.objects.get(user=request.user)
        return qs.filter(order__order_items__product__vendor=vendor).distinct()

    def order_count(self, obj):
        return obj.order_count

    order_count.admin_order_field = 'order_count'  # Allows column order sorting
    order_count.short_description = 'Total Orders'


admin.site.register(Customer, CustomerAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register([Cart, CartItem])
admin.site.register(Vendor)
