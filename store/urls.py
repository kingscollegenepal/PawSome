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
    path('dog-products/', views.dog_products, name="dog_products"),
    path('dog-products/beds_and_mats/', views.beds_and_mats_products, name="beds_and_mats_products"),
    path('dog-products/healthcare/', views.healthcare_products, name="healthcare_products"),
    path('dog-products/treats_and_chews/', views.treats_and_chews_products, name="treats_and_chews_products"),
    path('dog-products/food/', views.food_products, name="food_products"),
    path('dog-products/bowls_feeders/', views.bowls_feeders_products, name="bowls_feeders_products"),
    path('dog-products/toys_products/', views.toys_products, name="toys_products"),
    path('dog-products/collar_leashes_products/', views.collar_leashes_products, name="collar_leashes_products"),
    path('dog-products/training_aids_products/', views.training_aids_products, name="training_aids_products"),
    path('dog-products/grooming_supplies_products/', views.grooming_supplies_products, name="grooming_supplies_products"),
    path('dog-products/crates_carriers/', views.crates_and_carriers_products, name="crates_carriers_products"),
    path('cat-products/', views.cat_products, name="cat_products"),
    path('dog-products/<int:product_id>/', views.product_detail, name="product_detail"),
    path('cat-products/<int:product_id>/', views.product_detail, name="product_detail"),
    path('search/', views.search_results, name='search_results'),
]


