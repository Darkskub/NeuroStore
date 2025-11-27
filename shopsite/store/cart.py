# store/cart.py
from decimal import Decimal
from .models import Product, ActiveCart, ActiveCartItem


class Cart:
    """
    Корзина, привязанная к пользователю и хранящаяся в БД (ActiveCart).
    Для анонимных пользователей корзина считается пустой.
    """

    def __init__(self, request):
        self.request = request
        self.user = getattr(request, "user", None)
        self.cart_obj = None

        if self.user and self.user.is_authenticated:
            self.cart_obj, _ = ActiveCart.objects.get_or_create(user=self.user)

    def add(self, product_id: int, qty: int = 1):
        if not self.cart_obj:
            # Для анонимных просто игнорируем (у нас корзина только для клиентов).
            return
        product = Product.objects.get(pk=product_id)
        item, created = ActiveCartItem.objects.get_or_create(
            cart=self.cart_obj,
            product=product,
            defaults={"price": product.price, "qty": 0},
        )
        item.qty += qty
        if item.qty <= 0:
            item.delete()
        else:
            item.price = product.price  # на всякий случай обновим цену
            item.save()

    def set(self, product_id: int, qty: int):
        if not self.cart_obj:
            return
        product = Product.objects.get(pk=product_id)
        if qty <= 0:
            ActiveCartItem.objects.filter(cart=self.cart_obj, product=product).delete()
            return
        item, created = ActiveCartItem.objects.get_or_create(
            cart=self.cart_obj,
            product=product,
            defaults={"price": product.price, "qty": qty},
        )
        if not created:
            item.qty = qty
            item.price = product.price
            item.save()

    def remove(self, product_id: int):
        if not self.cart_obj:
            return
        ActiveCartItem.objects.filter(cart=self.cart_obj, product_id=product_id).delete()

    def clear(self):
        if self.cart_obj:
            self.cart_obj.items.all().delete()

    def __iter__(self):
        if not self.cart_obj:
            return
        for item in self.cart_obj.items.select_related("product"):
            yield {
                "product": item.product,
                "price": item.price,
                "qty": item.qty,
                "subtotal": item.subtotal,
            }

    def total_qty(self):
        if not self.cart_obj:
            return 0
        return sum(item.qty for item in self.cart_obj.items.all())

    def total_price(self):
        if not self.cart_obj:
            return Decimal("0.00")
        return sum(item.subtotal for item in self.cart_obj.items.all())
