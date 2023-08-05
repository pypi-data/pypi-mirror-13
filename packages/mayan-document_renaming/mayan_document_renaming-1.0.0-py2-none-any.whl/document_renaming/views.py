from __future__ import absolute_import, unicode_literals

from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _

from common.generics import (
    SingleObjectCreateView, SingleObjectDeleteView, SingleObjectEditView,
    SingleObjectListView
)
from documents.models import DocumentType

from .models import Sequence
from .permissions import (
    permission_sequence_create, permission_sequence_delete,
    permission_sequence_edit, permission_sequence_view,
    permission_renaming_template_edit
)


class SequenceListView(SingleObjectListView):
    model = Sequence
    view_permission = permission_sequence_view

    def get_extra_context(self):
        return {
            'hide_object': True,
            'title': _('Sequences'),
        }


class SequenceCreateView(SingleObjectCreateView):
    model = Sequence
    post_action_redirect = reverse_lazy('document_renaming:sequence_list')
    view_permission = permission_sequence_create

    def get_extra_context(self):
        return {
            'title': _('Create sequence'),
        }


class SequenceDeleteView(SingleObjectDeleteView):
    model = Sequence
    post_action_redirect = reverse_lazy('document_renaming:sequence_list')
    view_permission = permission_sequence_delete

    def get_extra_context(self):
        return {
            'object': self.get_object(),
            'title': _('Delete the sequence: %s?') % self.get_object(),
        }


class SequenceEditView(SingleObjectEditView):
    model = Sequence
    post_action_redirect = reverse_lazy('document_renaming:sequence_list')
    view_permission = permission_sequence_edit

    def get_extra_context(self):
        return {
            'object': self.get_object(),
            'title': _('Edit sequence: %s') % self.get_object(),
        }


class DocumentTypeRenamingTemplateEditView(SingleObjectEditView):
    fields = ('template',)
    view_permission = permission_renaming_template_edit

    def get_object(self, queryset=None):
        return get_object_or_404(
            DocumentType, pk=self.kwargs['pk']
        ).renaming_template

    def get_extra_context(self):
        return {
            'title': _(
                'Edit renaming template for document type: %s'
            ) % self.get_object().document_type
        }
