from django.urls import path , include
from login import views

urlpatterns = [
    path('login/', views.login),
    path('success', views.logout),
]