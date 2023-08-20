from django.shortcuts import render
from catguide.models import CatGuide

def catshowdata(request):
    catresults = CatGuide.objects.all()
    return render (request, 'cat.html',{"data":catresults})



# Create your views here.
