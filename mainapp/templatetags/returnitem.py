from django import template

register = template.Library()
@register.filter
def returnitem(l,i):
    try:
        return l[i-1]
    except:
        return None
    