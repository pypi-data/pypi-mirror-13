from textplusstuff import registry

from .models import StacksImage, StacksImageList
from .serializers import StacksImageSerializer, StacksImageListSerializer


class StacksImageStuff(registry.ModelStuff):
    # The queryset used to retrieve instances of TestModel
    # within the front-end interface. For instance, you could
    # exclude 'unpublished' instances or anything else you can
    # query the ORM against
    queryset = StacksImage.objects.all()

    description = 'A single image with optional content.'

    # The serializer we just defined, this is what provides the context/JSON
    # payload for this Stuff
    serializer_class = StacksImageSerializer

    # All Stuff must have at least one rendition (specified in
    # the `renditions` attribute below) which basically
    # just points to a template and some human-readable metadata.
    # At present there are only two options for setting rendition_type:
    # either 'block' (the default) or inline. These will be used by
    # the front-end editor when placing tokens.
    renditions = [
        registry.Rendition(
            short_name='full_width',
            verbose_name="Full Width Image",
            description="An image that spans the full width of it's "
                        "containing div.",
            path_to_template='stacks_image/stacksimage/'
                             'stacksimage-full_width.html'
        ),
        registry.Rendition(
            short_name='image_left_content_right',
            verbose_name="Image Left, Content Right",
            description="Display an image on the left with it's accompanying "
                        "content on the right. NOTE: This rendition should "
                        "only be used if the 'Optional Content' field is "
                        "filled out.",
            path_to_template='stacks_image/stacksimage/'
                             'stacksimage-image_left_content_right.html'
        ),
        registry.Rendition(
            short_name='image_right_content_left',
            verbose_name="Image Right, Content Left",
            description="Display an image on the right with it's accompanying "
                        "content on the left. NOTE: This rendition should "
                        "only be used if the 'Optional Content' field is "
                        "filled out.",
            path_to_template='stacks_image/stacksimage/'
                             'stacksimage-image_right_content_left.html'
        )
    ]
    # The attributes used in the list (table) display of the front-end
    # editing tool.
    list_display = ('id', 'name')


class StacksImageListStuff(registry.ModelStuff):
    # The queryset used to retrieve instances of TestModel
    # within the front-end interface. For instance, you could
    # exclude 'unpublished' instances or anything else you can
    # query the ORM against
    queryset = StacksImageList.objects.prefetch_related(
        'stacksimagelistimage_set',
        'stacksimagelistimage_set__image'
    )

    description = 'A list of images with optional content.'
    serializer_class = StacksImageListSerializer

    # All Stuff must have at least one rendition (specified in
    # the `renditions` attribute below) which basically
    # just points to a template and some human-readable metadata.
    # At present there are only two options for setting rendition_type:
    # either 'block' (the default) or inline. These will be used by
    # the front-end editor when placing tokens.
    renditions = [
        registry.Rendition(
            short_name='1up',
            verbose_name="Image List 1-Up",
            description="A list of images displayed in grid with one image "
                        "in each row.",
            path_to_template='stacks_image/stacksimagelist/'
                             'stacksimagelist-1up.html'
        ),
        registry.Rendition(
            short_name='2up',
            verbose_name="Image List 2-Up",
            description="A list of images displayed in grid with two "
                        "in each row.",
            path_to_template='stacks_image/stacksimagelist/'
                             'stacksimagelist-2up.html'
        ),
        registry.Rendition(
            short_name='3up',
            verbose_name="Image List 3-Up",
            description="A list of images displayed in grid with three "
                        "in each row.",
            path_to_template='stacks_image/stacksimagelist/'
                             'stacksimagelist-3up.html'
        ),
        registry.Rendition(
            short_name='gallery',
            verbose_name="Image Gallery",
            description="A list of images displayed in a 4-up grid "
                        "that, when clicked, are displayed at full-size.",
            path_to_template='stacks_image/stacksimagelist/'
                             'stacksimagelist-gallery.html'
        ),
        registry.Rendition(
            short_name='carousel',
            verbose_name="Image Carousel",
            description="A list of images displayed in a javascript-powered "
                        "carousel.",
            path_to_template='stacks_image/stacksimagelist/'
                             'stacksimagelist-carousel.html'
        )
    ]
    # The attributes used in the list (table) display of the front-end
    # editing tool.
    list_display = ('id', 'list_name')


registry.stuff_registry.add_modelstuff(
    StacksImage,
    StacksImageStuff,
    groups=['stacks', 'image', 'media']
)

registry.stuff_registry.add_modelstuff(
    StacksImageList,
    StacksImageListStuff,
    groups=['stacks', 'image', 'media']
)
