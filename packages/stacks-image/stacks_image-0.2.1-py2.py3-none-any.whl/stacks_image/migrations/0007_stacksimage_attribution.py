# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stacks_image', '0006_auto_20150529_2033'),
    ]

    operations = [
        migrations.AddField(
            model_name='stacksimage',
            name='attribution',
            field=models.CharField(help_text='The source/attribution of this image.', max_length=200, verbose_name='Source / Attribution', blank=True),
        ),
    ]
