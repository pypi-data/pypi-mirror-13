from __future__ import unicode_literals

import logging

from django.db import models

logger = logging.getLogger(__name__)


class RenamingTemplateManager(models.Manager):
    def rename_document(self, document):
        result = document.document_type.renaming_template.render_for(
            document=document
        )
        document.label = result
        document.save()
