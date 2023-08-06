# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.forms import ModelForm, forms
from django.forms.models import inlineformset_factory

from snowpenguin.django.recaptcha2.fields import ReCaptchaField
from snowpenguin.django.recaptcha2.widgets import ReCaptchaWidget
# from captcha.fields import ReCaptchaField

from .models import Text, Media


class TextForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(TextForm, self).__init__(*args, **kwargs)
        # Установка widget label, placeholder
        for field_name in self.fields:
            placeholder = Text.widget_placeholders[field_name]
            label = Text.widget_labels[field_name]
            self.fields[field_name].widget.attrs['placeholder'] = placeholder
            self.fields[field_name].label = label

    class Meta:
        model = Text
        fields = ['author_name', 'author_url', 'text']
        # exclude = ['id', 'posted_at']


class MediaInline(ModelForm):
    class Meta:
        model = Media
        fields = ['url']


MediaFormSet = inlineformset_factory(Text,
                                     Media,
                                     form=MediaInline,
                                     extra=1,
                                     can_delete=False,
                                     can_order=False)


class CaptchaForm(forms.Form):
    captcha = ReCaptchaField(widget=ReCaptchaWidget())
    # captcha = ReCaptchaField(attrs={'theme': 'clean'})
