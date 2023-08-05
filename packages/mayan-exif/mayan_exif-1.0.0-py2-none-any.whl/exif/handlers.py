from __future__ import unicode_literals

from .models import DocumentVersionEXIFData


def extract_exif(sender, instance, **kwargs):
    """Extract EXIF data of each newly created document version"""
    DocumentVersionEXIFData.objects.process_version(document_version=instance)
