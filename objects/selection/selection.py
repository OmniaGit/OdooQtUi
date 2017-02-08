'''
Created on 06 feb 2017

@author: Daniel
'''
from PyQt4 import QtGui
from utils import utils
from objects.fieldTemplate import OdooFieldTemplate


class Selection(OdooFieldTemplate):
    def __init__(self, xmlField, fieldsDefinition):
        super(Selection, self).__init__(xmlField, fieldsDefinition)
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
        self.populateMapping(self.fieldDefinition.get('selection', []))
        self.widgetQtObj.addItems(self.selectionMappingReverse.keys())
        self.widgetQtObj.setToolTip(self.fieldDefinition.get('help', ''))
        self.hboxLay.addWidget(self.widgetQtObj)
        return self.hboxLay

    @property
    def value(self):
        return self.currentValue
