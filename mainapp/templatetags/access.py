from django import template

register = template.Library()
@register.filter
def access(l,i):
    try:
        return l[i]
    except:
        return None
