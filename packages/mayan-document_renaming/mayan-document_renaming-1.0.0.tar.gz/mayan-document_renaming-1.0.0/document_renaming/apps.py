from __future__ import unicode_literals

from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

from common import menu_object, menu_secondary, menu_setup
from common.apps import MayanAppConfig
from documents.models import Document, DocumentType
from documents.signals import post_document_created
from mayan.celery import app
from navigation import SourceColumn

from .handlers import initialize_new_document_types, rename_document
from .links import (
    link_sequence_create, link_sequence_delete, link_sequence_edit,
    link_sequence_list, link_document_type_renaming_template_edit
)
from .models import Sequence


class DocumentRenamingApp(MayanAppConfig):
    name = 'document_renaming'
    test = True
    verbose_name = _('Document renaming')

    def ready(self):
        super(DocumentRenamingApp, self).ready()

        SourceColumn(
            source=Sequence, label=_('Label'),
            attribute='label'
        )

        SourceColumn(
            source=Sequence, label=_('Slug'),
            attribute='slug'
        )

        SourceColumn(
            source=Sequence, label=_('Increment'),
            attribute='increment'
        )

        SourceColumn(
            source=Sequence, label=_('Value'),
            attribute='value'
        )

        # Since we work on uploaded documents, we reuse the 'uploads' queue
        # defined by the 'documents' app.
        app.conf.CELERY_ROUTES.update(
            {
                'document_renaming.tasks.task_rename_document': {
                    'queue': 'uploads'
                },
            }
        )

        menu_object.bind_links(
            links=(link_sequence_delete, link_sequence_edit,),
            sources=(Sequence,)
        )

        menu_object.bind_links(
            links=(link_document_type_renaming_template_edit,),
            sources=(DocumentType,)
        )

        menu_secondary.bind_links(
            links=(link_sequence_list, link_sequence_create),
            sources=(
                Sequence, 'document_renaming:sequence_create',
                'document_renaming:sequence_list'
            )
        )

        menu_setup.bind_links(links=(link_sequence_list,))

        post_document_created.connect(
            rename_document, dispatch_uid='rename_document',
            sender=Document
        )

        post_save.connect(
            initialize_new_document_types,
            dispatch_uid='initialize_new_document_types', sender=DocumentType
        )
