from django.db import models

class Product(models.Model):
    name = models.CharField("Название", max_length=200)
    slug = models.SlugField("Слаг", unique=True)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    image = models.ImageField("Изображение", upload_to="products/", blank=True, null=True)
    description = models.TextField("Описание", blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return f"{self.name} ({self.price} ₽)"
