# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stacks_image', '0005_remove_stacksimagelist_list_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stacksimage',
            name='display_title',
            field=models.CharField(help_text='An optional displayed-to-the-user title of this content.', max_length=100, verbose_name='Display Title', blank=True),
        ),
        migrations.AlterField(
            model_name='stacksimagelist',
            name='display_title',
            field=models.CharField(help_text='An optional displayed-to-the-user title of this content.', max_length=100, verbose_name='Display Title', blank=True),
        ),
    ]
