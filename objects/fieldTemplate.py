'''
Created on 02 feb 2017

@author: Daniel
'''
from PyQt4 import QtGui, QtCore
from utils_odoo_conn import utils
from utils_odoo_conn import constants
import json


class OdooFieldTemplate(QtCore.QObject, object):

    value_changed_signal = QtCore.pyqtSignal(QtCore.QString)
    translation_clicked = QtCore.pyqtSignal(QtCore.QString)

    def __init__(self, xmlField, fieldsDefinition, rpc):
        self.rpc = rpc
        self.fieldXmlAttributes = xmlField.attrib
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
        self.widgetQtObj = None
        self.initVal = ''
        self.changed = False
        self.widgetLyQtObject = QtGui.QHBoxLayout()
        self.translateButton = False
        self.invisibleConditions, self.readonlyConditions = utils.evaluateModifiers(self.modifiers)
        return super(OdooFieldTemplate, self).__init__()

    @property
    def qtObject(self):
        return self.widgetLyQtObject

    def connectTranslationButton(self):
        self.translateButton = QtGui.QPushButton('Translate')
        self.translateButton.setStyleSheet(constants.BUTTON_STYLE)
        self.translateButton.clicked.connect(self.translateDialog)

    def valueTemplateChanged(self):
        self.value_changed_signal.emit(self.fieldName)

    def setValue(self, newVal):
        utils.logMessage('warning', 'setValue not implemented for field: %r' % (self.fieldName), 'setValue')

    def setReadonly(self, val=False):
        self.hideTranslateButton(val)

    def setInvisible(self, val=False):
        self.hideTranslateButton(val)

    def hideTranslateButton(self, val):
        if self.translateButton:
            self.translateButton.setHidden(val)

    def valueChanged(self):
        utils.logMessage('warning', 'valueChanged not implemented for field: %r' % (self.fieldName), 'valueChanged')

    def translateDialog(self):
        self.translation_clicked.emit(self.fieldName)
