from django.urls import path , include
from login import views

urlpatterns = [
<<<<<<< HEAD
    path('', views.login),
=======
    path('login/', views.login),
>>>>>>> bb75f3e (login and home page)
    path('success', views.logout),
]