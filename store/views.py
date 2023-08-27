from django.shortcuts import render, redirect
from store.models import Product, Cart, CartItem
from django.http import JsonResponse
import json
from django.contrib import messages

# pylint: disable=missing-function-docstring
def home(request):
    products = Product.objects.all()
    
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user, completed = False)
    context = {"products":products}

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


def confirm_payment(request, pk):
    cart = Cart.objects.get(id=pk)
    cart.completed = True
    cart.save()
    messages.success(request, "Payment made successfully")
    return redirect("home")