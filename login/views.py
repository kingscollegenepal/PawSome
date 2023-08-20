from django.shortcuts import render , redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from products.models import Product


# Create your views here.
def login(request):
    if request.method=="POST":
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username,password=password)
        if user is not None:
            auth.login(request, user)
            messages.success(request, f" Hello {username}, You Are Successfully Logged In")
            results=Product.objects.all()
            return render(request, 'products.html',{"data":results})

        else:
            if not User.objects.filter(username=username).exists():
                messages.error(request, "Username Doesn't Exist")
            else:
                messages.info(request, "Incorrect Password")
            return redirect('/')

    else:  
        return render(request, "index.html")

def logout(request):
    auth.logout(request)
    return redirect('/')
