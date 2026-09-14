# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011-2026 OmniaSolutions and the OdooQtUi contributors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of OdooQtUi, released under the Apache License 2.0.
# Redistributions must keep the attribution in the NOTICE file.
# See the LICENSE and NOTICE files at the root of the project.

'''
Created on 7 Feb 2017

@author: dsmerghetto
'''
import ast
from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

from OdooQtUi.utils_odoo_conn import utils, utilsUi
from OdooQtUi.utils_odoo_conn import constants
from OdooQtUi.objects.fieldTemplate import OdooFieldTemplate

#: What the web client proposes while the user types.
SEARCH_LIMIT = 8

#: How long the user may pause between two keys before the server is asked.
SEARCH_DELAY_MS = 300

CREATE_LABEL = 'Create and Edit...'

#: The item data of the combo entries that are not a record.
CREATE_ITEM = '__create__'


class Many2one(OdooFieldTemplate):
    """A many2one, searched on the server as the user types.

    It used to read every record of the related model -- no domain, no limit --
    for every many2one of a form, each time a form was opened, and to tell the
    records apart by their name. Now the combo holds the current value only,
    the proposals come from `name_search` with the field's domain and context,
    and every entry carries its id.
    """

    def __init__(self,
                 qtParent,
                 xmlField,
                 fieldsDefinition,
                 odooConnector=None,
                 isChatterWidget=False):
        super(Many2one, self).__init__(qtParent,
                                       xmlField,
                                       fieldsDefinition,
                                       odooConnector)
        self.isChatterWidget = isChatterWidget
        self.labelQtObj = False
        self.widgetQtObj = False
        self.editButton = False
        self.odooConnector = odooConnector
        # The form the field is in: what the domain and the context read.
        self.formView = qtParent
        self.currentValue = False
        self.relation = self.fieldPyDefinition.get('relation', '')
        options = self._options()
        self.canCreate = _attributeBoolean(self.fieldXmlAttributes.get('can_create', True)) \
            and not options.get('no_create')
        self.canWrite = _attributeBoolean(self.fieldXmlAttributes.get('can_write', True)) \
            and not options.get('no_open')
        self._updating = False
        self._searchTimer = QtCore.QTimer(self)
        self._searchTimer.setSingleShot(True)
        self._searchTimer.setInterval(SEARCH_DELAY_MS)
        self._searchTimer.timeout.connect(self._search)
        self._completerModel = QtGui.QStandardItemModel(self)
        self.getQtObject()

    def __str__(self)->str:
        return f"<{self.fieldName}> : {self.relation}"

    def _options(self):
        try:
            options = ast.literal_eval(self.fieldXmlAttributes.get('options', '{}') or '{}')
        except Exception:
            return {}
        return options if isinstance(options, dict) else {}

    def getQtObject(self):
        self.labelQtObj = QtWidgets.QLabel(self.fieldStringInterface)
        self.labelQtObj.setStyleSheet(constants.LABEL_STYLE)
        self.qtHorizontalWidget.addWidget(self.labelQtObj)
        self.widgetQtObj = QtWidgets.QWidget(self)
        self.widgetQtObj2 = QtWidgets.QComboBox(self)
        self.widgetQtObj2.setStyleSheet(constants.SELECTION_STYLE)
        self.widgetQtObj2.setToolTip(self.tooltip)
        self.widgetQtObj2.setEditable(True)
        self.widgetQtObj2.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        self.widgetQtObj2.currentIndexChanged.connect(self.indexChanged)
        self._attachCompleter()
        self._fillCombo()
        if self.required:
            utilsUi.setRequiredBackground(self.widgetQtObj2, constants.SELECTION_STYLE)
        self.qtHorizontalWidget.addWidget(self.widgetQtObj2)
        if self.canWrite:
            self.editButton = QtWidgets.QPushButton('E')
            self.editButton.clicked.connect(self.editItem)
            self.editButton.setStyleSheet(constants.BUTTON_STYLE_MANY_2_ONE)
            self.qtHorizontalWidget.addWidget(self.editButton)
            if not self.currentValue:
                self.editButton.setHidden(True)
        self.qtHorizontalWidget.addWidget(self.widgetQtObj)
        self.qtHorizontalWidget.insertSpacerItem(3, QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        if self.translatable:
            self.connectTranslationButton()
            self.addWidget(self.translateButton)

    # -- the combo: blank, the current value, create -------------------------

    def _fillCombo(self):
        """The combo holds what can be picked without a search."""
        self._updating = True
        try:
            combo = self.widgetQtObj2
            combo.clear()
            combo.addItem('', False)
            if self.currentValue:
                combo.addItem(self.currentValue[1], self.currentValue[0])
                combo.setCurrentIndex(1)
            else:
                combo.setCurrentIndex(0)
            if self.canCreate:
                combo.addItem(CREATE_LABEL, CREATE_ITEM)
            self._restoreText()
        finally:
            self._updating = False

    def _restoreText(self):
        if self.widgetQtObj2.lineEdit():
            self.widgetQtObj2.lineEdit().setText(self.valueInterface)

    # -- the search while the user types -------------------------------------

    def _attachCompleter(self):
        """The popup of proposals, on the line edit of the combo.

        Attached again whenever the combo becomes editable: setEditable(False)
        destroys the line edit, and the completer with it.
        """
        lineEdit = self.widgetQtObj2.lineEdit()
        if lineEdit is None or lineEdit is getattr(self, '_attachedLineEdit', None):
            # None, or the one already served: the modifier pass calls
            # setReadonly(False) on every change, and each call would add a
            # completer and one more connection to the same signals.
            return
        self._attachedLineEdit = lineEdit
        completer = QtWidgets.QCompleter(self._completerModel, self)
        # The server has filtered already: show what it answered, all of it.
        completer.setCompletionMode(QtWidgets.QCompleter.UnfilteredPopupCompletion)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        completer.activated[QtCore.QModelIndex].connect(self._proposalChosen)
        lineEdit.setCompleter(completer)
        lineEdit.textEdited.connect(self._textEdited)
        lineEdit.editingFinished.connect(self._editingFinished)
        self._completer = completer

    def _textEdited(self, text):
        if self._updating:
            return
        if not text:
            self._searchTimer.stop()
            if self.currentValue:
                self._setCurrent(False)
            return
        self._searchTimer.start()

    def _search(self):
        lineEdit = self.widgetQtObj2.lineEdit()
        if lineEdit is None or not self.relation:
            return
        text = lineEdit.text()
        results = self.nameSearch(text)
        self._completerModel.clear()
        for recordId, name in results:
            item = QtGui.QStandardItem(name)
            item.setData(recordId, QtCore.Qt.UserRole)
            self._completerModel.appendRow(item)
        if results:
            self._completer.setCompletionPrefix('')
            self._completer.complete()

    def nameSearch(self, text, limit=SEARCH_LIMIT):
        """[(id, name)] of the related records matching `text`, as Odoo finds them."""
        kwargs = {'name': text or '', 'domain': self.evaluatedDomain(), 'limit': limit}
        results = self.odooConnector.rpc_connector.callCustomMethod(
            self.relation, 'name_search', [], kwargs, context=self.evaluatedContext())
        return [(pair[0], pair[1]) for pair in (results or [])
                if isinstance(pair, (list, tuple)) and len(pair) == 2]

    def _recordValues(self):
        form = self.formView
        if form is None or not hasattr(form, 'interfaceFieldsDict'):
            return {}
        return utils.recordValues(form.interfaceFieldsDict, getattr(form, 'formVals', {}))

    def evaluatedDomain(self):
        """The field's domain, over the record in the form. [] if it cannot be read."""
        domain = self.fieldXmlAttributes.get('domain') or self.fieldPyDefinition.get('domain') or []
        if isinstance(domain, (list, tuple)):
            return list(domain)
        namespace = dict(self._recordValues())
        namespace.setdefault('context', dict(self.odooConnector.rpc_connector.contextUser))
        namespace.setdefault('uid', self.odooConnector.rpc_connector.contextUser.get('uid'))
        try:
            result = eval(str(domain), {'__builtins__': {'True': True, 'False': False, 'None': None}}, namespace)
        except Exception as ex:
            utils.logMessage('debug', 'Unable to evaluate the domain %r of %r: %s'
                             % (domain, self.fieldName, ex), 'evaluatedDomain')
            return []
        return list(result) if isinstance(result, (list, tuple)) else []

    def evaluatedContext(self):
        form = self.formView
        fields = getattr(form, 'interfaceFieldsDict', {}) if form is not None else {}
        return utils.evaluateContext(self.context, fields)

    def _proposalChosen(self, index):
        recordId = index.data(QtCore.Qt.UserRole)
        name = index.data(QtCore.Qt.DisplayRole)
        if recordId:
            self._setCurrent([recordId, name])

    def _editingFinished(self):
        # A text typed and not chosen is not a value: back to the one there is.
        if not self._updating and self.widgetQtObj2.lineEdit() \
                and self.widgetQtObj2.lineEdit().text() != self.valueInterface:
            self._searchTimer.stop()
            self._restoreText()

    def _setCurrent(self, value):
        """The user picked a value: show it, and tell the form."""
        changed = self.value != (value[0] if value else False)
        self.currentValue = value
        self._fillCombo()
        self._showEditButton()
        if changed:
            self.valueTemplateChanged()

    def _showEditButton(self):
        if self.editButton:
            self.editButton.setHidden(not self.currentValue or not self.widgetQtObj2.isEnabled())

    # -- the public interface ------------------------------------------------

    def comboActivated(self, val=False):
        """Kept for the callers of old: a search of the text in the combo."""
        self._search()

    def setValue(self, val=False, viewType='form'):
        """[id, name] as a read answers, an id, or False. Asks the server only for an id."""
        if isinstance(val, (list, tuple)) and len(val) == 2:
            value = [val[0], val[1]]
        elif isinstance(val, int) and not isinstance(val, bool) and val:
            res = self.odooConnector.rpc_connector.read(self.relation, ['display_name'], [val])
            value = [val, res[0].get('display_name', '')] if res else False
        else:
            value = False
        self.currentValue = value
        self._fillCombo()
        self._showEditButton()

    def setReadonly(self, val=False):
        super(Many2one, self).setReadonly(val)
        self.widgetQtObj2.setEnabled(not val)
        self.widgetQtObj2.setEditable(not val)
        self.widgetQtObj2.setDisabled(val)
        if not val:
            self._attachCompleter()
            self._restoreText()
        if val:
            if self.editButton:
                self.editButton.setHidden(True)
            self.widgetQtObj2.setStyleSheet(constants.SELECTION_STYLE + constants.READONLY_STYLE)
        else:
            self._showEditButton()
            if self.required:
                utilsUi.setRequiredBackground(self.widgetQtObj2, constants.SELECTION_STYLE)
            else:
                self.widgetQtObj2.setStyleSheet(constants.SELECTION_STYLE)

    def setInvisible(self, val=False):
        if self.isChatterWidget:
            return
        super(Many2one, self).setInvisible(val)
        self.labelQtObj.setHidden(val)
        if self.widgetQtObj2:
            self.widgetQtObj2.setHidden(val)
        if self.currentValue and not val:
            if self.editButton:
                self.editButton.show()
        else:
            if self.editButton:
                self.editButton.hide()

    def editItem(self, res=False):
        if not self.currentValue:
            return
        dialog = QtWidgets.QDialog()

        def accept():
            dialog.accept()

        def reject():
            dialog.reject()

        self.setViewObject()
        self.viewObj.loadIds([self.currentValue[0]])
        mainLay = QtWidgets.QVBoxLayout()
        utilsUi.setLayoutMarginAndSpacing(mainLay)
        mainLay.addWidget(self.viewObj)
        lay, okButt, cancelButt = utilsUi.getButtonBox()
        okButt.clicked.connect(accept)
        cancelButt.clicked.connect(reject)
        okButt.setStyleSheet(constants.BUTTON_STYLE_OK)
        cancelButt.setStyleSheet(constants.BUTTON_STYLE_CANCEL)
        lay.setParent(None)
        mainLay.addLayout(lay)
        dialog.setLayout(mainLay)
        dialog.setStyleSheet(constants.BACKGROUND_WHITE)
        dialog.adjustSize()
        dialog.resize(1000, 750)
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            valuesToUpdate = {}
            for fieldName, fieldObj in list(self.viewObj.fieldsChanged.items()):
                valuesToUpdate[fieldName] = fieldObj.value
            if valuesToUpdate:
                self.odooConnector.rpc_connector.write(self.relation, valuesToUpdate, self.currentValue[0])
                # The name shown is the server's display_name, whatever changed.
                self.setValue(self.currentValue[0])
                self.valueTemplateChanged()

    def setViewObject(self):
        self.viewObj = self.odooConnector.initFormViewObj(self.relation)

    def indexChanged(self, res=False):
        if self._updating:
            return
        data = self.widgetQtObj2.currentData()
        if data == CREATE_ITEM:
            self._createAndEdit()
        elif not data:
            if self.currentValue:
                self._setCurrent(False)
        elif not self.currentValue or data != self.currentValue[0]:
            self._setCurrent([data, self.widgetQtObj2.currentText()])

    def _createAndEdit(self):
        dialog = QtWidgets.QDialog()

        def accept():
            dialog.accept()

        def reject():
            dialog.reject()

        self.setViewObject()
        self.viewObj.loadIds([])
        mainLay = self.viewObj.layout()
        lay, okButt, cancelButt = utilsUi.getButtonBox()
        okButt.clicked.connect(accept)
        cancelButt.clicked.connect(reject)
        okButt.setStyleSheet(constants.BUTTON_STYLE_OK)
        cancelButt.setStyleSheet(constants.BUTTON_STYLE_CANCEL)
        lay.setParent(None)
        mainLay.addLayout(lay)
        dialog.setLayout(mainLay)
        dialog.setStyleSheet(constants.VIOLET_BACKGROUND)
        dialog.adjustSize()
        dialog.resize(800, dialog.height())
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            valuesToCreate = {}
            for fieldName, fieldObj in list(self.viewObj.interfaceFieldsDict.items()):
                valuesToCreate[fieldName] = fieldObj.value
            newId = self.odooConnector.rpc_connector.create(self.relation, valuesToCreate)
            if newId:
                self.setValue(newId)
                self.valueTemplateChanged()
                return
        self._fillCombo()

    @property
    def value(self):
        try:
            if isinstance(self.currentValue, int):
                return self.currentValue
            if self.currentValue:
                return self.currentValue[0]
            return self.currentValue
        except Exception as ex:
            utils.logMessage('error', 'Error during getting value from many2one field %r: %r' % (self.fieldName, ex), 'value')

    @property
    def valueInterface(self):
        if self.currentValue:
            return self.currentValue[1]
        return ''

    def eraseValue(self):
        self.setValue(False)


def _attributeBoolean(value):
    """can_create and can_write: JSON up to 16 ("true"), Python from 17 ("True")."""
    if isinstance(value, str):
        return value.strip().lower() in ('true', '1')
    return bool(value)
