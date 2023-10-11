from django.urls import path
from .import views
from .views import *
from django.contrib.auth import views as auth_views


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

    path('dog-products/beds_and_mats/', views.dog_beds_and_mats_products, name="dog_beds_and_mats_products"),
    path('dog-products/healthcare/', views.dog_healthcare_products, name="dog_healthcare_products"),
    path('dog-products/treats_and_chews/', views.dog_treats_and_chews_products, name="dog_treats_and_chews_products"),
    path('dog-products/food/', views.dog_food_products, name="dog_food_products"),
    path('dog-products/bowls_feeders/', views.dog_bowls_feeders_products, name="dog_bowls_feeders_products"),
    path('dog-products/toys_products/', views.dog_toys_products, name="dog_toys_products"),
    path('dog-products/collar_leashes_products/', views.dog_collar_leashes_products, name="dog_collar_leashes_products"),
    path('dog-products/training_aids_products/', views.dog_training_aids_products, name="dog_training_aids_products"),
    path('dog-products/grooming_supplies_products/', views.dog_grooming_supplies_products, name="dog_grooming_supplies_products"),
    path('dog-products/crates_carriers/', views.dog_crates_and_carriers_products, name="dog_crates_carriers_products"),

    path('cat-products/', views.cat_products, name="cat_products"),

    path('cat-products/food/', views.cat_food, name="cat_food"),
    path('cat-products/grooming/', views.cat_grooming, name="cat_grooming"),
    path('cat-products/toys/', views.cat_toys, name="cat_toys"),
    path('cat-products/treats/', views.cat_treats, name="cat_treats"),
    path('cat-products/transport/', views.cat_transport, name="cat_transport"),
    path('cat-products/bedding/', views.cat_bedding, name="cat_bedding"),
    path('cat-products/collors_harness/', views.cat_collors_harness, name="cat_collors_harness"),
    path('cat-products/kernels/', views.cat_kernels, name="cat_kennels"),
    path('cat-products/training_aids/', views.cat_training_aids, name="cat_training_aids"),
    path('cat-products/bowls/', views.cat_bowls, name="cat_bowls"),

    path('dog-products/<int:product_id>/', views.product_detail, name="product_detail"),
    path('cat-products/<int:product_id>/', views.product_detail, name="product_detail"),
    path('search/', views.search_results, name='search_results'),


    ## path('login/', views.login, name = "login"),
    ##path('logout/', views.logout, name="logout"),
    ##path('register/', views.register, name = "register"),
    path('vendor/', views.get_sales_data, name='vendor'),

    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),

]





