from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView, CreateView, FormView, DetailView, ListView
from store.models import Product, Cart, CartItem, Order
from django.http import JsonResponse
import json
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from .forms import CheckoutForm
from django.http import HttpResponseRedirect
import requests



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