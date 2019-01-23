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
    def __init__(self, qtParent, xmlField, fieldsDefinition, rpc):
        super(Selection, self).__init__(qtParent, xmlField, fieldsDefinition, rpc)
        self.selectionMapping = {}
        self.selectionMappingReverse = {}
        self.labels = []
        self.qDoubleSpinBoxValue = False
        self.currentValue = ''
        self.widget = self.fieldXmlAttributes.get('widget', '')
        if self.widget == 'statusbar':
            self.statusbar_colors = json.loads(self.fieldXmlAttributes.get('statusbar_colors', ''))
            self.statusbar_visible = self.fieldXmlAttributes.get('statusbar_visible', '').split(',')
        self.getQtObject()

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
            self.addWidget(labelQtObj)
            self.labels.append(labelQtObj)
        self.setSpacing(0)
        self.setMargin(0)

    def getQtObject(self):
        if self.widget == 'statusbar':
            self.statusBar()
        else:
            self.getCombo()

    def getCombo(self):
        self.labelQtObj = QtWidgets.QLabel(self.fieldStringInterface)
        self.labelQtObj.setStyleSheet(constants.LABEL_STYLE)
        self.qDoubleSpinBoxValue = QtWidgets.QComboBox(self)
        self.qDoubleSpinBoxValue.setStyleSheet(constants.SELECTION_STYLE)
        selectionVals = [('', '')]
        selectionVals.extend(self.fieldPyDefinition.get('selection', []))
        self.populateMapping(selectionVals)
        self.qDoubleSpinBoxValue.addItems(list(self.selectionMappingReverse.keys()))
        self.qDoubleSpinBoxValue.setToolTip(self.tooltip)
        self.qDoubleSpinBoxValue.currentIndexChanged.connect(self.valueChanged)
        if self.required:
            utilsUi.setRequiredBackground(self.qDoubleSpinBoxValue, constants.SELECTION_STYLE)
        self.qtHorizontalWidget.addWidget(self.labelQtObj)
        self.qtHorizontalWidget.addWidget(self.qDoubleSpinBoxValue)
        self.qtHorizontalWidget.addSpacerItem(QtWidgets.QSpacerItem(40, 40, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

    def valueChanged(self, newIndex):
        currentValue = str(self.qDoubleSpinBoxValue.currentText())
        self.currentValue = self.selectionMappingReverse.get(currentValue)
        self.valueTemplateChanged()

    def setValue(self, newVal):
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
                    return
        allItems = tuple(self.selectionMapping.keys())
        if newVal not in allItems:
            utils.logMessage('warning', '[%r] Value %r not found in values: %r' % (self.fieldName, newVal, allItems), 'setValue')
            return
        newIndex = allItems.index(newVal)
        if newIndex:
            self.qDoubleSpinBoxValue.setCurrentIndex(newIndex)
        self.currentValue = newVal

    @property
    def value(self):
        return self.currentValue

    @property
    def valueInterface(self):
        return self.currentValue

    def eraseValue(self):
        self.setValue(False)
