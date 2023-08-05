# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stacks_image', '0004_auto_20150528_1701'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stacksimagelist',
            name='list_name',
        ),
    ]
