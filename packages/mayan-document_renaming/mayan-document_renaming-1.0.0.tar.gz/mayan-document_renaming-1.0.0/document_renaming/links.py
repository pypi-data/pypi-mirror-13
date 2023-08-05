from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from navigation import Link

from .permissions import (
    permission_sequence_create, permission_sequence_delete,
    permission_sequence_edit, permission_sequence_view,
    permission_renaming_template_edit
)

link_sequence_create = Link(
    permissions=(permission_sequence_create,),
    text=_('Create sequence'), view='document_renaming:sequence_create'
)
link_sequence_delete = Link(
    permissions=(permission_sequence_delete,), tags='dangerous',
    text=_('Delete'), view='document_renaming:sequence_delete',
    args='resolved_object.id'
)
link_sequence_edit = Link(
    permissions=(permission_sequence_edit,), text=_('Edit'),
    view='document_renaming:sequence_edit', args='resolved_object.id'
)
link_sequence_list = Link(
    icon='fa fa-sort-amount-asc', permissions=(permission_sequence_view,),
    text=_('Sequences'), view='document_renaming:sequence_list',
)

link_document_type_renaming_template_edit = Link(
    permissions=(permission_renaming_template_edit,),
    text=_('Renaming template'),
    view='document_renaming:renaming_template_edit', args='resolved_object.id'
)
