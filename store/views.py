from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView, CreateView, FormView, DetailView, ListView
from store.models import Product, Cart, CartItem, Order, Review, Rating, OrderItem, Customer, SalesRecord, Vendor
from django.http import JsonResponse
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView, PasswordResetConfirmView
from store.forms import RegistrationForm, LoginForm, UserPasswordResetForm, UserSetPasswordForm, UserPasswordChangeForm
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Avg, Sum
from django.db.models import Count, F
from django.contrib.admin.models import LogEntry
import json
from django.contrib.auth import logout
from django.db.models import OuterRef, Subquery, Count
from django.db.models import F
from django.contrib import messages
from django.db import transaction
from django.urls import reverse_lazy, reverse
from .forms import CheckoutForm, ReviewForm
from django.http import HttpResponseRedirect
import requests
from django.shortcuts import get_object_or_404
from django.db.models.functions import Coalesce
from django.db.models import Q
from django.core.paginator import Paginator
from math import floor
from django.contrib.auth.models import User, auth
from .forms import registrationform
from django.contrib.auth.forms import UserCreationForm
from django.utils.http import url_has_allowed_host_and_scheme
from collections import defaultdict
from django.shortcuts import render
from django.db.models import Sum
from datetime import datetime, timedelta
from datetime import time
from django.utils import timezone



# pylint: disable=missing-function-docstring
def home(request):
    dog_products = Product.objects.filter(category='Dog')
    cat_products = Product.objects.filter(category='Cat')
    
    context = {
        "dog_products": dog_products,
        "cat_products": cat_products
    }
    
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user, completed=False)
        context["cart"] = cart

    return render(request, "home.html", context)

# pylint: disable=missing-function-docstring
def cart(request):

    cart = None
    cartitems = []

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user, completed = False)
        cartitems = cart.cartitems.all()

    context = {"cart":cart, "items":cartitems}
    return render(request, "cart.html", context)

def add_to_cart(request):
    data = json.loads(request.body)
    product_id = data["id"]
    product = Product.objects.get(id=product_id)

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user, completed=False)
        cartitem, created = CartItem.objects.get_or_create(cart=cart, product=product)
        
        if cartitem.quantity < product.stock_quantity:
            cartitem.quantity += 1
            cartitem.save()
            num_of_item = cart.num_of_items
            response_data = {
                "num_of_item": num_of_item,
                "message": "Product added to cart!"
            }
        else:
            messages.error(request, f"Sorry, we do not have more stock of {product.product.name} than currently in your cart.")
        
        return JsonResponse(num_of_item, safe=False)

class ManageCartView(View):
    def get(self, request, *args, **kwargs):
        item_id = self.kwargs["item_id"]
        action = request.GET.get("action")
        item_obj = CartItem.objects.get(id=item_id)
        cart_item = item_obj.cart

        if action == "inc":
            if item_obj.quantity < item_obj.product.stock_quantity:
                item_obj.quantity += 1
                item_obj.save()
            else:
                messages.error(request, f"Sorry, we do not have more stock of {item_obj.product.name} than currently in your cart.")
                return redirect("cart")
        elif action == "dcr":
            item_obj.quantity -= 1
            item_obj.save()
            if item_obj.quantity == 0:
                item_obj.delete()
        elif action == "rmv":
            item_obj.delete()

        return redirect("cart")

class CustomerProfileView(TemplateView):
    template_name = "customerprofile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.request.user
        context['customer'] = customer
        orders = Order.objects.filter(cart__user=customer).order_by("-created_at")
        context['orders']=orders
        return context

