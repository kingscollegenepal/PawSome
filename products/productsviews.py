from django.shortcuts import redirect, render, get_object_or_404
from products.models import Product

def showdata(request):
    results=Product.objects.all()
    return render(request, 'products.html',{"data":results})
