# App/context_processors.py
from .models import Cart, CartItem

def cart_item_count(request):
    count = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            count = cart.items.count()
        except Cart.DoesNotExist:
            count = 0
    else:
        session_key = request.session.session_key
        if session_key:
            try:
                cart = Cart.objects.get(session_key=session_key)
                count = cart.items.count()
            except Cart.DoesNotExist:
                count = 0
    return {'cart_item_count': count}