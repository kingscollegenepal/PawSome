from django.urls import path
from .import views

urlpatterns = [
    path("", views.home, name = "home"),
    path("cart", views.cart, name="cart"),
    path("add_to_cart", views.add_to_cart, name="add"),
    path("confirm_payment/<str:pk>", views.confirm_payment, name="add"),
]

