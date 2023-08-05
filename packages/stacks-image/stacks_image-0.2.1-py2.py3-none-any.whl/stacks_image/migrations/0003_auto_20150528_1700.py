# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stacks_image', '0002_auto_20150402_1441'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stacksimagelistimage',
            name='date_created',
        ),
        migrations.RemoveField(
            model_name='stacksimagelistimage',
            name='date_modified',
        ),
        migrations.AddField(
            model_name='stacksimage',
            name='display_title',
            field=models.CharField(default='Foo', help_text='The displayed-to-the-user title of this content.', max_length=100, verbose_name='Display Title'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stacksimagelist',
            name='display_title',
            field=models.CharField(default='Foo', help_text='The displayed-to-the-user title of this content.', max_length=100, verbose_name='Display Title'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stacksimagelist',
            name='name',
            field=models.CharField(default='Foo', help_text='The internal name/signifier of this content.', max_length=100, verbose_name='Name'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='stacksimage',
            name='name',
            field=models.CharField(help_text='The internal name/signifier of this content.', max_length=100, verbose_name='Name'),
        ),
    ]
