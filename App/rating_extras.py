# templatetags/rating_extras.py
from django import template

register = template.Library()

@register.filter
def get_range(value):
    """Returns a range object for looping in templates."""
    return range(value)