class CustomerOrderDetailView(DetailView):
    template_name = "customerorderdetail.html"
    model = Order
    context_object_name = "ord_obj"

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all()

    # Calculate the average rating
    average_rating = product.ratings.aggregate(avg_rating=Avg('value'))['avg_rating']
    if average_rating is None:
        average_rating = 0

    # Calculate the number of reviews
    review_count = reviews.count()

    # Calculate floor rating and check for half star
    floor_rating = floor(average_rating)
    half_star = 0.5 <= average_rating - floor_rating < 1  # Boolean (True if half star is needed, False otherwise)
    
    # Handle the review form submission
    if request.method == "POST" and request.user.is_authenticated:
        form = ReviewForm(request.POST)
        if form.is_valid():
            # Save the review
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()

            # Save the rating for the review
            Rating.objects.create(product=product, user=request.user, value=form.cleaned_data['rating'])

            return HttpResponseRedirect(reverse('product_detail', args=[product_id]))  # Redirect after POST
    else:
        form = ReviewForm()

    context = {
        'product': product,
        'reviews': reviews,
        'form': form,
        'average_rating': average_rating,
        'floor_rating': floor_rating,
        'half_star': half_star,
        'review_count': review_count  # Adding review_count to the context
    }
    return render(request, 'product_detail.html', context)

def cat_rating_product(request):
    products = Product.objects.all()

    for product in products:
        average_rating = product.ratings.aggregate(avg_rating=Avg('value'))['avg_rating']
        if average_rating is None:
            average_rating = 0

        floor_rating = floor(average_rating)
        half_star = 0.5 <= average_rating - floor_rating < 1

        # Attach the ratings to the product object for easier access in the template
        product.average_rating = average_rating
        product.floor_rating = floor_rating
        product.half_star = half_star

    context = {
        'products': products,
        # ... any other context data you need ...
    }
    
    return render(request, 'cat_products.html', context)

def search_results(request):
    query = request.GET.get('query')
    products = Product.objects.filter(
        Q(category__icontains=query) | 
        Q(subcategory__icontains=query)
    )

    for product in products:
        average_rating = product.ratings.aggregate(avg_rating=Avg('value'))['avg_rating']
        if average_rating is None:
            average_rating = 0

        floor_rating = floor(average_rating)
        half_star = 0.5 <= average_rating - floor_rating < 1

        # Attach the ratings to the product object for easier access in the template
        product.average_rating = average_rating
        product.floor_rating = floor_rating
        product.half_star = half_star

    context = {
        'products': products,
        'query': query  # Add this line
    }

    return render(request, 'search_results.html', context)

def dog_products(request):
    """Display all dog products."""
    dog_products = Product.objects.filter(category='Dog')
    subcategories = Product.SUBCATEGORY_CHOICES
    context = {
        "products": dog_products,
        "subcategories": subcategories
    }
    return render(request, "dog_products.html", context)

def dog_beds_and_mats_products(request):
    """Display all dog pen products."""
    beds_and_mats_products = Product.objects.filter(category='Dog', subcategory='D - Beds & Mats')
    context = {"products": beds_and_mats_products}
    return render(request, "dog_beds_and_mats_products.html", context)

def dog_healthcare_products(request):
    """Display all dog pen products."""
    healthcare_products = Product.objects.filter(category='Dog', subcategory='healthcare')
    context = {"products": healthcare_products}
    return render(request, "dog_healthcare_products.html", context)

def dog_treats_and_chews_products(request):
    """Display all dog pen products."""
    treats_and_chews_products = Product.objects.filter(category='Dog', subcategory='Treats and Chews')
    context = {"products": treats_and_chews_products}
    return render(request, "dog_treats_and_chews_products.html", context)

def dog_food_products(request):
    """Display all dog pen products."""
    food_products = Product.objects.filter(category='Dog', subcategory='D - Food')
    context = {"products": food_products}
    return render(request, "dog_food_products.html", context)

def dog_bowls_feeders_products(request):
    """Display all dog pen products."""
    bowls_feeders_products = Product.objects.filter(category='Dog', subcategory='Bowls & Feeders')
    context = {"products": bowls_feeders_products}
    return render(request, "dog_bowls_feeders_products.html", context)

def dog_toys_products(request):
    """Display all dog pen products."""
    toys_products = Product.objects.filter(category='Dog', subcategory='Toys')
    context = {"products": toys_products}
    return render(request, "dog_toys_products.html", context)

