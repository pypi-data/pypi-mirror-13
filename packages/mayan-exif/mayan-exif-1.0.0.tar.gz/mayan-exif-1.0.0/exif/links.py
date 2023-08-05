from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from documents.permissions import permission_document_view
from navigation import Link

link_document_version_exif_list = Link(
    permissions=(permission_document_view,), text=_('EXIF'),
    view='exif:document_version_exif_list', args='object.id'
)
