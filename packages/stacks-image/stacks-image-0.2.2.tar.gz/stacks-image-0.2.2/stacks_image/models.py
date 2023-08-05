from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from textplusstuff.fields import TextPlusStuffField
from versatileimagefield.fields import VersatileImageField, PPOIField


class StacksImageBase(models.Model):
    """
    An abstract base model that keeps track of when a model instance
    was created and last-updated.
    """
    date_created = models.DateTimeField(
        auto_now_add=True
    )
    date_modified = models.DateTimeField(
        auto_now=True
    )
    name = models.CharField(
        _('Name'),
        max_length=100,
        help_text=_('The internal name/signifier of this content.')
    )
    display_title = models.CharField(
        _('Display Title'),
        max_length=100,
        help_text=_(
            'An optional displayed-to-the-user title of this content.'
        ),
        blank=True
    )

    class Meta:
        abstract = True


@python_2_unicode_compatible
class StacksImage(StacksImageBase):
    """Represents an image."""
    image = VersatileImageField(
        upload_to='stacks_image/',
        width_field='width',
        height_field='height',
        ppoi_field='image_ppoi',
        max_length=300
    )
    image_ppoi = PPOIField()

    height = models.PositiveIntegerField(
        blank=True,
        null=True
    )
    width = models.PositiveIntegerField(
        blank=True,
        null=True
    )
    optional_content = TextPlusStuffField(
        _('Optional Content'),
        blank=True,
        help_text=_(
            "A field to enter optional accompanying content. Example uses: "
            "captions, credits or accompanying content."
        )
    )
    attribution = models.CharField(
        _('Source / Attribution'),
        max_length=200,
        blank=True,
        help_text=_('The source/attribution of this image.')
    )

    class Meta:
        verbose_name = _('Stacks Image')
        verbose_name_plural = _('Stacks Images')

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class StacksImageList(StacksImageBase):
    """Represents a list of StacksImage instances."""

    images = models.ManyToManyField(
        StacksImage,
        through='StacksImageListImage'
    )

    class Meta:
        verbose_name = _('Stacks Image List')
        verbose_name_plural = _('Stacks Image List')

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class StacksImageListImage(models.Model):
    """
    A through table for connecting StacksImage instances to StacksImageList
    instances.
    """
    image_list = models.ForeignKey(
        StacksImageList
    )
    order = models.PositiveIntegerField()
    image = models.ForeignKey(
        StacksImage
    )

    class Meta:
        ordering = ('order',)

    def __str__(self):
        return "{} {}. {}".format(
            self.image_list.name,
            self.order,
            self.image.name,
        )