def dog_collar_leashes_products(request):
    """Display all dog pen products."""
    collar_leashes_products = Product.objects.filter(category='Dog', subcategory='Collar & Leashes')
    context = {"products": collar_leashes_products}
    return render(request, "dog_collar_leashes_products.html", context)

def dog_training_aids_products(request):
    """Display all dog pen products."""
    training_aids_products = Product.objects.filter(category='Dog', subcategory='Training Aids')
    context = {"products": training_aids_products}
    return render(request, "dog_training_aids_products.html", context)

def dog_grooming_supplies_products(request):
    """Display all dog pen products."""
    grooming_supplies_products = Product.objects.filter(category='Dog', subcategory='Vitamins & Supplements')
    context = {"products": grooming_supplies_products}
    return render(request, "dog_grooming_supplies_products.html", context)

def dog_crates_and_carriers_products(request):
    """Display all dog pen products."""
    crates_and_carriers_products = Product.objects.filter(category='Dog', subcategory='Crates & Carriers')
    context = {"products": crates_and_carriers_products}
    return render(request, "dog_crates_and_carriers_products.html", context)

def cat_products(request):
    """Display all cat products."""
    cat_products = Product.objects.filter(category='Cat')
    for product in cat_products:
        average_rating = product.ratings.aggregate(avg_rating=Avg('value'))['avg_rating']
        if average_rating is None:
            average_rating = 0

        floor_rating = floor(average_rating)
        half_star = 0.5 <= average_rating - floor_rating < 1

        # Attach the ratings to the product object for easier access in the template
        product.average_rating = average_rating
        product.floor_rating = floor_rating
        product.half_star = half_star

    context = {"products": cat_products}
    return render(request, "cat_products.html", context)

def cat_food(request):
    """Display all dog pen products."""
    cat_food = Product.objects.filter(category='Cat', subcategory='C - Food')
    context = {"products": cat_food}
    return render(request, "cat_food.html", context)

def cat_grooming(request):
    """Display all dog pen products."""
    cat_grooming = Product.objects.filter(category='Cat', subcategory='C - Grooming')
    context = {"products": cat_grooming}
    return render(request, "cat_grooming.html", context)

def cat_toys(request):
    """Display all dog pen products."""
    cat_toys = Product.objects.filter(category='Cat', subcategory='C - Toys')
    context = {"products": cat_toys}
    return render(request, "cat_toys.html", context)

def cat_treats(request):
    """Display all dog pen products."""
    cat_treats = Product.objects.filter(category='Cat', subcategory='C - Treats')
    context = {"products": cat_treats}
    return render(request, "cat_treats.html", context)

def cat_transport(request):
    """Display all dog pen products."""
    cat_transport = Product.objects.filter(category='Cat', subcategory='C - Transport')
    context = {"products": cat_transport}
    return render(request, "cat_transport.html", context)

def cat_bedding(request):
    """Display all dog pen products."""
    cat_bedding = Product.objects.filter(category='Cat', subcategory='C - Bedding')
    context = {"products": cat_bedding}
    return render(request, "cat_bedding.html", context)

def cat_collors_harness(request):
    """Display all dog pen products."""
    cat_collors_harness = Product.objects.filter(category='Cat', subcategory='C - Collors & Harness')
    context = {"products": cat_collors_harness}
    return render(request, "cat_collors_harness.html", context)

def cat_kernels(request):
    """Display all dog pen products."""
    cat_kernels = Product.objects.filter(category='Cat', subcategory='C - Kernels')
    context = {"products": cat_kernels}
    return render(request, "cat_kernels.html", context)

def cat_training_aids(request):
    """Display all dog pen products."""
    cat_training_aids = Product.objects.filter(category='Cat', subcategory='C - Training Aids')
    context = {"products": cat_training_aids}
    return render(request, "cat_training_aids.html", context)

