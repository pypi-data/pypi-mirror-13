"""
media model-definitions

"""


import os

from PIL import Image as PillowImage

from django.conf import settings
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _


# media-files locations:
IMAGE_UPLOAD_DIR = os.path.join('img', '%Y', '%m')
DOCUMENT_UPLOAD_DIR = os.path.join('doc', '%Y', '%m')

IMAGE_WIDTHS = (
    (0, _('original')),
    (150, '150 px'),
    (300, '300 px'),
    (450, '450 px'),
    (600, '600 px'),
)
IMAGE_WIDTH_DEFAULT = 0


class ImageCollection(models.Model):
    """
    Group images to collections.
    Convenient for handling a large amount of images in the backend.
    """
    name = models.CharField(
        _('Name'),
        max_length=100,
        unique=True,
        default='')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Image(models.Model):
    """
    Images should be referenceable by name.
    Therefor names have to be unique.
    """
    collection = models.ForeignKey(
        'ImageCollection',
        verbose_name=_('Collection'))

    img = models.ImageField(
        _('Image-File'),
        upload_to=IMAGE_UPLOAD_DIR)

    name = models.CharField(
        _('Name'),
        max_length=200,
        db_index=True,
        default='')

    target_width = models.IntegerField(
        _('Width'),
        choices=IMAGE_WIDTHS,
        default=IMAGE_WIDTH_DEFAULT)

    def __str__(self):
        return self.name

    @property
    def size(self):
        try:
            return filesizeformat(self.img.size)
        except FileNotFoundError:
            return None

    @property
    def url(self):
        return self.img.url

    @property
    def width(self):
        try:
            return self.img.width
        except FileNotFoundError:
            return None

    @property
    def height(self):
        try:
            return self.img.height
        except FileNotFoundError:
            return None

    def preview(self):
        try:
            width = self.img.width
            height = self.img.height
        except FileNotFoundError:
            html = 'No Image'
        else:
            f = 80.0 / max(width, height)
            width *= f
            height *= f
            html = '<img src="{0}" width="{1}" height="{2}" />'.format(
                self.url, width, height)
        return html

    preview.allow_tags = True

    def save(self, **kwargs):
        """handle pre_save and post_save actions."""
        self._remember_previous_image()
        super().save(**kwargs)
        self._scale_image()
        self._unlink_previous_image()

    def _scale_image(self):
        """Scales an image to the target-size."""
        if not self.target_width:
            # 0: leave image as is
            return
        f = self.target_width / self.width
        height = int(self.height * f)
        size = (self.target_width, height)
        try:
            img = PillowImage.open(self.img.path)
        except IOError:
            # should not happen - do nothing
            return
        img.thumbnail(size, PillowImage.ANTIALIAS)
        img.save(self.img.path)

    def _remember_previous_image(self):
        """On exchanging an existing image remember the old one."""
        if not self.pk:
            # new dataset
            self._previous_img = None
        else:
            original = Image.objects.get(pk=self.pk)
            self._previous_img = original.img

    def _unlink_previous_image(self):
        """Avoid orphans: remove optional previous image."""
        if self._previous_img:
            if self._previous_img.name != self.img.name:
                self._previous_img.delete(save=False)


@receiver(post_delete, sender=Image)
def delete_image_handler(sender, **kwargs):
    """
    Remove an image-file from the disk if the corresponding media-db
    entry is deleted.
    """
    instance = kwargs.get('instance')
    instance.img.delete(save=False)


class DocumentCollection(models.Model):
    """
    Group documents to collections.
    Convenient for handling a large amount of documents in the backend.
    """
    name = models.CharField(
        _('Name'),
        max_length=100,
        unique=True,
        default='')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Document(models.Model):
    """
    Stores Information about an uploaded document.
    """
    collection = models.ForeignKey(
        'DocumentCollection',
        verbose_name=_('Collection'))

    doc = models.FileField(
        _('Document-File'),
        upload_to=DOCUMENT_UPLOAD_DIR)

    name = models.CharField(
        _('Name'),
        max_length=200,
        db_index=True,
        default='')

    def __str__(self):
        return self.name

    @property
    def size(self):
        try:
            return filesizeformat(self.doc.size)
        except FileNotFoundError:
            return None

    @property
    def url(self):
        return self.doc.url

    def save(self, **kwargs):
        self._remember_previous_doc()
        super().save(**kwargs)
        self._unlink_previous_doc()

    def _remember_previous_doc(self):
        """
        Remember the last doc-file in case a new one gets uploaded for
        this dataset.
        """
        if not self.pk:
            # new dataset
            self._previous_doc = None
        else:
            original = Document.objects.get(pk=self.pk)
            self._previous_doc = original.doc

    def _unlink_previous_doc(self):
        """Avoid orphans: remove optional previous document."""
        if self._previous_doc:
            if self._previous_doc.url != self.doc.url:
                self._previous_doc.delete(save=False)


@receiver(post_delete, sender=Document)
def delete_document_handler(sender, **kwargs):
    """
    Removes a file from the disk if the corresponding media-db
    entry is deleted.
    """
    instance = kwargs.get('instance')
    instance.doc.delete(save=False)
