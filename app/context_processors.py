from .models import Order

def cart_item_count(request):
    cartItems = 0
    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(customer=request.user, complete=False)
        cartItems = order.get_cart_items
    return {'cartItems': cartItems}