def cat_bowls(request):
    """Display all dog pen products."""
    cat_bowls = Product.objects.filter(category='Cat', subcategory='C - Bowls')
    context = {"products": cat_bowls}
    return render(request, "cat_bowls.html", context)

def handle_sales_record(item, vendor, sale_date):
    product_price = item.product.price
    
    record, created = SalesRecord.objects.get_or_create(
        product=item.product,
        vendor=vendor,
        sale_date=sale_date,
        defaults={
            'quantity_sold': 0,
            'individual_product_cost': product_price,
            'cost_based_on_quantity': 0  # Initialized to 0, we'll update it in the next lines
        }
    )
    record.quantity_sold += item.quantity
    record.cost_based_on_quantity += product_price * item.quantity
    record.save()



def handle_order_creation(items, form, cart, vendor, customer):
    order = form.save(commit=False)
    order.total = sum(item.product.price * item.quantity for item in items)
    order.cart = cart
    order.order_status = "Order Received"
    order.vendor = vendor
    order.customer = customer
    order.save()

    for item in items:
        OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)
        item.product.stock_quantity = F('stock_quantity') - item.quantity
        item.product.save(update_fields=['stock_quantity'])

        # Call the handle_sales_record function here
        handle_sales_record(item, vendor, order.created_at.date())  # Assuming you have a date field on the order, adjust if necessary

    return order



def checkout(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse_lazy("home"))

    cart, created = Cart.objects.get_or_create(user=request.user, completed=False)
    cartitems = cart.cartitems.all()
    form = CheckoutForm(request.POST or None)

    # Fetch data for chart
    customers = Customer.objects.annotate(order_count=Count('order'))
    customer_names = [customer.name for customer in customers]
    order_counts = [customer.order_count for customer in customers]

    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data.get("email")
        customer, _ = Customer.objects.get_or_create(
            email=email,
            defaults={
                'name': form.cleaned_data.get("ordered_by"),
                'shipping_address': form.cleaned_data.get("shipping_address"),
                'mobile': form.cleaned_data.get("mobile"),
            }
        )

        items_by_vendor = defaultdict(list)
        for item in cartitems:
            items_by_vendor[item.product.vendor].append(item)

        last_order = None
        with transaction.atomic():
            for vendor, items in items_by_vendor.items():
                last_order = handle_order_creation(items, form, cart, vendor, customer)
            
            cart.completed = True
            cart.save()

        pm = form.cleaned_data.get("payment_method")
        if pm == "Khalti" and last_order:
            return redirect(reverse("khaltirequest") + "?o_id=" + str(last_order.id))

    context = {
        "form": form, 
        "cart": cart, 
        "items": cartitems, 
    }
    return render(request, "checkout.html", context)

class KhaltiRequestView(View):
    def get(self, request, *args, **kwargs):
        o_id = request.GET.get("o_id")
        order = Order.objects.get(id=o_id)
        context = {
            "order": order
        }
        return render(request, "khaltirequest.html", context)

class KhaltiVerifyView(View):
    def get(self, request, *args, **kwargs):
        token = request.GET.get("token")
        amount = request.GET.get("amount")
        o_id = request.GET.get("order_id")
        print(token, amount, o_id)

        url = "https://khalti.com/api/v2/payment/verify/"
        payload = {
            "token": token,
            "amount": amount
        }
        headers = {
            "Authorization": "Key test_secret_key_de7c8744c0ed419593bcde4a8c6ddd1c"
        }

        order_obj = Order.objects.get(id=o_id)

        response = requests.post(url, payload, headers=headers)
        resp_dict = response.json()
        if resp_dict.get("idx"):
            success = True
            order_obj.payment_completed = True
            order_obj.save()
        else:
            success = False
        data = {
            "success": success
        }
        return JsonResponse(data)
    
