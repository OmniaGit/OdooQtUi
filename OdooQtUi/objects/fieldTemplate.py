'''
Created on 02 feb 2017

@author: Daniel
'''
import json

from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets
from OdooQtUi.utils_odoo_conn import utils
from OdooQtUi.utils_odoo_conn import utilsUi
from OdooQtUi.utils_odoo_conn import constants


class OdooFieldTemplate(QtWidgets.QWidget):
    value_changed_signal = QtCore.Signal((str,))
    translation_clicked = QtCore.Signal((str,))

    def __init__(self, qtParent, xmlField, fieldsDefinition, odooConnector):
        super(OdooFieldTemplate, self).__init__(qtParent)
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.odooConnector=odooConnector
        self.fieldXmlAttributes = xmlField.attrib
        self.parentId = False
        self.odooId=False
        self.parentModel = ''
        self.fieldName = self.fieldXmlAttributes.get('name', '')
        self.modifiers = json.loads(self.fieldXmlAttributes.get('modifiers', '{}'))
        self.on_change = self.fieldXmlAttributes.get('on_change', '')
        self.fieldPyDefinition = fieldsDefinition.get(self.fieldName, {})
        readonly = self.fieldPyDefinition.get('readonly', self.fieldXmlAttributes.get('readonly', False))
        self.readonly = utils.evaluateBoolean(readonly)
        required = self.fieldPyDefinition.get('required', self.fieldXmlAttributes.get('required', False))
        self.required = utils.evaluateBoolean(required)
        invisible = self.fieldPyDefinition.get('invisible', self.fieldXmlAttributes.get('invisible', False))
        self.invisible = utils.evaluateBoolean(invisible)
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
        self.widgetQtObj = None
        self.initVal = ''
        self.changed = False
        self.translateButton = False
        self.invisibleConditions, self.readonlyConditions = utils.evaluateModifiers(self.modifiers)
        self.qtHorizontalWidget = QtWidgets.QHBoxLayout(self)
        utilsUi.setLayoutMarginAndSpacing(self.qtHorizontalWidget)
        self.hide()
        if constants.DEBUG:
            self.setStyleSheet("border: 2px solid black;")
        return self

    @property
    def qtObject(self):
        return self.qtHorizontalWidget

    def setParentAttrs(self, parentId, parentModel):
        self.parentId = parentId
        self.parentModel = parentModel

    def connectTranslationButton(self):
        self.translateButton = QtWidgets.QPushButton('T')
        self.translateButton.setStyleSheet(constants.BUTTON_STYLE)
        self.translateButton.clicked.connect(self.translateDialog)
        # self.qtHorizontalWidget.setSpacing(10)

    def valueTemplateChanged(self):
        self.value_changed_signal.emit(self.fieldName)

    def setValue(self, newVal, viewType='form'):
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
        self.hideTranslateButton(val)

    def setInvisible(self, val):
        utilsUi.setLayoutMarginAndSpacing(self.qtHorizontalWidget, 0)
        self.hideTranslateButton(val)
        if val:
            self.hide()
        else:
            self.show()

    def showChatterWidget(self):
        pass