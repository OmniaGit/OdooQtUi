'''
Created on 06 feb 2017

@author: Daniel
'''
import json
from PySide2 import QtCore
from PySide2 import QtWidgets
from OdooQtUi.utils_odoo_conn import utils, utilsUi
from OdooQtUi.utils_odoo_conn import constants
from OdooQtUi.objects.fieldTemplate import OdooFieldTemplate


class Selection(OdooFieldTemplate):
    def __init__(self, qtParent, xmlField, fieldsDefinition, rpc, isChatterWidget=False):
        super(Selection, self).__init__(qtParent, xmlField, fieldsDefinition, rpc)
        self.isChatterWidget = isChatterWidget
        self.selectionMapping = {}
        self.selectionMappingReverse = {}
        self.labels = []
        self.widgetQtObj = False
        self.currentValue = ''
        self.widget = self.fieldXmlAttributes.get('widget', '')
        if self.widget == 'statusbar':
            self.statusbar_colors = json.loads(self.fieldXmlAttributes.get('statusbar_colors', ''))
            self.statusbar_visible = self.fieldXmlAttributes.get('statusbar_visible', '').split(',')
        self.getQtObject()

        if self.widgetQtObj:
            self.widgetQtObj.setDisabled(self.readonly)
            if self.invisible:
                self.widgetQtObj.hide()

    def populateMapping(self, items):
        for odooName, interfaceName in items:
            odooName = str(odooName)
            interfaceName = str(interfaceName)
            self.selectionMapping[odooName] = interfaceName
            self.selectionMappingReverse[interfaceName] = odooName

    def statusBar(self):
        self.labels = []
        for visibleText in self.statusbar_visible:
            labelQtObj = QtWidgets.QLabel(visibleText.title())
            labelQtObj.setStyleSheet(constants.LABEL_STYLE_STATUSBAR)
            labelQtObj.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            self.layout().addWidget(labelQtObj)
            self.labels.append(labelQtObj)
        self.layout().setSpacing(0)
        self.layout().setMargin(0)

    def getQtObject(self):
        if self.widget == 'statusbar':
            self.statusBar()
        else:
            self.getCombo()

    def getCombo(self):
        self.labelQtObj = QtWidgets.QLabel(self.fieldStringInterface)
        self.labelQtObj.setStyleSheet(constants.LABEL_STYLE)
        self.widgetQtObj = QtWidgets.QComboBox(self)
        self.widgetQtObj.setStyleSheet(constants.SELECTION_STYLE)
        selectionVals = [('', '')]
        selectionVals.extend(self.fieldPyDefinition.get('selection', []))
        self.populateMapping(selectionVals)
        self.widgetQtObj.addItems(list(self.selectionMappingReverse.keys()))
        self.widgetQtObj.setToolTip(self.tooltip)
        self.widgetQtObj.currentIndexChanged.connect(self.valueChanged)
        if self.required:
            utilsUi.setRequiredBackground(self.widgetQtObj, constants.SELECTION_STYLE)
        self.qtHorizontalWidget.addWidget(self.labelQtObj)
        self.qtHorizontalWidget.addWidget(self.widgetQtObj)
        self.qtHorizontalWidget.addSpacerItem(QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

    def valueChanged(self, newIndex):
        currentValue = str(self.widgetQtObj.currentText())
        self.currentValue = self.selectionMappingReverse.get(currentValue)
        self.valueTemplateChanged()

    def setValue(self, newVal, viewType='form'):
        if isinstance(newVal, bool):
            if not newVal:
                newVal = ''
            else:
                newVal = ''
                utils.logMessage('warning', 'Boolean value %r is passed to char field %r, check better' % (newVal, self.fieldName), 'setValue')

        if self.widget == 'statusbar':
            for label in self.labels:
                if str(label.text()).upper() == str(newVal).upper():
                    label.setStyleSheet(constants.LABEL_STYLE_STATUSBAR_ACTIVE)
                    self.currentValue = newVal
                else:
                    label.setStyleSheet(constants.LABEL_STYLE_STATUSBAR)
            return
        allItems = tuple(self.selectionMapping.keys())
        if newVal not in allItems:
            utils.logMessage('warning', '[%r] Value %r not found in values: %r' % (self.fieldName, newVal, allItems), 'setValue')
            return
        newIndex = allItems.index(newVal)
        if newIndex:
            self.widgetQtObj.setCurrentIndex(newIndex)
        self.currentValue = newVal

    def setReadonly(self, val=False):
        super(Selection, self).setReadonly(val)
        if self.widgetQtObj:
            self.widgetQtObj.setEnabled(not val)
            self.widgetQtObj.setEditable(not val)
            self.widgetQtObj.setDisabled(val)
            if val:
                self.widgetQtObj.setStyleSheet(constants.SELECTION_STYLE + constants.READONLY_STYLE)
            elif self.required:
                utilsUi.setRequiredBackground(self.widgetQtObj, constants.SELECTION_STYLE)
            else:
                if self.required:
                    utilsUi.setRequiredBackground(self.widgetQtObj, constants.SELECTION_STYLE)
                else:
                    self.widgetQtObj.setStyleSheet(constants.SELECTION_STYLE)

    def setInvisible(self, val=False):
        if self.isChatterWidget:
            return
        super(Selection, self).setInvisible(val)
        if self.labelQtObj:
            self.labelQtObj.setContentsMargins(0,0,0,0)
            self.labelQtObj.setHidden(val)
        if self.widgetQtObj:
            self.widgetQtObj.setContentsMargins(0,0,0,0)
            self.widgetQtObj.setHidden(val)

    @property
    def value(self):
        return self.currentValue

    @property
    def valueInterface(self):
        return self.currentValue

    def eraseValue(self):
        self.setValue(False)
