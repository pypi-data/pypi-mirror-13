# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import versatileimagefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('stacks_image', '0007_stacksimage_attribution'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stacksimage',
            name='image',
            field=versatileimagefield.fields.VersatileImageField(height_field=b'height', width_field=b'width', max_length=300, upload_to=b'stacks_image/'),
        ),
    ]
