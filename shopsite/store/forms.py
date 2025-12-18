from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import Category, Product, News, Order


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ("name", "parent")


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ("category", "name", "price", "image", "description")


class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ("title", "body", "is_published")


class SignUpForm(UserCreationForm):
    email = forms.EmailField(label="Email", required=False)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class ManagerCreateForm(UserCreationForm):
    email = forms.EmailField(label="Email", required=False)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get("email") or ""
        user.is_staff = True
        if commit:
            user.save()
        return user


class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ("status",)
