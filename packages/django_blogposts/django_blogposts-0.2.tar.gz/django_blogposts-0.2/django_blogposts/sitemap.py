# -*- coding: utf-8 -*-
__author__ = "spi4ka"
from django.contrib.sitemaps import Sitemap
from .models import BlogPost


class BlogPostSitemap(Sitemap):

    def items(self):
        return BlogPost.objects.filter(is_moderated=True)

    def lastmod(self, obj):
        return obj.de
