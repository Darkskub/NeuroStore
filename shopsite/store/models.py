from django.db import models
from django.contrib.auth.models import User
from autoslug import AutoSlugField


class Category(models.Model):
    name = models.CharField("Название", max_length=200)
    slug = AutoSlugField("Слаг", populate_from="name", unique=True, always_update=False)
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="Родительская категория"
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        null=True,
        blank=True,
        verbose_name="Категория"
    )
    name = models.CharField("Название", max_length=200)
    slug = AutoSlugField("Слаг", populate_from="name", unique=True, always_update=False)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    image = models.ImageField("Изображение", upload_to="products/", blank=True, null=True)
    description = models.TextField("Описание", blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return f"{self.name} ({self.price} ₽)"


class News(models.Model):
    title = models.CharField("Заголовок", max_length=200)
    slug = AutoSlugField("Слаг", populate_from="title", unique=True, always_update=False)
    body = models.TextField("Текст")
    created_at = models.DateTimeField("Дата", auto_now_add=True)
    is_published = models.BooleanField("Опубликовано", default=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Новость"
        verbose_name_plural = "Новости"

    def __str__(self):
        return self.title


class ActiveCart(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="active_cart",
        verbose_name="Пользователь"
    )
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Активная корзина"
        verbose_name_plural = "Активные корзины"

    def __str__(self):
        return f"Корзина {self.user.username}"


class ActiveCartItem(models.Model):
    cart = models.ForeignKey(
        ActiveCart,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Корзина"
    )
    product = models.ForeignKey(
        "Product",
        on_delete=models.PROTECT,
        verbose_name="Товар"
    )
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    qty = models.PositiveIntegerField("Количество", default=1)

    class Meta:
        verbose_name = "Позиция корзины"
        verbose_name_plural = "Позиции корзины"
        unique_together = ("cart", "product")

    def __str__(self):
        return f"{self.product.name} x {self.qty}"

    @property
    def subtotal(self):
        return self.price * self.qty
