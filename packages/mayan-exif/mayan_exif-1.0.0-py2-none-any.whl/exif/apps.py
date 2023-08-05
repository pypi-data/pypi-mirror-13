from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from common import menu_object
from common.apps import MayanAppConfig
from documents.models import Document, DocumentVersion
from documents.signals import post_version_upload

from navigation import SourceColumn

from .classes import DocumentEXIFHelper, DocumentVersionEXIFHelper
from .handlers import extract_exif
from .links import link_document_version_exif_list
from .models import DocumentVersionEXIFData


class EXIFApp(MayanAppConfig):
    name = 'exif'
    test = True
    verbose_name = _('Document EXIF data')

    def ready(self):
        super(EXIFApp, self).ready()

        Document.add_to_class(
            'exif_value_of', DocumentEXIFHelper.constructor
        )

        DocumentVersion.add_to_class(
            'exif_value_of', DocumentVersionEXIFHelper.constructor
        )

        SourceColumn(
            source=DocumentVersionEXIFData, label=_('Tag'),
            attribute='tag'
        )

        SourceColumn(
            source=DocumentVersionEXIFData, label=_('Value'),
            attribute='value'
        )

        menu_object.bind_links(
            links=(link_document_version_exif_list,),
            sources=(DocumentVersion,)
        )

        # Extract EXIF data of each newly created document version
        post_version_upload.connect(
            extract_exif, dispatch_uid='extract_exif',
            sender=DocumentVersion
        )
