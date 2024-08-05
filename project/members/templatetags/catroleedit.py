from django import template

register = template.Library()

@register.filter
def categoryparser(categoryString):
    trimmedString = categoryString[1:-1]
    return trimmedString

@register.filter
def roleparser(roleString):
    trimmedString = roleString[1:-1]
    return trimmedString