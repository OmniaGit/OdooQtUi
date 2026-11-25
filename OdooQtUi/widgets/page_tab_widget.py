# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011-2026 OmniaSolutions and the OdooQtUi contributors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of OdooQtUi, released under the Apache License 2.0.
# Redistributions must keep the attribution in the NOTICE file.
# See the LICENSE and NOTICE files at the root of the project.

"""A notebook as high as the page it shows, as Odoo draws one.

QTabWidget.sizeHint is the tallest of its pages, whatever their size policy
(measured 2026-11-25): a short page left an empty band under it, and the form
grew by it. Here the hint is the page shown, and it changes with the page.
"""

from PySide6 import QtCore
from PySide6 import QtWidgets


class PageTabWidget(QtWidgets.QTabWidget):

    def __init__(self, parent=None):
        super(PageTabWidget, self).__init__(parent)
        # Room the layout has to spare goes elsewhere, not under the page.
        self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        self.currentChanged.connect(self._pageChanged)

    def _pageChanged(self, _index):
        self.updateGeometry()

    def _onePage(self, hint, pageHint):
        """hint, the tallest page's height in it replaced by the page shown's."""
        page = self.currentWidget()
        if page is None:
            return hint
        tallest = 0
        for index in range(self.count()):
            other = self.widget(index)
            if other is not None and self.isTabVisible(index):
                tallest = max(tallest, pageHint(other).height())
        return QtCore.QSize(hint.width(), hint.height() - tallest + pageHint(page).height())

    def sizeHint(self):
        return self._onePage(super(PageTabWidget, self).sizeHint(), lambda page: page.sizeHint())

    def minimumSizeHint(self):
        return self._onePage(super(PageTabWidget, self).minimumSizeHint(),
                             lambda page: page.minimumSizeHint())
