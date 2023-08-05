from __future__ import unicode_literals

from django.core.files.base import File
from django.test import TestCase, override_settings

from documents.models import DocumentType
from documents.tests import TEST_DOCUMENT_TYPE

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

    def test_accessor(self):
        self.assertEqual(
            self.document.latest_version.exif_value_of.FileType, 'PNG'
        )

        self.assertEqual(
            self.document.exif_value_of.FileType, 'PNG'
        )

    def test_invalid_tag(self):
        with self.assertRaises(AttributeError):
            self.document.exif_value_of.InvalidTag
