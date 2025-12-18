from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Product, Category, News


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "slug", "parent"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "qty", "style": "width:100%"}),
            "slug": forms.TextInput(attrs={"class": "qty", "style": "width:100%"}),
            "parent": forms.Select(attrs={"class": "qty", "style": "width:100%"}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["category", "name", "slug", "price", "image", "description"]
        widgets = {
            "category": forms.Select(attrs={"class": "qty", "style": "width:100%"}),
            "name": forms.TextInput(attrs={"class": "qty", "style": "width:100%"}),
            "slug": forms.TextInput(attrs={"class": "qty", "style": "width:100%"}),
            "price": forms.NumberInput(attrs={"class": "qty", "step": "0.01", "style": "width:100%"}),
            "description": forms.Textarea(attrs={"class": "qty", "rows": 4, "style": "width:100%"}),
        }


class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ["title", "slug", "body", "is_published"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "qty", "style": "width:100%"}),
            "slug": forms.TextInput(attrs={"class": "qty", "style": "width:100%"}),
            "body": forms.Textarea(attrs={"class": "qty", "rows": 8, "style": "width:100%"}),
            "is_published": forms.CheckboxInput(attrs={"style": "transform:scale(1.2);"}),
        }


class ManagerCreateForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "qty", "style": "width:100%"}))
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput(attrs={"class": "qty", "style": "width:100%"}))
    password2 = forms.CharField(label="Повтор пароля", widget=forms.PasswordInput(attrs={"class": "qty", "style": "width:100%"}))

    class Meta:
        model = User
        fields = ("username",)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = True
        user.is_superuser = False
        if commit:
            user.save()
        return user