"""
def login(request):
    if request.method == "GET":
        # Store the 'next' parameter in the session
        next_url = request.GET.get('next', '/')
        request.session['next'] = next_url
        
    if request.method == "POST":
        # The rest of your login logic ...
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)
        
        if user is not None:
            auth.login(request, user)
            messages.success(request, f"Hello {username}, You Are Successfully Logged In")
            
            # Redirect to the URL stored in session or default to home page
            next_url = request.session.pop('next', '/')
            return redirect(next_url)
        
    return render(request, 'index.html')
"""
"""
def register(request):
    if request.method=='POST':
        form = registrationform(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            # password1 = form.cleaned_data.get('password1')
            # user = auth.authenticate(username=username,password=password1)
            # auth.login(request, user)
            messages.info(request, f'Hello {username}, You are Successfully Registered!!') 
            return render(request, 'success.html',)
            form = registrationform()
    else:
        form = registrationform()
    return render(request, 'register.html', {'form':form})
"""

from django.http import QueryDict

"""
def logout(request):
    next_url = request.GET.get('next', None)

    if next_url is None:
        next_url = request.META.get('HTTP_REFERER', '/')
    
    # Validate the next_url
    if not url_has_allowed_host_and_scheme(url=next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        next_url = '/'
    
    auth.logout(request)
    return redirect(next_url)
"""

def success(request):
    return render(request, 'success.html')

def get_sales_data(request):

    # Identifying the vendor from the logged in user
    vendor = None
    try:
        vendor = Vendor.objects.get(user=request.user)
    except Vendor.DoesNotExist:
        pass  # Vendor not found for the user

    # Fetching from session or GET request
    filters_from_session = request.session.get('filters', {})
    timeframe_products = request.GET.get('timeframe_products')
    timeframe_sales = request.GET.get('timeframe_sales')
    timeframe_customers = request.GET.get('timeframe_customers')

    if not timeframe_products:
        timeframe_products = filters_from_session.get('timeframe_products', 'daily_desc')
    if not timeframe_sales:
        timeframe_sales = filters_from_session.get('timeframe_sales', 'daily_desc')
    if not timeframe_customers:
        timeframe_customers = filters_from_session.get('timeframe_customers', 'daily_desc')

    # Update the session data after determining the current values
    request.session['filters'] = {
        'timeframe_products': timeframe_products,
        'timeframe_customers': timeframe_customers,
        'timeframe_sales': timeframe_sales
    }

    print("Timeframe Products:", timeframe_products)
    print("Timeframe Sales:", timeframe_sales)
    print("Timeframe Customers:", timeframe_customers)


    today = timezone.now()

    # Filtering logic for products
    filter_date_products = get_filter_date(timeframe_products)
    ordering_products = get_ordering(timeframe_products)
    sales_data_products = get_sales_data_by_filter(timeframe_products, filter_date_products, ordering_products, vendor)
    
