'''
Created on 06 feb 2017

@author: Daniel
'''
from PyQt4 import QtGui
from objects import button
from utils import utils
from objects.selection.selection import Selection
from cookielib import vals_sorted_by_key
    

def computeField(xmlObj, fieldsDefinition):
    fieldAttributes = xmlObj.attrib
    fieldName = fieldAttributes.get('name','')
    fieldDefinition = fieldsDefinition.get(fieldName, {})
    fieldType = fieldDefinition.get('type', False)
    fieldObj = None
    fieldQt = None
    if fieldType == 'selection':
        fieldObj = Selection(xmlObj, fieldsDefinition)
        fieldQt = fieldObj.getQtObject()
    return fieldObj, fieldQt

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
            buttonQt = buttonObj.getQtObject()
            headerLayout.addWidget(buttonQt)
            commonAppend(buttonObj.buttonString, {'buttonObj': buttonObj, 'buttonQt': buttonQt})
        elif xmlObj.tag == 'field':
            fieldObj, fieldQt = computeField(xmlObj, fieldsDefinition)
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
            commonAppend(fieldName, {'fieldObj': fieldObj, 'fieldQt': fieldQt})
        else:
            pass
    return mapping, headerLayout
        
    