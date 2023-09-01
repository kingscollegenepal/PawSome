from django.urls import path
from .import views
from .views import KhaltiRequestView, KhaltiVerifyView

urlpatterns = [
    path("", views.home, name = "home"),
    path("cart", views.cart, name="cart"),
    path("add_to_cart", views.add_to_cart, name="add"),
    path('checkout/', views.checkout, name='checkout'),
    path("khalti-request/", KhaltiRequestView.as_view(), name="khaltirequest"),
    path("khalti-verify/", KhaltiVerifyView.as_view(), name="khaltiverify"),
]

