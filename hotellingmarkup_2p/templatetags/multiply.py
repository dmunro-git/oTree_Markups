# app/templatetags/multiply.py
import random
from django import template
register = template.Library()

@register.filter
def multiply(value, arg):
    return value*arg