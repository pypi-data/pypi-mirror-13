from django.contrib import admin

from textplusstuff.admin import TextPlusStuffRegisteredModelAdmin

from .models import StacksImage, StacksImageList, StacksImageListImage


class StacksImageAdmin(TextPlusStuffRegisteredModelAdmin):
    exclude = ('image_ppoi', 'image_width', 'image_height')
    list_display = (
        'name',
        'display_title',
        'attribution',
        'date_created',
        'date_modified'
    )


class StacksImageListImageInline(admin.StackedInline):
    model = StacksImageListImage
    exclude = ('images',)


class StacksImageListAdmin(TextPlusStuffRegisteredModelAdmin):
    inlines = [StacksImageListImageInline]
    list_display = ('name', 'display_title', 'date_created', 'date_modified')

admin.site.register(StacksImage, StacksImageAdmin)
admin.site.register(StacksImageList, StacksImageListAdmin)
