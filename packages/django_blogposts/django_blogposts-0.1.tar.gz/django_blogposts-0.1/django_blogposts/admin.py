# -*- coding: utf-8 -*-
__author__ = "spi4ka"
from django.contrib import admin
from .models import BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    pass
