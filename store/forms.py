from django import forms
from .models import Order, Product, Review
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class CheckoutForm(forms.ModelForm):

    ordered_by = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}))
    shipping_address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3,'class': 'form-control', 'placeholder': 'Shipping Address'}))
    mobile = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control','placeholder': '10-digit Mobile Number'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control','placeholder': 'Email Address'}))
    payment_method = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control'}), choices=Order.payment_method.field.choices)

    
    class Meta:
        model = Order
        fields = ["ordered_by", "shipping_address",
                  "mobile", "email", "payment_method"]
        
class ReviewForm(forms.ModelForm):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]  # Assuming a 1-5 rating scale
    rating = forms.ChoiceField(choices=RATING_CHOICES, widget=forms.RadioSelect)

    class Meta:
        model = Review
        fields = ['review_text']

class registrationform(UserCreationForm):
    email = forms.EmailField(
        required = True,
    )
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']