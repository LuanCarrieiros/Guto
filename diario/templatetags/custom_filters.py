from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Filtro para acessar valores de dicionário no template"""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

@register.filter
def default_if_none(value, default):
    """Retorna default se value for None"""
    return default if value is None else value