# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals
import os

from django.test import TestCase
from django.core.urlresolvers import reverse

from rest_framework.test import APITestCase
from rest_framework import status

from .models import Text

# app_nape / namespace - used to get urls
app_name = 'textbin'
# disable the recaptcha field and let test works
os.environ['RECAPTCHA_DISABLE'] = 'True'


class UrlsTestCase(APITestCase):
    """ Тесты доступа к URL по имени протсранства имён и именам URL
    """
    msg = "Message in the test post"   # message in Text instance`s .text field
    text = None                        # Text instance

    @classmethod
    def setUpClass(cls):
        """ Создание тестового поста
        """
        super(UrlsTestCase, cls).setUpClass()
        cls.text = Text.objects.create(text=cls.msg)

    def check_response_status(self, url, status):
        """ вспомогательная функция
        """
        response = self.client.get(url)
        self.assertEqual(response.status_code, status)

    def test_get_url_text_create(self):
        """ Форма создания поста
        """
        self.check_response_status(
            reverse('%s:text_create' % app_name),
            status.HTTP_200_OK)

    def test_get_url_text_api_create(self):
        """ Открывается как запрос GET, который запрещён (запрос всех постов)
        Статус должен быть - 405
        """
        self.check_response_status(
            reverse('%s:text_api_create' % app_name),
            status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_url_text_detail(self):
        url = '%s:text_detail' % app_name
        response = self.client.get(reverse(url,
                                           args=(self.text,)))
        self.assertTrue(self.msg.encode() in response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ApiTextCreate(APITestCase):
    """
    Тесты REST API - создание поста
    """
    def test_api_text_create_only_text(self):
        """ Содание поста POST-запросом по url REST API
        Заполняются  поля `текст` и `автор`
        """
        msg = 'API-test: creating text'
        author = 'UnitTest'
        url = reverse('%s:text_api_create' % app_name)
        response = self.client.post(url, {"text": msg,
                                          "author_name": author})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_api_text_create_only_url(self):
        """ Содание поста POST-запросом по url REST API
        Заполняется только поле `media` - прикрепляется изображение.
        Автор - по умолчанию - Anonymous
        """
        media = 'http://s.smmplanner.com/favicon.ico'
        url = reverse('%s:text_api_create' % app_name)
        response = self.client.post(url, {"media": [media, ], })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_api_text_create_no_content(self):
        """ Содание поста POST-запросом по url REST API
        Указывается только имя автора. Такие посты запрещены как пустые.
        """
        author = 'UnitTest'
        url = reverse('%s:text_api_create' % app_name)
        response = self.client.post(url, {"author_name": author})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_text_detail(self):
        """ Получение поста GET-запросом по url REST API
        """
        msg = 'API-test: fetching text'
        obj = Text.objects.create(text=msg)
        url = reverse('%s:text_api_detail' % app_name, args=(obj,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(msg.encode() in response.content)


class TextDetailTests(TestCase):
    """
    Тесты проверяющие отображение запрашиваемого поста

    Проверка выполняется по содержимому получаемой страницы в той или иной
    ситуации.
    """
    def test_detail_view(self):
        """ Запрос по id поста
        Создаётся пост с текстом. Запрашивается представление поста.
        Результат должен содержать текст поста
        """
        msg = 'Test-post created!'
        new_text = Text.objects.create(text=msg)
        response = self.client.get(reverse('%s:text_detail' % app_name,
                                           args=(new_text,)))
        self.assertTrue(msg.encode() in response.content)

    def test_detail_view_with_nonexist_text(self):
        """ Запрос по id поста который несуществует
        Результатотм такого запроса должна быть страница со статусом 404
        """
        response = self.client.get(reverse('%s:text_detail' % app_name,
                                           args=('abcdefgh',)))
        self.assertEqual(response.status_code, 404)
