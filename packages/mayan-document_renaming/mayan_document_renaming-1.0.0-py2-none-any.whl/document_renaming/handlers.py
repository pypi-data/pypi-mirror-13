from __future__ import unicode_literals

import logging

from .models import RenamingTemplate
from .tasks import task_rename_document

logger = logging.getLogger(__name__)


def initialize_new_document_types(sender, instance, **kwargs):
    """
    Create a blank renaming template when a new document type is created
    """

    if kwargs['created']:
        RenamingTemplate.objects.create(document_type=instance)


def rename_document(sender, instance, **kwargs):
    """
    Call the background task to rename a document
    """

    logger.debug('instance: %s', instance)

    task_rename_document.apply_async(kwargs={'document_pk': instance.pk})
