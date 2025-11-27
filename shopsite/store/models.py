from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField("Название категории", max_length=200)
    slug = models.SlugField("Слаг", unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        verbose_name="Категория",
        on_delete=models.CASCADE,
        related_name="products",
        null=True,
        blank=True,
    )
    name = models.CharField("Название", max_length=200)
    slug = models.SlugField("Слаг", unique=True)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    image = models.ImageField(
        "Изображение", upload_to="products/", blank=True, null=True
    )
    description = models.TextField("Описание", blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return f"{self.name} ({self.price} ₽)"


class ActiveCart(models.Model):
    """
    Текущая корзина клиента, хранится в БД, чтобы менеджер мог её видеть и править.
    Один пользователь — одна активная корзина.
    """
    user = models.OneToOneField(
        User,
        verbose_name="Клиент",
        on_delete=models.CASCADE,
        related_name="active_cart",
    )
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Корзина клиента"
        verbose_name_plural = "Корзины клиентов"

    def __str__(self):
        return f"Корзина {self.user.username}"

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def total_qty(self):
        return sum(item.qty for item in self.items.all())


class ActiveCartItem(models.Model):
    cart = models.ForeignKey(
        ActiveCart,
        verbose_name="Корзина",
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        Product,
        verbose_name="Товар",
        on_delete=models.CASCADE,
    )
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    qty = models.PositiveIntegerField("Количество", default=1)

    class Meta:
        verbose_name = "Позиция корзины"
        verbose_name_plural = "Позиции корзины"

    @property
    def subtotal(self):
        return self.price * self.qty

    def __str__(self):
        return f"{self.product.name} x {self.qty}"


class News(models.Model):
    title = models.CharField("Заголовок", max_length=200)
    slug = models.SlugField("Слаг", unique=True)
    body = models.TextField("Текст новости")
    created_at = models.DateTimeField("Дата публикации", auto_now_add=True)
    is_published = models.BooleanField("Опубликовано", default=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Новость"
        verbose_name_plural = "Новости"

    def __str__(self):
        return self.title


class Order(models.Model):
    STATUS_NEW = "new"
    STATUS_PROCESSING = "processing"
    STATUS_DONE = "done"
    STATUS_CANCELED = "canceled"

    STATUS_CHOICES = [
        (STATUS_NEW, "Новый"),
        (STATUS_PROCESSING, "В обработке"),
        (STATUS_DONE, "Выполнен"),
        (STATUS_CANCELED, "Отменён"),
    ]

    user = models.ForeignKey(
        User,
        verbose_name="Клиент",
        on_delete=models.CASCADE,
        related_name="orders",
    )
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    status = models.CharField(
        "Статус", max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW
    )
    comment = models.CharField(
        "Комментарий клиента", max_length=500, blank=True, default=""
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Заказ #{self.id} от {self.user.username}"

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        verbose_name="Заказ",
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        Product,
        verbose_name="Товар",
        on_delete=models.PROTECT,
    )
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    qty = models.PositiveIntegerField("Количество", default=1)

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    @property
    def subtotal(self):
        return self.price * self.qty

    def __str__(self):
        return f"{self.product.name} x {self.qty}"
