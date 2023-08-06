# -*- coding: utf-8 -*-
__author__ = "spi4ka"
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.http import Http404
from .models import BlogPost


class PagesListView(ListView):

    model = BlogPost

    model_fields = ['pk', 'header', 'short_content', 'image', 'da']

    paginate_by = 10

    template_name = "django_blogposts/list.html"

    def get_queryset(self):
        return self.model.objects.filter(
            is_moderated=True
        ).only(*self.model_fields)


class PagesDetailView(DetailView):

    model = BlogPost

    template_name = "django_blogposts/detail.html"

    def get_object(self):
        try:
            page = self.model.objects.get(pk=self.kwargs.get('pk'))
        except:
            raise Http404
        return page
