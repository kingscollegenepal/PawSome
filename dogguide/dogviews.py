from django.shortcuts import render
from dogguide.models import DogGuide

def dogshowdata(request):
    dogresults = DogGuide.objects.all()
    return render (request, 'dog.html',{"data":dogresults})



# Create your views here.
