# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011-2026 OmniaSolutions and the OdooQtUi contributors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of OdooQtUi, released under the Apache License 2.0.
# Redistributions must keep the attribution in the NOTICE file.
# See the LICENSE and NOTICE files at the root of the project.

"""Pick records of a model from its list: the one dialog for a many2many's
"Add an item" (several) and a many2one's "Search More..." (one), as Odoo has
one for both (2026-11-25).

The list has the model's search view above it, and pages through the
domain it is given. Records are picked by ticking them, by selecting rows,
or by a double click, which takes its row and closes the dialog.
"""

from PySide6 import QtCore
from PySide6 import QtWidgets

from OdooQtUi.utils_odoo_conn import constants
from OdooQtUi.utils_odoo_conn import utilsUi

CHECK_BOXES = {0: QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled}


def pickedIds(listView, extraIds=()):
    """The ids picked in listView, in the order of its rows: ticked or
    selected, and extraIds (the row double-clicked)."""
    picked = set(listView.getSelectedIds()) | set(extraIds)
    rows = listView.idLineRel
    return [rows[row] for row in sorted(rows) if rows[row] in picked]


def pickRecords(odooConnector, model, domain=None, multi=True, title=''):
    """The ids of the records of model the user picks, [] when cancelled.
    :domain the records that may be picked, [] for all of them
    :multi several records, or one
    """
    domain = list(domain or [])
    listView = odooConnector.initTreeListViewObject(model,
                                                    viewCheckBoxes=CHECK_BOXES if multi else {},
                                                    viewFilter=True,
                                                    deafult_filter=domain)
    resIds = odooConnector.rpc_connector.search(model, domain, limit=listView.currentRange[-1],
                                                offset=listView.currentRange[0])
    listView.loadIds(resIds, {}, {}, {})
    table = listView.treeObj.tableWidget
    table.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection if multi
                           else QtWidgets.QAbstractItemView.SingleSelection)

    dialog = QtWidgets.QDialog()
    dialog.setWindowTitle(title)
    layout = QtWidgets.QVBoxLayout()
    utilsUi.setLayoutMarginAndSpacing(layout)
    buttonsLayout, okButton, cancelButton = utilsUi.getButtonBox('right')
    okButton.setStyleSheet(constants.BUTTON_STYLE_OK)
    cancelButton.setStyleSheet(constants.BUTTON_STYLE_CANCEL)
    okButton.clicked.connect(dialog.accept)
    cancelButton.clicked.connect(dialog.reject)
    layout.addWidget(listView)
    layout.addLayout(buttonsLayout)
    dialog.setLayout(layout)
    dialog.setStyleSheet(constants.VIOLET_BACKGROUND)
    dialog.resize(800, 500)

    doubleClicked = []

    def takeRow(objId):
        doubleClicked.append(objId)
        dialog.accept()
    listView.doubleClickCallback = takeRow

    if dialog.exec() != QtWidgets.QDialog.Accepted:
        return []
    ids = pickedIds(listView, doubleClicked)
    if not multi:
        ids = doubleClicked[:1] or ids[:1]
    return ids
