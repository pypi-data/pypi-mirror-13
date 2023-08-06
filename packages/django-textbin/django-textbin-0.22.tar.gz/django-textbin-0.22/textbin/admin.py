from __future__ import print_function, division, absolute_import, unicode_literals

from django.contrib import admin
from django.template.defaultfilters import truncatechars

from . import models

# from utils.decorator import attrs
# ToDo: find utils package!


def attrs(**kwargs):
    def attrsetter(function):
        for key, value in kwargs.items():
            setattr(function, key, value)
        return function
    return attrsetter


class ImageInline(admin.StackedInline):
    model = models.Media
    extra = 1


@admin.register(models.Text)
class TextAdmin(admin.ModelAdmin):
    list_display = ('id', 'author_name', 'text_truncated')
    search_fields = ('id',)
    inlines = [ImageInline,]
    readonly_fields = ('id', )

    @staticmethod
    @attrs(short_description='text', admin_order_field='text')
    def text_truncated(obj):
        return truncatechars(obj.text, 140)


@admin.register(models.Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'text')
    readonly_fields = ('id',)
    search_fields = ('id',)
