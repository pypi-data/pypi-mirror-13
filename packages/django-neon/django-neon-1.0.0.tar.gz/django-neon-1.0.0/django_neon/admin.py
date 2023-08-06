
from django.contrib import admin
# from django.utils.translation import ugettext as _

from .models.media import (
    Document,
    DocumentCollection,
    Image,
    ImageCollection,
)
from .models.page import Page
from .models.pane import (
    Section,
    Pane
)


class SectionAdmin(admin.ModelAdmin):
    list_display = ('name', )


class PaneAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'screen': ('/static/css/backend.css',),
            }
    list_display = (
        'name',
        'page',
        'is_active',
        'publish_from',
        'publish_until',
        'order_id', )
    list_editable = ('order_id', 'is_active')
    list_filter = ('is_active', 'page')
    fields = (
        'name',
        ('page', 'section'),
        'is_active',
        ('publish_from', 'publish_until'),
        'order_id',
        'content',
        'markup',
        'use_mediadb',
    )


class PageAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = (
        'name', 'parent', 'sibling_id', 'is_active', )
    list_editable = ('sibling_id', 'is_active')
    list_filter = ('is_active', )
    fieldsets = (
        (None, {
            'fields': (
                'parent',
                'name',
                'template_name',
                'is_active',
                ('publish_from', 'publish_until'),
                'sibling_id')
        }),
        ('Meta-tags & Slug', {
            'classes': ('collapse',),
            'fields': ('description', 'slug')
        }),
    )


class ImageCollectionAdmin(admin.ModelAdmin):
    pass


class ImageAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'width',
        'height',
        'preview',
        'size')
    list_filter = ('collection', )


class DocumentCollectionAdmin(admin.ModelAdmin):
    pass


class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'size',
        'url')
    list_filter = ('collection', )


admin.site.register(Document, DocumentAdmin)
admin.site.register(DocumentCollection, DocumentCollectionAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(ImageCollection, ImageCollectionAdmin)
admin.site.register(Pane, PaneAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(Section, SectionAdmin)
