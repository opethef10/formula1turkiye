from numbers import Number

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
import markdown

register = template.Library()

@register.filter
@stringfilter
def render_markdown(value):
    md = markdown.Markdown(extensions=["fenced_code"])
    return mark_safe(md.convert(value))

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


@register.filter
def with_currency(obj, currency="₺"):
    if not isinstance(obj, Number):
        return ""
    return f"{obj}{currency}"
