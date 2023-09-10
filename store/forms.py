from django import forms
from .models import Order, Product, Review
from django.contrib.auth.models import User


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["ordered_by", "shipping_address",
                  "mobile", "email", "payment_method"]
        
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['review_text']