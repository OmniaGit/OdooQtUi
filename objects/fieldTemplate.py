'''
Created on 02 feb 2017

@author: Daniel
'''
from PyQt4 import QtGui


class OdooFieldTemplate(object):
    def __init__(self, xmlField, fieldsDefinition):
        self.fieldAttributes = xmlField.attrib
        self.fieldName = self.fieldAttributes.get('name','')
        self.fieldDefinition = fieldsDefinition.get(self.fieldName, {})
        self.fieldType = self.fieldDefinition.get('type', False)
        self.labelString = self.fieldDefinition.get('string', '')
        self.labelQtObj = None
        self.widgetQtObj = None
        return super(OdooFieldTemplate, self).__init__()

    @property
    def qtObject(self):
        return QtGui.QHBoxLayout()