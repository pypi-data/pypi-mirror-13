from __future__ import unicode_literals

from django.core.files import File
from django.test import override_settings

from common.tests.test_views import GenericViewTestCase
from documents.models import DocumentType
from documents.permissions import permission_document_view
from documents.tests import TEST_DOCUMENT_TYPE
from user_management.tests.literals import (
    TEST_USER_PASSWORD, TEST_USER_USERNAME
)

from .literals import TEST_SMALL_DOCUMENT_PATH


@override_settings(OCR_AUTO_OCR=False)
class DocumentsVersionEXIFViewsTestCase(GenericViewTestCase):
    def setUp(self):
        super(DocumentsVersionEXIFViewsTestCase, self).setUp()
        self.document_type = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE
        )

        with open(TEST_SMALL_DOCUMENT_PATH) as file_object:
            self.document = self.document_type.new_document(
                file_object=File(file_object)
            )

    def tearDown(self):
        super(DocumentsVersionEXIFViewsTestCase, self).tearDown()
        if self.document_type.pk:
            self.document_type.delete()

    def test_document_version_exit_view_no_permission(self):
        self.login(
            username=TEST_USER_USERNAME, password=TEST_USER_PASSWORD
        )

        response = self.get(
            'exif:document_version_exif_list',
            args=(self.document.latest_version.pk,)
        )
        self.assertEqual(response.status_code, 403)

    def test_document_version_exif_view_with_permission(self):
        self.login(
            username=TEST_USER_USERNAME, password=TEST_USER_PASSWORD
        )

        self.role.permissions.add(
            permission_document_view.stored_permission
        )
        response = self.get(
            'exif:document_version_exif_list',
            args=(self.document.latest_version.pk,), follow=True
        )
        self.assertContains(response, text='FileType', status_code=200)