# Create a dictionary of {product name: quantity}
    product_quantity_dict = {record.product.name: record.quantity_sold for record in sales_data_products}

    # Filter out products with a quantity of 0
    product_quantity_dict = {product: qty for product, qty in product_quantity_dict.items() if qty > 0}

    # Generate lists
    products = list(product_quantity_dict.keys())
    quantities = list(product_quantity_dict.values())

    costs_based_on_quantity = [float(record.cost_based_on_quantity) for record in sales_data_products]

    # Sales Labels Calculation for products
    sales_labels_products = get_sales_labels(timeframe_products, today)

    # Filtering logic for total sales
    filter_date_sales = get_filter_date(timeframe_sales)
    sales_data_sales = get_sales_data_by_filter(timeframe_sales, filter_date_sales, None, vendor)

    # Sales Labels Calculation for sales
    sales_labels_sales = get_sales_labels(timeframe_sales, today)

    # Filtering logic for customers
    filter_date_customers = get_filter_date(timeframe_customers)
    customers = get_customers_by_user(request.user, filter_date_customers)
    customer_names = [customer.name for customer in customers]
    order_counts = [customer.order_count for customer in customers]

    # Calculate the total sales for today
    total_sales_today = 0
    if vendor:  # Ensure vendor is found for the user
        total_sales_today = SalesRecord.objects.filter(
            vendor=vendor, sale_date=today.date()
        ).aggregate(total_sales=Sum('cost_based_on_quantity'))['total_sales'] or 0

    print("Vendor:", vendor)

    start_of_day = today.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = today.replace(hour=23, minute=59, second=59, microsecond=999999)

    if vendor:
        total_daily_orders = Order.objects.filter(vendor=vendor, created_at__range=(start_of_day, end_of_day)).count()

    else:
        total_daily_orders = 0
    
    print("Total Daily Orders:", total_daily_orders)

    if vendor:

        total_customers = Order.objects.filter(vendor=vendor).values('customer').distinct().count()

    else:

        total_customers = 0

    if vendor:
        total_cost = SalesRecord.objects.filter(
            vendor=vendor
        ).aggregate(total_cost=Sum('cost_based_on_quantity'))['total_cost'] or 0

    else:
        total_cost = 0

    context = {
        'products': products,
        'quantities': quantities,
        'costs_based_on_quantity': costs_based_on_quantity,
        "customer_names": customer_names, 
        "order_counts": order_counts,
        'sales_labels_products': sales_labels_products,
        'sales_labels_sales': sales_labels_sales,
        'sales_data_sales': sales_data_sales,
        'total_sales_today': total_sales_today,
        'total_daily_orders': total_daily_orders,
        'total_customers': total_customers,
        'total_cost': total_cost,
    }

    print(len(products), products)
    print(len(quantities), quantities)
    print(len(customer_names), customer_names)
    print(len(order_counts), order_counts)
    
    return render(request, 'pages/index.html', context)

def get_sales_labels(timeframe, today):
    if 'daily' in timeframe:
        return [(today - timedelta(days=i)).strftime('%A') for i in range(7)][::-1]
    elif 'weekly' in timeframe:
        return [(today - timedelta(weeks=i)).strftime('%Y-%W') for i in range(4)][::-1]  # Week numbers
    elif 'monthly' in timeframe:
        return [(today - timedelta(days=i*30)).strftime('%B') for i in range(12)][::-1]
    elif 'yearly' in timeframe:
        return [str(today.year - i) for i in range(5)][::-1]
    else:
        return []
    
""""
def get_filter_date(timeframe):
    today = timezone.now()
    filter_date = None

    if 'daily' in timeframe:
        filter_date = today.date()
    elif 'weekly' in timeframe:
        start_week = today - timedelta(days=today.weekday())
        end_week = start_week + timedelta(days=6)
        filter_date = (start_week.date(), end_week.date())
    elif 'monthly' in timeframe:
        start_month = today.replace(day=1)
        last_day = (today.replace(month=today.month%12+1, day=1) - timedelta(days=1)).day
        end_month = today.replace(day=last_day)
        filter_date = (start_month.date(), end_month.date())
    elif 'yearly' in timeframe:
        start_year = today.replace(month=1, day=1)
        end_year = start_year.replace(month=12, day=31)
        filter_date = (start_year.date(), end_year.date())

    return filter_date
"""


def get_filter_date(timeframe):
    today = timezone.now().date()  # This gets the date without the time component

    if timeframe == "daily_desc":
        start_of_day = datetime.combine(today, time.min)
        end_of_day = datetime.combine(today, time.max)
        result = (start_of_day, end_of_day)
        print(f"Returning from daily_desc: {type(result)} - {result}")
        return result
        return (start_of_day, end_of_day)
    elif timeframe == "weekly_asc":
        start_week = today - timedelta(days=today.weekday())
        end_week = start_week + timedelta(days=6)  # End of the week
        # Adjusted to consider the full day
        start_of_week_datetime = datetime.combine(start_week, time.min)
        end_of_week_datetime = datetime.combine(end_week, time.max)
        
        # Debugging lines:
        print(f"Weekly Range: {start_of_week_datetime} - {end_of_week_datetime}")
        orders_in_week = Order.objects.filter(created_at__range=(start_of_week_datetime, end_of_week_datetime))
        print(f"Orders in the week: {orders_in_week.count()}")
        result = (start_of_week_datetime, end_of_week_datetime)
        print(f"Returning from weekly_asc: {type(result)} - {result}")
        return result
    # ... other timeframes ...


    # ... other timeframes ...

