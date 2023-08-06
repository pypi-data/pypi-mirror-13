# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals
from rest_framework import serializers
from .models import Text, Media


class TextSerializer(serializers.ModelSerializer):
    class Meta:
        model = Text

    # Attached medias urls
    media = serializers.ListField(
        child=serializers.URLField(required=True),
        required=False)

    def create(self, validated_data):
        """
        Create a new `Text` instance and it`s attached 'Media'
        instances, given the validated data, return new 'Text' instance
        """
        # Get media's urls
        urls = validated_data.pop('media', [])
        # Create Text instance
        new_text = Text(**validated_data)

        # Additional check: user must input text or add media url(s)
        if not (urls or new_text.text):
            raise serializers.ValidationError(
                "You must enter text or add media url(s)")
        else:
            new_text.save()

        # Create Media instances
        for url in urls:
            Media.objects.create_media(url=url, text=new_text)
        return new_text

    def to_representation(self, obj):
        """ Return details for `Text` instance and it`s attached `Media`
        """
        # Add Text data
        text = {'id':          obj.id,
                'author_name': obj.author_name,
                'author_url':  obj.author_url,
                'posted_at':   obj.posted_at,
                'text':        obj.text}
        # Create attached media's urls list
        urls = list()
        medias = obj.media.all()
        for media in medias:
            urls.append(media.url)
        text['media'] = urls
        return text
