from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "slug", "price", "image", "description"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "qty", "style": "width:100%"}),
            "slug": forms.TextInput(attrs={"class": "qty", "style": "width:100%"}),
            "price": forms.NumberInput(attrs={"class": "qty", "step": "0.01", "style": "width:100%"}),
            "description": forms.Textarea(attrs={"class": "qty", "rows": 4, "style": "width:100%"}),
        }
