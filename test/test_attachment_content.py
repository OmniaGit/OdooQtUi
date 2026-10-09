# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011-2026 OmniaSolutions and the OdooQtUi contributors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of OdooQtUi, released under the Apache License 2.0.
# Redistributions must keep the attribution in the NOTICE file.
# See the LICENSE and NOTICE files at the root of the project.

"""ir.attachment content across Odoo versions: datas up to 19, raw from 20,
and a binary field read as a string up to 19, as {content, size} from 20."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from OdooQtUi.utils_odoo_conn import utils


class TestAttachmentContent(unittest.TestCase):

    def test_the_field_follows_the_server(self):
        self.assertEqual('datas', utils.attachmentContentField(18))
        self.assertEqual('datas', utils.attachmentContentField(19))
        self.assertEqual('raw', utils.attachmentContentField(20))
        self.assertEqual('raw', utils.attachmentContentField(21))
        self.assertEqual('raw', utils.attachmentContentField(None))

    def test_the_content_of_every_shape(self):
        self.assertEqual('QUJD', utils.binaryContent('QUJD'))
        self.assertEqual('QUJD', utils.binaryContent({'content': 'QUJD', 'size': 3, 'filename': 'a'}))
        self.assertEqual('', utils.binaryContent(False))
        self.assertEqual('', utils.binaryContent({'content': False, 'size': 0}))


if __name__ == '__main__':
    unittest.main()
