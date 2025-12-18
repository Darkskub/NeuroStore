from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


def _unique_slug(model_cls, base_text: str, instance_pk=None) -> str:
    base = slugify(base_text, allow_unicode=True) or "item"
    candidate = base
    n = 2
    qs = model_cls.objects.all()
    if instance_pk:
        qs = qs.exclude(pk=instance_pk)
    while qs.filter(slug=candidate).exists():
        candidate = f"{base}-{n}"
        n += 1
    return candidate


class Category(models.Model):
    name = models.CharField("Название", max_length=200)
    slug = models.SlugField("Слаг", unique=True, blank=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="Родительская категория",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _unique_slug(Category, self.name, self.pk)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        null=True,
        blank=True,
        verbose_name="Категория",
    )
    name = models.CharField("Название", max_length=200)
    slug = models.SlugField("Слаг", unique=True, blank=True)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    image = models.ImageField("Изображение", upload_to="products/", blank=True, null=True)
    description = models.TextField("Описание", blank=True)
    created_at = models.DateTimeField("Создан", auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _unique_slug(Product, self.name, self.pk)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.price} ₽)"


class News(models.Model):
    title = models.CharField("Заголовок", max_length=200)
    slug = models.SlugField("Слаг", unique=True, blank=True)
    body = models.TextField("Текст")
    created_at = models.DateTimeField("Дата", auto_now_add=True)
    is_published = models.BooleanField("Опубликовано", default=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Новость"
        verbose_name_plural = "Новости"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _unique_slug(News, self.title, self.pk)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ActiveCart(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="active_cart",
        verbose_name="Пользователь",
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
        verbose_name="Корзина",
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Товар")
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


class Order(models.Model):
    STATUS_NEW = "new"
    STATUS_PROCESSING = "processing"
    STATUS_SHIPPED = "shipped"
    STATUS_DONE = "done"
    STATUS_CANCELED = "canceled"

    STATUS_CHOICES = [
        (STATUS_NEW, "Новый"),
        (STATUS_PROCESSING, "В обработке"),
        (STATUS_SHIPPED, "Отправлен"),
        (STATUS_DONE, "Завершён"),
        (STATUS_CANCELED, "Отменён"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders", verbose_name="Клиент")
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    comment = models.TextField("Комментарий", blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Заказ #{self.pk} ({self.user.username})"

    @property
    def total_price(self):
        return sum((item.subtotal for item in self.items.all()), 0)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", verbose_name="Заказ")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Товар")
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    qty = models.PositiveIntegerField("Количество", default=1)

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    def __str__(self):
        return f"{self.product.name} x {self.qty}"

    @property
    def subtotal(self):
        return self.price * self.qty
