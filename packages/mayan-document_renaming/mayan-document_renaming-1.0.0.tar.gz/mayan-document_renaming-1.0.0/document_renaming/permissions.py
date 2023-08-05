from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from permissions import PermissionNamespace

namespace = PermissionNamespace('document_renaming', _('Document renaming'))

permission_sequence_create = namespace.add_permission(
    name='sequence_create', label=_('Create sequences')
)
permission_sequence_delete = namespace.add_permission(
    name='sequence_delete', label=_('Delete sequences')
)
permission_sequence_edit = namespace.add_permission(
    name='sequence_edit', label=_('Edit sequences')
)
permission_sequence_view = namespace.add_permission(
    name='sequence_view', label=_('View sequences')
)

permission_renaming_template_edit = namespace.add_permission(
    name='renaming_template_edit', label=_('Edit renaming templates')
)
