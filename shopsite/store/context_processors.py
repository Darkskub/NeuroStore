from .cart import Cart


def cart_summary(request):
    if not request.user.is_authenticated:
        return {"cart_total_qty": 0, "cart_total_price": 0}

    cart = Cart(request)
    return {
        "cart_total_qty": cart.total_qty,
        "cart_total_price": cart.total_price,
    }
