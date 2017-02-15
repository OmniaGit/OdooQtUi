'''
Created on 02 feb 2017

@author: Daniel
'''
from PyQt4 import QtGui, QtCore
from utils import utils


class OdooFieldTemplate(QtCore.QObject, object):
    
    value_changed_signal = QtCore.pyqtSignal(QtCore.QString)

    def __init__(self, xmlField, fieldsDefinition, rpc):
        self.rpc = rpc
        self.fieldAttributes = xmlField.attrib
        self.fieldName = self.fieldAttributes.get('name', '')
        self.modifiers = self.fieldAttributes.get('modifiers', {})
        self.on_change = self.fieldAttributes.get('on_change', '')
        self.fieldDefinition = fieldsDefinition.get(self.fieldName, {})
        self.readonly = utils.evaluateBoolean(self.fieldDefinition.get('readonly', False))
        self.required = utils.evaluateBoolean(self.fieldDefinition.get('required', False))
        self.invisible = utils.evaluateBoolean(self.fieldDefinition.get('invisible', False))
        self.tooltip = self.fieldDefinition.get('help', '')
        self.fieldType = self.fieldDefinition.get('type', '')
        self.labelString = self.fieldDefinition.get('string', '')
        self.change_default = utils.evaluateBoolean(self.fieldDefinition.get('change_default', False))
        self.searchable = utils.evaluateBoolean(self.fieldDefinition.get('searchable', True))
        self.manual = utils.evaluateBoolean(self.fieldDefinition.get('manual', False))
        self.depends = self.fieldDefinition.get('depends', [])
        self.related = self.fieldDefinition.get('related', [])
        self.company_dependent = utils.evaluateBoolean(self.fieldDefinition.get('company_dependent', False))
        self.sortable = utils.evaluateBoolean(self.fieldDefinition.get('sortable', True))
        self.store = utils.evaluateBoolean(self.fieldDefinition.get('store', True))
        self.labelQtObj = None
        self.widgetQtObj = None
        self.initVal = ''
        self.currentValue = ''
        self.changed = False
        self.hboxLay = QtGui.QHBoxLayout()
        self.invisibleConditions, self.readonlyConditions = utils.evaluateModifiers(self.modifiers)
        return super(OdooFieldTemplate, self).__init__()

    @property
    def qtObject(self):
        return self.hboxLay

    @property
    def value(self):
        return self.currentValue

    def valueTemplateChanged(self):
        self.value_changed_signal.emit(self.fieldName)

    def setValue(self, newVal):
        utils.logMessage('warning', 'setValue not implemented for field: %r' % (self.fieldName), 'setValue')

    def setReadonly(self, val=False):
        utils.logMessage('warning', 'setReadonly not implemented for field: %r' % (self.fieldName), 'setReadonly')
        
    def valueChanged(self):
        utils.logMessage('warning', 'valueChanged not implmented for field: %r' % (self.fieldName), 'valueChanged')
        