'''
Created on 02 feb 2017

@author: Daniel
'''
import json

from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets
from OdooQtUi.utils_odoo_conn import utils
from OdooQtUi.utils_odoo_conn import constants


class OdooFieldTemplate(QtWidgets.QWidget):
    value_changed_signal = QtCore.Signal((str,))
    translation_clicked = QtCore.Signal((str,))

    def __init__(self, qtParent, xmlField, fieldsDefinition, rpc):
        super(OdooFieldTemplate, self).__init__(qtParent)
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.setMinimumSize(40, 40)
        self.rpc = rpc
        self.fieldXmlAttributes = xmlField.attrib
        self.parentId = False
        self.parentModel = ''
        self.fieldName = self.fieldXmlAttributes.get('name', '')
        self.modifiers = json.loads(self.fieldXmlAttributes.get('modifiers', '{}'))
        self.on_change = self.fieldXmlAttributes.get('on_change', '')
        self.fieldPyDefinition = fieldsDefinition.get(self.fieldName, {})
        self.readonly = utils.evaluateBoolean(self.fieldPyDefinition.get('readonly', False))
        self.required = utils.evaluateBoolean(self.fieldPyDefinition.get('required', False))
        self.invisible = utils.evaluateBoolean(self.fieldPyDefinition.get('invisible', False))
        self.tooltip = self.fieldPyDefinition.get('help', '')
        self.fieldType = self.fieldPyDefinition.get('type', '')
        self.labelString = self.fieldPyDefinition.get('string', '')
        self.fieldStringInterface = self.fieldXmlAttributes.get('string', self.labelString)
        self.change_default = utils.evaluateBoolean(self.fieldPyDefinition.get('change_default', False))
        self.searchable = utils.evaluateBoolean(self.fieldPyDefinition.get('searchable', True))
        self.manual = utils.evaluateBoolean(self.fieldPyDefinition.get('manual', False))
        self.depends = self.fieldPyDefinition.get('depends', [])
        self.related = self.fieldPyDefinition.get('related', [])
        self.company_dependent = utils.evaluateBoolean(self.fieldPyDefinition.get('company_dependent', False))
        self.sortable = utils.evaluateBoolean(self.fieldPyDefinition.get('sortable', True))
        self.store = utils.evaluateBoolean(self.fieldPyDefinition.get('store', True))
        self.translatable = self.fieldXmlAttributes.get('translate', self.fieldPyDefinition.get('translate', False))
        self.labelQtObj = None
        self.qDoubleSpinBoxValue = None
        self.initVal = ''
        self.changed = False
        self.translateButton = False
        self.invisibleConditions, self.readonlyConditions = utils.evaluateModifiers(self.modifiers)
        self.qtHorizontalWidget = QtWidgets.QHBoxLayout(self)
        self.hide()
        if constants.DEBUG:
            self.setStyleSheet("border: 2px solid black;")
            self.show()
        return self

    def setParentAttrs(self, parentId, parentModel):
        self.parentId = parentId
        self.parentModel = parentModel

    def connectTranslationButton(self):
        self.translateButton = QtWidgets.QPushButton('Translate')
        self.translateButton.setStyleSheet(constants.BUTTON_STYLE)
        self.translateButton.clicked.connect(self.translateDialog)

    def valueTemplateChanged(self):
        self.value_changed_signal.emit(self.fieldName)

    def setValue(self, newVal):
        utils.logMessage('warning', 'setValue not implemented for field: %r' % (self.fieldName), 'setValue')

    def hideTranslateButton(self, val):
        if self.translateButton:
            self.translateButton.setHidden(val)

    def valueChanged(self):
        utils.logMessage('warning', 'valueChanged not implemented for field: %r' % (self.fieldName), 'valueChanged')

    def translateDialog(self):
        self.translation_clicked.emit(self.fieldName)

    def setReadonly(self, val):
        self.setEnabled(not val)

    def setInvisible(self, val):
        if val:
            self.hide()
        else:
            self.show()
