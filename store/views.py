from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView, CreateView, FormView, DetailView, ListView
from store.models import Product, Cart, CartItem, Order, Review, Rating, OrderItem
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Avg
import json
from django.contrib import messages
from django.db import transaction
from django.urls import reverse_lazy, reverse
from .forms import CheckoutForm, ReviewForm
from django.http import HttpResponseRedirect
import requests
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from math import floor
from django.contrib.auth.models import User, auth
from .forms import registrationform
from django.contrib.auth.forms import UserCreationForm
from django.utils.http import url_has_allowed_host_and_scheme
from collections import defaultdict


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

    print("User:", request.user)

    if request.user.is_authenticated:
        print("User is authenticated")

        cart, created = Cart.objects.get_or_create(user=request.user, completed=False)
        cartitem, created = CartItem.objects.get_or_create(cart=cart, product=product)
        cartitem.quantity +=1
        cartitem.save()

        num_of_item = cart.num_of_items

        print(cartitem)

    return JsonResponse(num_of_item, safe=False) 


class ManageCartView(View):
    def get(self, request, *args, **kwargs):
        print("This is manage cart section")
        item_id = self.kwargs["item_id"]
        action=request.GET.get("action")
        item_obj=CartItem.objects.get(id=item_id)
        cart_item=item_obj.cart
        print(item_id, action)

        if action=="inc":
            item_obj.quantity += 1
            item_obj.save()
            updated_cart_total = cart_item.total_price
            print("Updated Cart Total:", updated_cart_total)

        elif action=="dcr":
            item_obj.quantity -= 1
            item_obj.save()
            updated_cart_total = cart_item.total_price
            print("Updated Cart Total:", updated_cart_total)
            if item_obj.quantity == 0:
                item_obj.delete()

        elif action=="rmv":
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


def checkout(request):
    cart = None
    cartitems = []
    form = CheckoutForm()

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user, completed=False)
        cartitems = cart.cartitems.all()

    if request.method == 'POST':
        form = CheckoutForm(request.POST or None)
        if form.is_valid():
            if cart:
                items_by_vendor = {}
                for item in cartitems:
                    if item.product.vendor not in items_by_vendor:
                        items_by_vendor[item.product.vendor] = []
                    items_by_vendor[item.product.vendor].append(item)
                
                # Start a database transaction
                with transaction.atomic():
                    for vendor, items in items_by_vendor.items():
                        order = form.save(commit=False)
                        order.total = sum(item.product.price * item.quantity for item in items)
                        order.cart = cart
                        order.order_status = "Order Received"
                        order.vendor = vendor
                        order.save()
                        
                        # Create OrderItem instances for each item in the order
                        for item in items:
                            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)
                    
                    # Mark the cart as completed after processing all orders
                    cart.completed = True
                    cart.save()
                
                pm = form.cleaned_data.get("payment_method")
                if pm == "Khalti":
                    return redirect(reverse("khaltirequest") + "?o_id=" + str(order.id))
            else:
                return HttpResponseRedirect(reverse_lazy("home"))
    
    context = {"form": form, "cart": cart, "items": cartitems}
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

from django.http import QueryDict

def logout(request):
    next_url = request.GET.get('next', None)

    if next_url is None:
        next_url = request.META.get('HTTP_REFERER', '/')
    
    # Validate the next_url
    if not url_has_allowed_host_and_scheme(url=next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        next_url = '/'
    
    auth.logout(request)
    return redirect(next_url)

def success(request):
    return render(request, 'success.html')