# For debugging purposes:
print(get_filter_date("daily_desc"))  # should print today's date
print(get_filter_date("weekly_asc"))  # should print start and end dates of the week


def get_ordering(timeframe):
    if '_desc' in timeframe:
        return '-quantity_sold'
    elif '_asc' in timeframe:
        return 'quantity_sold'
    return None

def get_sales_data_by_filter(timeframe, filter_date, ordering=None, vendor=None):
    sales_data = SalesRecord.objects.all()

    # If a vendor is provided, filter the SalesRecord by the products associated with that vendor
    if vendor:
        vendor_products = Product.objects.filter(vendor=vendor)
        sales_data = sales_data.filter(product__in=vendor_products)

    # Timeframe and date filtering
    if 'daily' in timeframe:
        # Check if the filter_date is a tuple (range) or a single date
        if isinstance(filter_date, tuple):  # This means we have a range
            start_date, end_date = filter_date
            sales_data = sales_data.filter(sale_date__range=(start_date, end_date))
        else:  # This means we have a single day
            sales_data = sales_data.filter(sale_date=filter_date)

    # Ordering
    return sales_data.order_by(ordering or '-quantity_sold')  # Default order added


def get_customers_by_user(user, filter_date):
    try:
        vendor = Vendor.objects.get(user=user)
        is_vendor = True
    except Vendor.DoesNotExist:
        is_vendor = False

    if is_vendor:
        vendor_products = Product.objects.filter(vendor=vendor)

        # We'll create a subquery for counting the orders containing the vendor's products for each customer.
        orders_subquery = Order.objects.filter(
            customer=OuterRef('pk'),
            order_items__product__in=vendor_products
        ).distinct().order_by().values('customer').annotate(order_count=Count('id')).values('order_count')[:1]

        print(Order.objects.filter(order_items__product__in=vendor_products).values('customer').annotate(order_count=Count('id')))
        customers_query = Customer.objects.annotate(order_count=Coalesce(Subquery(orders_subquery), 0))

        if filter_date:
            if isinstance(filter_date, tuple):  # If it's a tuple, it means it's a range
                customers_query = customers_query.filter(order__created_at__range=filter_date)
            else:  # If it's not a tuple, it's a single date
                start_of_day = datetime.combine(filter_date, time.min)
                end_of_day = datetime.combine(filter_date, time.max)
                customers_query = customers_query.filter(order__created_at__range=(start_of_day, end_of_day))

        print(customers_query.values('id', 'name', 'order_count'))
        # Only include customers with order_count greater than zero
        customers = customers_query.filter(order_count__gt=0).distinct()
    else:
        customers_query = Customer.objects.all()

        if filter_date:
            if isinstance(filter_date, tuple):
                customers_query = customers_query.filter(order__created_at__range=filter_date)
            else:
                start_of_day = datetime.combine(filter_date, time.min)
                end_of_day = datetime.combine(filter_date, time.max)
                customers_query = customers_query.filter(order__created_at__range=(start_of_day, end_of_day))

        customers = customers_query.annotate(order_count=Count('order'))

    return customers


# Authentication
class UserLoginView(LoginView):
  template_name = 'accounts/login.html'
  form_class = LoginForm

def register(request):
  if request.method == 'POST':
    form = RegistrationForm(request.POST)
    if form.is_valid():
      form.save()
      print('Account created successfully!')
      return redirect('login/')
    else:
      print("Register failed!")
  else:
    form = RegistrationForm()

  context = { 'form': form }
  return render(request, 'accounts/register.html', context)

def logout_view(request):
  logout(request)
  return redirect('login')