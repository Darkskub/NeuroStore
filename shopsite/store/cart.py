from django.db import transaction
from .models import ActiveCart, ActiveCartItem, Product, Order, OrderItem


class Cart:
    def __init__(self, request):
        self.request = request
        self.user = request.user
        self.cart_obj = None

        if self.user.is_authenticated:
            self.cart_obj, _ = ActiveCart.objects.get_or_create(user=self.user)

    @property
    def is_enabled(self) -> bool:
        return self.user.is_authenticated and self.cart_obj is not None

    def items(self):
        if not self.is_enabled:
            return ActiveCartItem.objects.none()
        return self.cart_obj.items.select_related("product").all()

    @property
    def total_qty(self) -> int:
        if not self.is_enabled:
            return 0
        return sum(i.qty for i in self.items())

    @property
    def total_price(self):
        if not self.is_enabled:
            return 0
        return sum(i.subtotal for i in self.items())

    def add(self, product: Product, qty: int = 1):
        if not self.is_enabled:
            return

        qty = max(int(qty), 1)
        item, created = ActiveCartItem.objects.get_or_create(
            cart=self.cart_obj,
            product=product,
            defaults={"price": product.price, "qty": qty},
        )
        if not created:
            item.qty += qty
            item.price = product.price
            item.save(update_fields=["qty", "price"])

    def remove_item(self, item_id: int):
        if not self.is_enabled:
            return
        ActiveCartItem.objects.filter(cart=self.cart_obj, id=item_id).delete()

    def clear(self):
        if not self.is_enabled:
            return
        self.cart_obj.items.all().delete()

    @transaction.atomic
    def create_order(self, comment: str = "") -> Order:
        if not self.is_enabled:
            raise RuntimeError("Cart is disabled for anonymous users")

        order = Order.objects.create(user=self.user, comment=comment or "")
        for i in self.items():
            OrderItem.objects.create(
                order=order,
                product=i.product,
                price=i.price,
                qty=i.qty,
            )
        self.clear()
        return order
