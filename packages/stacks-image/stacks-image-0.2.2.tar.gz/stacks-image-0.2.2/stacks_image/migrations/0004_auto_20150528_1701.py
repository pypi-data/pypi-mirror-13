# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def populate_display_title(apps, schema_editor):
    """
    Populates display_title on both StacksImage and StacksImageList
    """
    StacksImage = apps.get_model("stacks_image", "StacksImage")
    for embed in StacksImage.objects.all():
        embed.display_title = embed.name
        embed.save()

    StacksImageList = apps.get_model("stacks_image", "StacksImageList")
    for image_list in StacksImageList.objects.all():
        image_list.name = image_list.list_name
        image_list.display_title = image_list.list_name
        image_list.save()


class Migration(migrations.Migration):

    dependencies = [
        ('stacks_image', '0003_auto_20150528_1700'),
    ]

    operations = [
        migrations.RunPython(
            populate_display_title,
        )
    ]
