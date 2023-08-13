from django.shortcuts import redirect, render, get_object_or_404
from products.models import ProductModel

def showdata(request):
    results=ProductModel.objects.all()
    return render(request, 'index.html',{"data":results})
