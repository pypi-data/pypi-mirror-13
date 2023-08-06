# -*- coding: utf-8 -*-
__author__ = "spi4ka"
from django import template
from ..models import BlogPost

register = template.Library()


@register.inclusion_tag('django_blogposts/list-item.html')
def blogpost_list_item(page, position="left"):
    return {
        'object': page,
        'position': position
    }
