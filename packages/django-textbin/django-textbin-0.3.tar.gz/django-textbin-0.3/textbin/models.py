# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals
import six
import random
import string
import urllib
from collections import defaultdict

from django.db import models
from django.core.exceptions import ObjectDoesNotExist, FieldError
from django.utils.encoding import python_2_unicode_compatible
from django.core.exceptions import ValidationError

# Length of unique hex-key for every text
ID_LENGTH = 10


def _unique_id():
    """ Returns unique ID for Text.id """
    check_field = 'id'
    model = Text
    new_id = None
    while True:
        new_id = ''.join(random.choice(
            string.ascii_letters + string.digits) for _ in range(ID_LENGTH))
        try:
            model.objects.get(**{check_field: new_id})
        except ObjectDoesNotExist as err:
            # ID is unique
            break
    return new_id


class MediaType(object):
    IMAGE = 1
    VIDEO = 2
    CHOICES = (
        (IMAGE, 'Image'),
        (VIDEO, 'Video'),
    )

    @classmethod
    def autodetect(cls, url):
        if not url:
            raise ValueError('Unable to autodetect media type: url is False.')
        res = urllib.urlopen(url)
        http_message = res.info()
        # full = http_message.type    # 'text/plain'
        curr_type = http_message.maintype  # 'text'
        curr_type = curr_type.capitalize()
        for choise in cls.CHOICES:
            if curr_type == choise[1]:
                return choise[0]
        # If content type not in cls.CHOICES
        raise FieldError('Not supported content type at ' + url)


def valid_url_media(url):
    try:
        MediaType.autodetect(url)
    except FieldError:
        raise ValidationError('URL must point to one of this: %s'
                              % ', '.join([ch[1] for ch in MediaType.CHOICES]))


@python_2_unicode_compatible
class Text(models.Model):
    len_author = 100  # max length of author_name CharField
    def_author = 'Anonymous'  # Default author name

    id = models.CharField(max_length=ID_LENGTH, primary_key=True,
                          # default=objects.unique_id,
                          default=_unique_id,
                          editable=False)
    text = models.TextField(default='',
                            blank=True)

    posted_at = models.DateTimeField(auto_now_add=True)
    author_name = models.CharField(max_length=len_author,
                                   default=def_author,
                                   blank=True)
    author_url = models.URLField(blank=True,
                                 default='')

    # Параметры отображения в форме
    widget_labels = dict()
    widget_labels['text'] = 'Текст сообщения'
    widget_labels['author_name'] = 'Ваше имя'
    widget_labels['author_url'] = 'Домашняя страница'

    widget_placeholders = defaultdict(lambda: '')
    # Не указанные в словаре поля будут иметь пустую строку placeholder
    widget_placeholders['text'] = 'Введите текст'

    @property
    def images(self):
        return self.media_set.filter(type=MediaType.IMAGE)

    @property
    def videos(self):
        return self.media_set.filter(type=MediaType.VIDEO)

    def __str__(self):
        return self.id


class MediaManager(models.Manager):
    def create_media(self, text, url, type=None):
        # Create Media instance with content type autodetection from url (if
        # not specified)
        if not type:
            type = MediaType.autodetect(url)
        media = self.create(text=text, url=url, type=type)
        return media


@python_2_unicode_compatible
class Media(models.Model):
    # Objects manager
    objects = MediaManager()

    # Objects attributes
    text = models.ForeignKey(Text,
                             editable=False,
                             verbose_name='Attached to',
                             on_delete=models.CASCADE,
                             related_name='media')
    type = models.SmallIntegerField(choices=MediaType.CHOICES)
    url = models.URLField(blank=False,
                          max_length=2000,
                          validators=[valid_url_media, ])

    def __str__(self):
        return six.text_type(self.pk)
