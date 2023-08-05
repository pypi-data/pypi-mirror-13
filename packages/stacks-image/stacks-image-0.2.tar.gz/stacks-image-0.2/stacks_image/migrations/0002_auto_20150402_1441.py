# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import versatileimagefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('stacks_image', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='stacksimage',
            name='height',
            field=models.PositiveIntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stacksimage',
            name='width',
            field=models.PositiveIntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='stacksimage',
            name='image',
            field=versatileimagefield.fields.VersatileImageField(height_field=b'height', width_field=b'width', upload_to=b'stacks_image/'),
            preserve_default=True,
        ),
    ]
