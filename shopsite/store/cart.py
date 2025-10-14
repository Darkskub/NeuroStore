# store/cart.py
from decimal import Decimal
from .models import Product

CART_SESSION_ID = "cart"

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_ID)
        if not cart:
            cart = self.session[CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product_id: int, qty: int = 1):
        pid = str(product_id)
        if pid not in self.cart:
            product = Product.objects.get(pk=product_id)
            self.cart[pid] = {"qty": 0, "price": str(product.price)}
        self.cart[pid]["qty"] += qty
        if self.cart[pid]["qty"] <= 0:
            self.remove(product_id)
        self.save()

    def set(self, product_id: int, qty: int):
        pid = str(product_id)
        if qty <= 0:
            self.remove(product_id)
        else:
            if pid not in self.cart:
                product = Product.objects.get(pk=product_id)
                self.cart[pid] = {"qty": 0, "price": str(product.price)}
            self.cart[pid]["qty"] = qty
            self.save()

    def remove(self, product_id: int):
        pid = str(product_id)
        if pid in self.cart:
            del self.cart[pid]
            self.save()

    def clear(self):
        self.session[CART_SESSION_ID] = {}
        self.session.modified = True

    def save(self):
        self.session[CART_SESSION_ID] = self.cart
        self.session.modified = True

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            item = self.cart[str(product.id)]
            price = Decimal(item["price"])
            qty = int(item["qty"])
            yield {
                "product": product,
                "price": price,
                "qty": qty,
                "subtotal": price * qty,
            }

    def total_qty(self):
        return sum(int(item["qty"]) for item in self.cart.values())

    def total_price(self):
        return sum(Decimal(item["price"]) * int(item["qty"]) for item in self.cart.values())
