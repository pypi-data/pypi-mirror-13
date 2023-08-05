from __future__ import absolute_import, unicode_literals

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _

from acls.models import AccessControlList
from common.views import SingleObjectListView
from documents.models import DocumentVersion
from documents.permissions import permission_document_view
from permissions import Permission


class DocumentVersionEXIFListView(SingleObjectListView):
    def get_extra_context(self):
        return {
            'hide_object': True,
            'object': self.get_object(),
            'document': self.get_object().document,
            'navigation_object_list': ('object', 'document'),
            'title': _('EXIF data for: %s') % self.get_object(),
        }

    def get_object(self):
        document_version = get_object_or_404(
            DocumentVersion, pk=self.kwargs['pk']
        )

        try:
            Permission.check_permissions(
                self.request.user, (permission_document_view,)
            )
        except PermissionDenied:
            AccessControlList.objects.check_access(
                permission_document_view, self.request.user, document_version
            )

        return document_version

    def get_queryset(self):
        return self.get_object().exif.all()
