from __future__ import unicode_literals

from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _


class DocumentVersionEXIFHelper(object):
    @staticmethod
    @property
    def constructor(source_object):
        return DocumentVersionEXIFHelper(source_object)

    def __init__(self, instance):
        self.instance = instance

    def __getattr__(self, tag):
        try:
            return self.instance.exif.get(tag=tag).value
        except ObjectDoesNotExist:
            raise AttributeError(
                _('EXIF Tag \'%s\' not found') % tag
            )


class DocumentEXIFHelper(DocumentVersionEXIFHelper):
    @staticmethod
    @property
    def constructor(source_object):
        return DocumentEXIFHelper(source_object)

    def __init__(self, instance):
        self.instance = instance.latest_version
