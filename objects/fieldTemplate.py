'''
Created on 02 feb 2017

@author: Daniel
'''
from PyQt4 import QtGui
from utils import utils


class OdooFieldTemplate(object):
    def __init__(self, xmlField, fieldsDefinition):
        self.fieldAttributes = xmlField.attrib
        self.fieldName = self.fieldAttributes.get('name','')
        self.modifiers = self.fieldAttributes.get('modifiers', {})
        self.fieldDefinition = fieldsDefinition.get(self.fieldName, {})
        self.readonly = utils.evaluateBoolean(self.fieldDefinition.get('readonly', False))
        self.required = utils.evaluateBoolean(self.fieldDefinition.get('required', False))
        self.invisible = utils.evaluateBoolean(self.fieldDefinition.get('invisible', False))
        self.tooltip = self.fieldDefinition.get('help', '')
        self.fieldType = self.fieldDefinition.get('type', '')
        self.labelString = self.fieldDefinition.get('string', '')
        self.labelQtObj = None
        self.widgetQtObj = None
        self.initVal = ''
        self.currentValue = ''
        self.changed = False
        self.invisibleConditions, self.readonlyConditions = utils.evaluateModifiers(self.modifiers)
        return super(OdooFieldTemplate, self).__init__()


        
    @property
    def qtObject(self):
        return QtGui.QHBoxLayout()
