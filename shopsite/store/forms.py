from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["category", "name", "slug", "price", "image", "description"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "qty", "style": "width:100%"}),
            "slug": forms.TextInput(attrs={"class": "qty", "style": "width:100%"}),
            "price": forms.NumberInput(
                attrs={"class": "qty", "step": "0.01", "style": "width:100%"}
            ),
            "description": forms.Textarea(
                attrs={"class": "qty", "rows": 4, "style": "width:100%"}
            ),
        }


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=False,
        label="Email",
        widget=forms.EmailInput(attrs={"class": "qty", "style": "width:100%"}),
    )

    class Meta:
        model = User
        fields = ("username", "email")
