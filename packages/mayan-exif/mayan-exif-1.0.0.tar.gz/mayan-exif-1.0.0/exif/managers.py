from __future__ import unicode_literals

import logging

from django.db import models
from django.utils.module_loading import import_string

from .settings import setting_exif_backend

logger = logging.getLogger(__name__)


class DocumentVersionEXIFDataManager(models.Manager):
    def process_version(self, document_version):
        backend_class = import_string(setting_exif_backend.value)
        backend = backend_class()

        for tag, value in backend.execute(document_version=document_version).items():
            self.create(
                document_version=document_version, tag=tag, value=value
            )
