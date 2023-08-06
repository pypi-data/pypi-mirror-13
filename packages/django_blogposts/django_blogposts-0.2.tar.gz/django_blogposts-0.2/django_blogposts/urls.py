# -*- coding: utf-8 -*-
__author__ = "spi4ka"
from django.conf.urls import url
from .views import PagesListView, PagesDetailView


urlpatterns = [
    url(
        r'^$',
        PagesListView.as_view(),
        name="django-blogposts-list",
    ),

    url(
        r'^(?P<pk>\d+)/(?P<slug>[^\.]+)/$',
        PagesDetailView.as_view(),
        name="django-blogposts-detail",
    )
]
