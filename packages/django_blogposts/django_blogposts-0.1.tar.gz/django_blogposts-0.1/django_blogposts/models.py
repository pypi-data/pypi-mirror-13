# -*- coding: utf-8 -*-
__author__ = "spi4ka"
from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from pytils.translit import translify


class BlogPost(models.Model):

    meta_title = models.CharField(_("Meta-tag title"), max_length=400)
    meta_kw = models.CharField(_("Meta-tag keywords"), max_length=400)
    meta_desc = models.TextField(_("Meta-tag Description"))

    slug = models.SlugField(_("Slug"), max_length=100, null=True, blank=True)

    header = models.CharField(_("Header (tag H1)"), max_length=400)
    short_content = models.TextField(_("Short content for preview"))
    content = models.TextField(_("Content"))

    image = models.ImageField(_("Image"), upload_to="blog/%Y/%m/%d")

    is_moderated = models.BooleanField(_("Is moderated"), default=True)

    da = models.DateTimeField(_("Date of create"), auto_now_add=True)
    de = models.DateTimeField(_("Date of last edit"), auto_now=True)

    class Meta:
        verbose_name = "Blog post"
        verbose_name_plural = "Blog posts"
        ordering = ['-da']

    def __unicode__(self):
        return u"{}".format(self.__str__(),)

    def __str__(self):
        return self.header

    def get_absolute_url(self):
        return reverse('django-blogposts-detail', args=(self.pk, self.slug,))

    def save(self, *args, **kwargs):
        slug = self.slug
        if not slug:
            self.slug = slugify(translify(self.header))

        return super(BlogPost, self).save(*args, **kwargs)
