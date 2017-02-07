'''
Created on 06 feb 2017

@author: Daniel
'''
from PyQt4 import QtGui
from objects import button
from utils import utils
from objects.selection.selection import Selection
    

def computeField(xmlObj, fieldsDefinition):
    fieldAttributes = xmlObj.attrib
    fieldName = fieldAttributes.get('name','')
    fieldDefinition = fieldsDefinition.get(fieldName, {})
    fieldType = fieldDefinition.get('type', False)
    fieldObj = None
    if fieldType == 'selection':
        fieldObj = Selection(xmlObj, fieldsDefinition)
    elif fieldType == 'char':
        pass
    elif fieldType == 'integer':
        pass
    elif fieldType == 'float':
        pass
    elif fieldType == 'datetime':
        pass
    elif fieldType == 'many2one':
        pass
    elif fieldType == 'many2many':
        pass
    elif fieldType == 'text':
        pass
    elif fieldType == 'boolean':
        pass
    return fieldObj


def computeHeader(archHeader, fieldsDefinition):
    mapping = {}

    def commonAppend(key, vals):
        if key not in mapping:
            mapping[key] = vals
        else:
            utils.launchMessage('multiple widgets with the same key: %r' % (key), 'warning')

    headerLayout = QtGui.QHBoxLayout()
    for xmlObj in archHeader._children:
        if xmlObj.tag == 'button':
            buttonObj = button.Button(xmlObj)
            headerLayout.addWidget(buttonObj.qtObject)
            commonAppend('button_' + unicode(buttonObj.buttonString).replace(' ', '_'), buttonObj)
        elif xmlObj.tag == 'field':
            fieldObj = computeField(xmlObj, fieldsDefinition)
            fieldQt = fieldObj.qtObject
            fieldName = fieldObj.fieldName
            if not fieldQt:
                utils.logMessage('warning', 'Qt field %r could not be loaded' % (fieldName), 'computeHeader')
                continue
            if isinstance(fieldQt, QtGui.QLayout):
                headerLayout.addLayout(fieldQt)
            elif isinstance(fieldQt, QtGui.QWidget):
                headerLayout.addWidget(fieldQt)
            else:
                utils.logMessage('warning', 'Field %r could not be added to layout' % (fieldName), 'computeHeader')
                continue
            commonAppend('field_' + unicode(fieldName), fieldObj)
        else:
            pass
    return mapping, headerLayout
        
    