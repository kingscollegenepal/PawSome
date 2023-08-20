from django.urls import path
from .views import login_view

urlpatterns = [
    # Other URLs
    path('login/', login_view, name='login'),