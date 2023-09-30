from django import forms
from .models import Order, Product, Review
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from store.models import Customer

class CheckoutForm(forms.ModelForm):
    ordered_by = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}))
    shipping_address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Shipping Address'}))
    mobile = forms.CharField(
        validators=[RegexValidator(r'^\d{10}$', message="Mobile number must be entered in the format: '9999999999'. Up to 10 digits allowed.")],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '10-digit Mobile Number'})
    )
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}))
    payment_method = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control'}), choices=Order.payment_method.field.choices)

    
    class Meta:
        model = Order
        fields = ["ordered_by", "shipping_address", "mobile", "email", "payment_method"]
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Check if a customer with the given email already exists
        email = self.cleaned_data['email']
        customer = Customer.objects.filter(email=email).first()

        if not customer:
            customer = Customer.objects.create(
                name=self.cleaned_data['ordered_by'],
                shipping_address=self.cleaned_data['shipping_address'],
                mobile=self.cleaned_data['mobile'],
                email=email
            )

        instance.customer = customer
        if commit:
            instance.save()
        return instance


        
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