from __future__ import unicode_literals

import os

from documents.tests import TEST_SMALL_DOCUMENT_FILENAME

TEST_SMALL_DOCUMENT_PATH = os.path.join(
    'contrib', 'sample_documents',
    TEST_SMALL_DOCUMENT_FILENAME
)

TEST_SEQUENCE_LABEL = 'test sequence label'
TEST_SEQUENCE_LABEL_EDITED = 'test sequence label edited'
TEST_SEQUENCE_SLUG = 'test_sequence_slug'
TEST_SEQUENCE_INCREMENT = 1
TEST_SEQUENCE_INITIAL_VALUE = 0
TEST_TEMPLATE = 'invoice-{{{{ sequence_{}.next_value }}}}'.format(
    TEST_SEQUENCE_SLUG
)
TEST_TEMPLATE_EDITED = 'edited'
