from __future__ import unicode_literals

from django.core.files.base import File
from django.test import TestCase, override_settings

from documents.models import DocumentType, Document
from documents.tests import TEST_DOCUMENT_TYPE

from .literals import (
    TEST_SEQUENCE_LABEL, TEST_SEQUENCE_INCREMENT, TEST_SEQUENCE_INITIAL_VALUE,
    TEST_SEQUENCE_SLUG, TEST_SMALL_DOCUMENT_PATH, TEST_TEMPLATE
)

from ..models import Sequence


@override_settings(OCR_AUTO_OCR=False)
class SequenceTestCase(TestCase):
    def setUp(self):
        self.sequence = Sequence.objects.create(
            label=TEST_SEQUENCE_LABEL, slug=TEST_SEQUENCE_SLUG,
            increment=TEST_SEQUENCE_INCREMENT,
            value=TEST_SEQUENCE_INITIAL_VALUE
        )

    def tearDown(self):
        self.sequence.delete()

    def test_sequence_increment(self):
        self.assertEqual(self.sequence.value, TEST_SEQUENCE_INITIAL_VALUE)

        self.assertEqual(
            self.sequence.next_value(), TEST_SEQUENCE_INITIAL_VALUE
        )
        self.assertEqual(
            self.sequence.next_value(),
            TEST_SEQUENCE_INITIAL_VALUE + TEST_SEQUENCE_INCREMENT
        )

        self.assertEqual(
            self.sequence.value,
            TEST_SEQUENCE_INITIAL_VALUE + TEST_SEQUENCE_INCREMENT +
            TEST_SEQUENCE_INCREMENT
        )


@override_settings(OCR_AUTO_OCR=False)
class RenamingTemplateTestCase(TestCase):
    def setUp(self):
        self.sequence = Sequence.objects.create(
            label=TEST_SEQUENCE_LABEL, slug=TEST_SEQUENCE_SLUG,
            increment=TEST_SEQUENCE_INCREMENT,
            value=TEST_SEQUENCE_INITIAL_VALUE
        )
        self.document_type = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE
        )
        self.document_type.renaming_template.template = TEST_TEMPLATE
        self.document_type.renaming_template.save()
        self.renaming_template = self.document_type.renaming_template

    def tearDown(self):
        self.document_type.delete()
        self.sequence.delete()

    def test_template_rendering(self):
        result = self.renaming_template.render_for(document=None)
        self.assertEqual(result, 'invoice-0')

        result = self.renaming_template.render_for(document=None)
        self.assertEqual(result, 'invoice-1')

    def test_rename_on_upload(self):
        with open(TEST_SMALL_DOCUMENT_PATH) as file_object:
            self.document = self.document_type.new_document(
                file_object=File(file_object)
            )

        document = Document.objects.get(pk=self.document.pk)
        self.assertEqual(document.label, 'invoice-0')
