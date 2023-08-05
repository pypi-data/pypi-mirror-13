from __future__ import unicode_literals

from django.test import override_settings

from common.tests.test_views import GenericViewTestCase
from documents.models import DocumentType
from documents.permissions import permission_document_type_view
from documents.tests import TEST_DOCUMENT_TYPE
from user_management.tests.literals import (
    TEST_USER_PASSWORD, TEST_USER_USERNAME
)

from ..models import Sequence
from ..permissions import (
    permission_sequence_create, permission_sequence_delete,
    permission_sequence_edit, permission_sequence_view,
    permission_renaming_template_edit
)

from .literals import (
    TEST_SEQUENCE_LABEL, TEST_SEQUENCE_LABEL_EDITED, TEST_SEQUENCE_INCREMENT,
    TEST_SEQUENCE_INITIAL_VALUE, TEST_SEQUENCE_SLUG, TEST_TEMPLATE,
    TEST_TEMPLATE_EDITED
)


@override_settings(OCR_AUTO_OCR=False)
class SequenceViewsTestCase(GenericViewTestCase):
    def test_sequence_creation_view_no_permission(self):
        self.login(
            username=TEST_USER_USERNAME, password=TEST_USER_PASSWORD
        )

        self.role.permissions.add(
            permission_sequence_view.stored_permission
        )
        response = self.post(
            'document_renaming:sequence_create',
            data={
                'label': TEST_SEQUENCE_LABEL,
                'slug': TEST_SEQUENCE_SLUG,
                'increment': TEST_SEQUENCE_INCREMENT,
                'value': TEST_SEQUENCE_INITIAL_VALUE,
            }, follow=True
        )
        self.assertEqual(response.status_code, 403)

    def test_sequence_creation_view_with_permission(self):
        self.login(
            username=TEST_USER_USERNAME, password=TEST_USER_PASSWORD
        )

        self.role.permissions.add(
            permission_sequence_create.stored_permission
        )
        self.role.permissions.add(
            permission_sequence_view.stored_permission
        )
        response = self.post(
            'document_renaming:sequence_create',
            data={
                'label': TEST_SEQUENCE_LABEL,
                'slug': TEST_SEQUENCE_SLUG,
                'increment': TEST_SEQUENCE_INCREMENT,
                'value': TEST_SEQUENCE_INITIAL_VALUE,
            }, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            Sequence.objects.all(),
            ('<Sequence: {}>'.format(TEST_SEQUENCE_LABEL),)
        )

    def test_sequence_delete_view_no_permission(self):
        self.login(
            username=TEST_USER_USERNAME, password=TEST_USER_PASSWORD
        )
        sequence = Sequence.objects.create(
            slug=TEST_SEQUENCE_SLUG, label=TEST_SEQUENCE_LABEL
        )

        self.role.permissions.add(
            permission_sequence_view.stored_permission
        )
        response = self.post(
            'document_renaming:sequence_delete', args=(sequence.pk,),
            follow=True
        )
        self.assertEqual(response.status_code, 403)

    def test_sequence_delete_view_with_permission(self):
        self.login(
            username=TEST_USER_USERNAME, password=TEST_USER_PASSWORD
        )
        sequence = Sequence.objects.create(
            slug=TEST_SEQUENCE_SLUG, label=TEST_SEQUENCE_LABEL
        )

        self.role.permissions.add(
            permission_sequence_delete.stored_permission
        )
        self.role.permissions.add(
            permission_sequence_view.stored_permission
        )
        response = self.post(
            'document_renaming:sequence_delete', args=(sequence.pk,),
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            Sequence.objects.all(), ()
        )

    def test_sequence_edit_view_no_permission(self):
        self.login(
            username=TEST_USER_USERNAME, password=TEST_USER_PASSWORD
        )
        sequence = Sequence.objects.create(
            slug=TEST_SEQUENCE_SLUG, label=TEST_SEQUENCE_LABEL
        )

        self.role.permissions.add(
            permission_sequence_view.stored_permission
        )
        response = self.post(
            'document_renaming:sequence_edit', args=(sequence.pk,),
            data={
                'label': TEST_SEQUENCE_LABEL_EDITED,
                'slug': TEST_SEQUENCE_SLUG,
                'increment': TEST_SEQUENCE_INCREMENT,
                'value': TEST_SEQUENCE_INITIAL_VALUE
            }, follow=True
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(sequence.label, TEST_SEQUENCE_LABEL)

    def test_sequence_edit_view_with_permission(self):
        self.login(
            username=TEST_USER_USERNAME, password=TEST_USER_PASSWORD
        )
        sequence = Sequence.objects.create(
            slug=TEST_SEQUENCE_SLUG, label=TEST_SEQUENCE_LABEL
        )

        self.role.permissions.add(
            permission_sequence_edit.stored_permission
        )
        self.role.permissions.add(
            permission_sequence_view.stored_permission
        )
        response = self.post(
            'document_renaming:sequence_edit', args=(sequence.pk,),
            data={
                'label': TEST_SEQUENCE_LABEL_EDITED,
                'slug': TEST_SEQUENCE_SLUG,
                'increment': TEST_SEQUENCE_INCREMENT,
                'value': TEST_SEQUENCE_INITIAL_VALUE
            }, follow=True
        )
        self.assertEqual(response.status_code, 200)
        sequence = Sequence.objects.get(pk=sequence.pk)
        self.assertEqual(sequence.label, TEST_SEQUENCE_LABEL_EDITED)


@override_settings(OCR_AUTO_OCR=False)
class RenamingTemplateEditViewsTestCase(GenericViewTestCase):
    def setUp(self):
        super(RenamingTemplateEditViewsTestCase, self).setUp()
        self.document_type = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE
        )

    def test_renaming_template_edit_view_no_permission(self):
        self.login(
            username=TEST_USER_USERNAME, password=TEST_USER_PASSWORD
        )
        self.document_type.renaming_template.template = TEST_TEMPLATE
        self.document_type.renaming_template.save()

        self.role.permissions.add(
            permission_document_type_view.stored_permission
        )
        response = self.post(
            'document_renaming:renaming_template_edit',
            args=(self.document_type.pk,), data={
                'template': TEST_TEMPLATE_EDITED,
            }, follow=True
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            self.document_type.renaming_template.template, TEST_TEMPLATE
        )

    def test_renaming_template_edit_view_with_permission(self):
        self.login(
            username=TEST_USER_USERNAME, password=TEST_USER_PASSWORD
        )
        self.document_type.renaming_template.template = TEST_TEMPLATE
        self.document_type.renaming_template.save()

        self.role.permissions.add(
            permission_renaming_template_edit.stored_permission
        )
        self.role.permissions.add(
            permission_document_type_view.stored_permission
        )
        response = self.post(
            'document_renaming:renaming_template_edit',
            args=(self.document_type.pk,), data={
                'template': TEST_TEMPLATE_EDITED,
            }, follow=True
        )

        # Refresh the model
        self.document_type = DocumentType.objects.get(pk=self.document_type.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self.document_type.renaming_template.template, TEST_TEMPLATE_EDITED
        )
