from django import template

register = template.Library()


@register.filter
def call_or_get_attr(obj, name):
    attr = getattr(obj, name, Ellipsis)
    if attr is Ellipsis:
        return ""
    if callable(attr):
        return attr()
    return attr


@register.filter
def index(indexable, i):
    try:
        return indexable[i]
    except IndexError:
        return ""
