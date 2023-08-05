from __future__ import unicode_literals

from django.conf import settings

from rest_framework import serializers
from textplusstuff.serializers import (
    ExtraContextSerializerMixIn,
    TextPlusStuffFieldSerializer
)
from versatileimagefield.serializers import VersatileImageFieldSerializer

from .models import StacksImage, StacksImageList

image_sets = getattr(
    settings,
    'VERSATILEIMAGEFIELD_RENDITION_KEY_SETS',
    {}
).get(
    'stacks_image',
    [
        ('full_size', 'url'),
        ('gallery_thumb', 'crop__400x225'),
        ('3up_thumb', 'crop__700x394'),
        ('2up_thumb', 'crop__800x450'),
        ('full_width', 'crop__1600x901'),
    ]
)


class StacksImageSerializer(ExtraContextSerializerMixIn,
                            serializers.ModelSerializer):
    """Serializes StacksImage instances"""
    image = VersatileImageFieldSerializer(
        sizes=image_sets
    )
    optional_content = TextPlusStuffFieldSerializer()

    class Meta:
        model = StacksImage
        fields = (
            'name',
            'display_title',
            'image',
            'optional_content',
            'attribution'
        )


class StacksImageListSerializer(ExtraContextSerializerMixIn,
                                serializers.ModelSerializer):
    images = serializers.SerializerMethodField()

    class Meta:
        model = StacksImageList
        fields = ('name', 'display_title', 'images')

    def get_images(self, obj):
        """Order `images` field properly."""
        images = obj.images.order_by('stacksimagelistimage__order')
        images = StacksImageSerializer(images, many=True)
        return images.data
