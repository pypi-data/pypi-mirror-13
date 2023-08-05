# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import textplusstuff.fields
import versatileimagefield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='StacksImage',
            fields=[
                (
                    'id',
                    models.AutoField(
                        verbose_name='ID',
                        serialize=False,
                        auto_created=True,
                        primary_key=True
                    )
                ),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                (
                    'name',
                    models.CharField(
                        help_text='The name of this image.',
                        max_length=100,
                        verbose_name='Name'
                    )
                ),
                (
                    'image',
                    versatileimagefield.fields.VersatileImageField(
                        upload_to=b'stacks_image/'
                    )
                ),
                (
                    'image_ppoi',
                    versatileimagefield.fields.PPOIField(
                        default='0.5x0.5',
                        max_length=20
                    )
                ),
                (
                    'optional_content',
                    textplusstuff.fields.TextPlusStuffField(
                        help_text='A field to enter optional accompanying '
                                  'content. Example uses: captions, credits '
                                  'or accompanying content.',
                        verbose_name='Optional Content',
                        blank=True
                    )
                ),
            ],
            options={
                'verbose_name': 'Stacks Image',
                'verbose_name_plural': 'Stacks Images',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StacksImageList',
            fields=[
                (
                    'id',
                    models.AutoField(
                        verbose_name='ID',
                        serialize=False,
                        auto_created=True,
                        primary_key=True
                    )
                ),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                (
                    'list_name',
                    models.CharField(
                        help_text='The name of this image list.',
                        max_length=100,
                        verbose_name='List Name'
                    )
                ),
            ],
            options={
                'verbose_name': 'Stacks Image List',
                'verbose_name_plural': 'Stacks Image List',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StacksImageListImage',
            fields=[
                (
                    'id',
                    models.AutoField(
                        verbose_name='ID',
                        serialize=False,
                        auto_created=True,
                        primary_key=True
                    )
                ),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('order', models.PositiveIntegerField()),
                ('image', models.ForeignKey(to='stacks_image.StacksImage')),
                (
                    'image_list',
                    models.ForeignKey(to='stacks_image.StacksImageList')
                ),
            ],
            options={
                'ordering': ('order',),
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='stacksimagelist',
            name='images',
            field=models.ManyToManyField(
                to='stacks_image.StacksImage',
                through='stacks_image.StacksImageListImage'
            ),
            preserve_default=True,
        ),
    ]
