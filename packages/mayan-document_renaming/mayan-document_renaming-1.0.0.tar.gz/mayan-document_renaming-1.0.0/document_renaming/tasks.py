from __future__ import unicode_literals

import logging

from django.db import OperationalError

from mayan.celery import app

from documents.models import Document
from lock_manager import Lock, LockError

from .literals import DOCUMENT_RENAME_RETRY_DELAY, LOCK_EXPIRE
from .models import RenamingTemplate

logger = logging.getLogger(__name__)


@app.task(bind=True, default_retry_delay=DOCUMENT_RENAME_RETRY_DELAY, ignore_result=True)
def task_rename_document(self, document_pk):
    lock_id = 'task_rename_document-%d' % document_pk

    try:
        logger.debug('trying to acquire lock: %s', lock_id)
        # Acquire a lock to avoid a race condition when incrementing the
        # sequence
        lock = Lock.acquire_lock(name=lock_id, timeout=LOCK_EXPIRE)
        logger.debug('acquired lock: %s', lock_id)
        try:
            logger.info(
                'Starting document rename for document: %s', document_pk
            )
            document = Document.objects.get(pk=document_pk)
            RenamingTemplate.objects.rename_document(document=document)
        except OperationalError as exception:
            logger.warning(
                'Operational error during document rename for document: %d; '
                '%s. Retrying.', document_pk, exception
            )
            raise self.retry(exc=exception)
        finally:
            lock.release()
    except LockError:
        logger.debug('unable to obtain lock: %s' % lock_id)
