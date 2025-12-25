"""
Custom template filters for CRM Nice.
"""
from django import template

register = template.Library()


@register.filter(name='remove')
def remove(value, arg):
    """
    Removes all occurrences of arg from value.
    Usage: {{ value|remove:"@" }}
    """
    try:
        if value is None:
            return ''
        if not isinstance(value, str):
            value = str(value)
        if arg is None:
            return value
        if not isinstance(arg, str):
            arg = str(arg)
        return value.replace(arg, '')
    except (AttributeError, TypeError):
        return value or ''

