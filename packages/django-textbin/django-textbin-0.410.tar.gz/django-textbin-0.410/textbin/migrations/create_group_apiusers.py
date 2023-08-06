# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals
from django.db import migrations
from django.contrib.auth.models import Group


def create_group_apiusers(apps, schema_editor):
    # Create group for api-users
    Group.objects.create(name='api-users')


class Migration(migrations.Migration):

    # dependencies = [("auth", "0001_initial")]
    dependencies = [("textbin", "0001_initial")]

    operations = [
        migrations.RunPython(create_group_apiusers),
    ]