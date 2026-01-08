"""
Custom template filters for CRM Nice.
"""
from django import template
from django.utils.safestring import mark_safe
import bleach

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


@register.filter(name='safe_html')
def safe_html(value):
    """
    Санітизує HTML та дозволяє безпечне виведення.
    Дозволяє: p, br, strong, em, u, h1-h3, ul, ol, li, a (з href), div
    Usage: {{ company.full_description|safe_html }}
    """
    if not value:
        return ''
    
    allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'ul', 'ol', 'li', 'a', 'div', 'span']
    allowed_attributes = {'a': ['href', 'title', 'target']}
    
    cleaned = bleach.clean(value, tags=allowed_tags, attributes=allowed_attributes, strip=True)
    return mark_safe(cleaned)

