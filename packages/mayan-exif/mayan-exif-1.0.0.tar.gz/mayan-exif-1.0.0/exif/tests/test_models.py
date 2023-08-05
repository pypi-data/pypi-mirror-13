from __future__ import unicode_literals

from django.core.files.base import File
from django.test import TestCase, override_settings

from documents.models import DocumentType
from documents.tests import TEST_DOCUMENT_TYPE

from ..models import DocumentVersionEXIFData

from .literals import TEST_SMALL_DOCUMENT_PATH


@override_settings(OCR_AUTO_OCR=False)
class DocumentVersionEXIFDataTestCase(TestCase):
    def setUp(self):
        self.document_type = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE
        )

        with open(TEST_SMALL_DOCUMENT_PATH) as file_object:
            self.document = self.document_type.new_document(
                file_object=File(file_object)
            )

    def tearDown(self):
        self.document_type.delete()

    def test_handler(self):
        exif_data = DocumentVersionEXIFData.objects.get(
            document_version=self.document.latest_version, tag='FileType'
        )

        self.assertEqual(exif_data.value, 'PNG')

    def test_model_str_method(self):
        self.assertEqual(
            unicode(self.document.latest_version.exif.get(tag='FileType')),
            'FileType: PNG'
        )
