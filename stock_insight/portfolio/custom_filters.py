from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiplies the value by the arg."""
    try:
        return value * arg
    except (TypeError, ValueError):
        return 0  # return 0 or handle the error as needed
