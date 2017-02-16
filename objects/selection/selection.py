'''
Created on 06 feb 2017

@author: Daniel
'''
from PyQt4 import QtGui
from utils import utils
from objects.fieldTemplate import OdooFieldTemplate


class Selection(OdooFieldTemplate):
    def __init__(self, xmlField, fieldsDefinition, rpc):
        super(Selection, self).__init__(xmlField, fieldsDefinition, rpc)
        self.selectionMapping = {}
        self.selectionMappingReverse = {}
        self.labelQtObj = False
        self.widgetQtObj = False
        self.widget = self.fieldAttributes.get('widget', '')
        if self.widget == 'statusbar':
            self.statusbar_colors = self.fieldAttributes.get('statusbar_colors', '')
            self.statusbar_visible = self.fieldAttributes.get('statusbar_visible', '')
        self.hboxLay = self.getQtObject()

        self.widgetQtObj.setDisabled(self.readonly)
        self.widgetQtObj.setHidden(self.invisible)

    def populateMapping(self, items):
        for odooName, interfaceName in items:
            odooName = unicode(odooName)
            interfaceName = unicode(interfaceName)
            self.selectionMapping[odooName] = interfaceName
            self.selectionMappingReverse[interfaceName] = odooName

    def getQtObject(self):
        self.hboxLay = QtGui.QHBoxLayout()
        self.labelQtObj = QtGui.QLabel(self.labelString)
        self.hboxLay.addWidget(self.labelQtObj)
        self.widgetQtObj = QtGui.QComboBox()
        selectionVals = [('', '')]
        selectionVals.extend(self.fieldDefinition.get('selection', []))
        self.populateMapping(selectionVals)
        self.widgetQtObj.addItems(self.selectionMappingReverse.keys())
        self.widgetQtObj.setToolTip(self.tooltip)
        self.widgetQtObj.currentIndexChanged.connect(self.valueChanged)
        if self.required:
            utils.setRequiredBackground(self.widgetQtObj)
        self.hboxLay.addWidget(self.widgetQtObj)
        return self.hboxLay

    def valueChanged(self, newIndex):
        currentValue = unicode(self.widgetQtObj.currentText())
        self.currentValue = self.selectionMappingReverse.get(currentValue)
        self.valueTemplateChanged()

    def setValue(self, newVal):
        if isinstance(newVal, bool):
            utils.logMessage('warning', 'Boolean value %r is passed to char field %r, check better' % (newVal, self.fieldName), 'setValue')
            newVal = ''
        allItems = self.selectionMapping.keys()
        if newVal not in allItems:
            utils.logMessage('warning', '[%r] Value %r not found in values: %r' % (self.fieldName, newVal, allItems), 'setValue')
            return
        newIndex = allItems.index(newVal)
        if newIndex:
            self.widgetQtObj.setCurrentIndex(newIndex)

    def setReadonly(self, val=False):
        self.widgetQtObj.setEnabled(not val)
        self.widgetQtObj.setEditable(not val)
        self.widgetQtObj.setDisabled(val)

    def setInvisible(self, val=False):
        self.labelQtObj.setHidden(val)
        self.widgetQtObj.setHidden(val)
