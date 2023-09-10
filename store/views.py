from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView, CreateView, FormView, DetailView, ListView
from store.models import Product, Cart, CartItem, Order, Review
from django.http import JsonResponse
import json
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from .forms import CheckoutForm, ReviewForm
from django.http import HttpResponseRedirect
import requests
from django.shortcuts import get_object_or_404
from django.db.models import Q


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

    if request.method == "POST" and request.user.is_authenticated:
        review_text = request.POST.get('review_text')
        Review.objects.create(product=product, user=request.user, review_text=review_text)
        return HttpResponseRedirect(reverse('product_detail', args=[product_id]))  # Redirect after POST

    context = {
        'product': product,
        'reviews': reviews,
    }
    return render(request, 'product_detail.html', context)

def search_results(request):
    query = request.GET.get('query')
    products = Product.objects.filter(
        Q(category__icontains=query) | 
        Q(subcategory__icontains=query)
    )
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

def pens_products(request):
    """Display all dog pen products."""
    pens_products = Product.objects.filter(category='Dog', subcategory='Pens')
    context = {"products": pens_products}
    return render(request, "pens_products.html", context)

def beds_products(request):
    """Display all dog pen products."""
    beds_products = Product.objects.filter(category='Dog', subcategory='Beds')
    context = {"products": beds_products}
    return render(request, "beds_products.html", context)


def crates_products(request):
    """Display all dog pen products."""
    crates_products = Product.objects.filter(category='Dog', subcategory='Crates')
    context = {"products": crates_products}
    return render(request, "crates_products.html", context)


def gates_products(request):
    """Display all dog pen products."""
    gates_products = Product.objects.filter(category='Dog', subcategory='Gates')
    context = {"products": gates_products}
    return render(request, "gates_products.html", context)

def cameras_products(request):
    """Display all dog pen products."""
    cameras_products = Product.objects.filter(category='Dog', subcategory='Cameras')
    context = {"products": cameras_products}
    return render(request, "cameras_products.html", context)

def treats_products(request):
    """Display all dog pen products."""
    treats_products = Product.objects.filter(category='Dog', subcategory='Treats')
    context = {"products": treats_products}
    return render(request, "treats_products.html", context)

def food_products(request):
    """Display all dog pen products."""
    food_products = Product.objects.filter(category='Dog', subcategory='Food')
    context = {"products": food_products}
    return render(request, "food_products.html", context)

def bowls_feeders_products(request):
    """Display all dog pen products."""
    bowls_feeders_products = Product.objects.filter(category='Dog', subcategory='Bowls & Feeders')
    context = {"products": bowls_feeders_products}
    return render(request, "bowls_feeders_products.html", context)

def food_storage_accessories_products(request):
    """Display all dog pen products."""
    food_storage_accessories_products = Product.objects.filter(category='Dog', subcategory='Food Storage & Accessories')
    context = {"products": food_storage_accessories_products}
    return render(request, "food_storage_accessories_products.html", context)

def toys_products(request):
    """Display all dog pen products."""
    toys_products = Product.objects.filter(category='Dog', subcategory='Toys')
    context = {"products": toys_products}
    return render(request, "toys_products.html", context)

def collar_leashes_products(request):
    """Display all dog pen products."""
    collar_leashes_products = Product.objects.filter(category='Dog', subcategory='Collar & Leashes')
    context = {"products": collar_leashes_products}
    return render(request, "collar_leashes_products.html", context)

def training_aids_products(request):
    """Display all dog pen products."""
    training_aids_products = Product.objects.filter(category='Dog', subcategory='Training Aids')
    context = {"products": training_aids_products}
    return render(request, "training_aids_products.html", context)


def vitamins_supplements_products(request):
    """Display all dog pen products."""
    vitamins_supplements_products = Product.objects.filter(category='Dog', subcategory='Vitamins & Supplements')
    context = {"products": vitamins_supplements_products}
    return render(request, "vitamins_supplements_products.html", context)


def grooming_supplies_products(request):
    """Display all dog pen products."""
    grooming_supplies_products = Product.objects.filter(category='Dog', subcategory='Vitamins & Supplements')
    context = {"products": grooming_supplies_products}
    return render(request, "grooming_supplies_products.html", context)

def cat_products(request):
    """Display all cat products."""
    cat_products = Product.objects.filter(category='Cat')
    context = {"products": cat_products}
    return render(request, "cat_products.html", context)

def checkout(request):
    cart = None
    cartitems = []
    form = CheckoutForm()

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user, completed=False)
        cartitems = cart.cartitems.all()

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            if cart:  # Using the cart object directly
                # Initialize a new Order model object or get the existing object you want to update
                order = form.save(commit=False)
                
                order.total= cart.total_price
                order.cart = cart
                ## order.total = cart.total  # Assuming `total` is a field in your Cart model
                order.order_status = "Order Received"
                pm = form.cleaned_data.get("payment_method")
                
                # Save the form and the order object to the database
                order.save()

                # Mark the cart as completed
                cart.completed = True
                cart.save()
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
