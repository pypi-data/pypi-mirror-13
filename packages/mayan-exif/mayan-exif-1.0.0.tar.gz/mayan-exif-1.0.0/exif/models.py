from __future__ import unicode_literals

import logging

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from documents.models import DocumentVersion

from .managers import DocumentVersionEXIFDataManager

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class DocumentVersionEXIFData(models.Model):
    """
    Model to store an EXIF tag and value for a document version.
    """

    document_version = models.ForeignKey(
        DocumentVersion, related_name='exif',
        verbose_name=_('Document version')
    )

    tag = models.CharField(max_length=255, verbose_name=_('Tag'))
    value = models.CharField(max_length=255, verbose_name=_('Value'))

    objects = DocumentVersionEXIFDataManager()

    class Meta:
        verbose_name = _('Document version EXIF data')
        verbose_name_plural = _('Document versions EXIF data')

    def __str__(self):
        return '{}: {}'.format(self.tag, self.value)
