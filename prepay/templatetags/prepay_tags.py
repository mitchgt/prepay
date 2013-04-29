from django import template

register = template.Library()

@register.filter(name="is_in_cart")
def is_in_cart(listing, cart):
    if cart and cart.listings.filter(id = listing.id):
        return True
    else:
        return False
