from __future__ import unicode_literals

import logging

from django.db import models
from django.template import Context, Template
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from documents.models import DocumentType

from .literals import (
    DEFAULT_SEQUENCE_INCREMENT, DEFAULT_SEQUENCE_INITIAL_VALUE
)
from .managers import RenamingTemplateManager

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class Sequence(models.Model):
    """
    Model to store the persistent state of a renaming sequence.
    """
    label = models.CharField(
        max_length=32, unique=True, verbose_name=_('Label')
    )
    slug = models.SlugField(
        help_text=_('Do not use hypens, if you need spacing use underscores.'),
        verbose_name=_('Slug')
    )
    increment = models.IntegerField(
        default=DEFAULT_SEQUENCE_INCREMENT, verbose_name=_('Increment')
    )
    value = models.IntegerField(
        default=DEFAULT_SEQUENCE_INITIAL_VALUE, verbose_name=_('Value')
    )

    def next_value(self):
        result = self.value
        self.value += self.increment
        self.save()
        return result

    class Meta:
        verbose_name = _('Sequence')
        verbose_name_plural = _('Sequences')

    def __str__(self):
        return self.label


class RenamingTemplate(models.Model):
    """
    Model to store the renaming template for a document type.
    """

    document_type = models.OneToOneField(
        DocumentType, related_name='renaming_template',
        verbose_name=_('Document type')
    )

    template = models.TextField(
        blank=True,
        help_text=_(
            'Sequences are available as "sequence_[sequence slug]". To obtain '
            'the next value for a sequence, call it\'s next_value method, ie: '
            '"invoice-{{ sequence_invoices.next_value }}.'
        ), verbose_name=_('Template')
    )

    objects = RenamingTemplateManager()

    def render_for(self, document):
        context_dictionary = {}
        for sequence in Sequence.objects.all():
            context_dictionary[
                'sequence_{}'.format(sequence.slug)
            ] = sequence
        context_dictionary['document'] = document

        try:
            template = Template(self.template)
            context = Context(context_dictionary)
            result = template.render(context=context)
        except Exception as exception:
            error_message = _(
                'Error rendering rename template for document: %(document)s; '
                'template: %(template)s; %(exception)s'
            ) % {
                'document': document,
                'template': self.template,
                'exception': exception
            }
            logger.debug(error_message)
        else:
            return result

    class Meta:
        verbose_name = _('Renaming template')
        verbose_name_plural = _('Renaming templates')
