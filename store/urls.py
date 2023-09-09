from django.urls import path
from .import views
from .views import *

urlpatterns = [
    path("", views.home, name = "home"),
    path("cart/", views.cart, name="cart"),
    path("profile/", CustomerProfileView.as_view(), name ="customerprofile"),
    path("profile/order-<uuid:pk>/", CustomerOrderDetailView.as_view(), name="customerorderdetail"),
    path("add_to_cart", views.add_to_cart, name="add"),
    path("manage-cart/<int:item_id>/", ManageCartView.as_view(), name="managecart"),
    path('checkout/', views.checkout, name='checkout'),
    path("khalti-request/", KhaltiRequestView.as_view(), name="khaltirequest"),
    path("khalti-verify/", KhaltiVerifyView.as_view(), name="khaltiverify"),
    path("dog-products/", views.dog_products, name="dog_products"),
    path("cat-products/", views.cat_products, name="cat_products"),
    path('dog-products/<int:product_id>/', views.product_detail, name="product_detail"),
]


