def get_cart(session):
    return session.get("cart", {})

def save_cart(session, cart):
    session["cart"] = cart
    session.modified = True

def cart_add(session, product_id, qty=1):
    cart = get_cart(session)
    pid = str(product_id)
    cart[pid] = cart.get(pid, 0) + qty
    save_cart(session, cart)

def cart_remove(session, product_id):
    cart = get_cart(session)
    pid = str(product_id)
    if pid in cart:
        del cart[pid]
    save_cart(session, cart)

def cart_clear(session):
    save_cart(session, {})
