'''
Created on 3 Feb 2017

@author: Daniel Smerghetto
'''
import xml.etree.ElementTree as ElementTree
from PyQt4 import QtGui
from objects import button
from utils import utils
from objects.selection.selection import Selection
from objects.boolean.boolean import Boolean
from objects.char.char import Charachter
from objects.date.date import Date
from objects.datetime.datetime import Datetime
from objects.float.float import Float
from objects.integer.integer import Integer
from objects.many2many.many2many import Many2many
from objects.many2one.many2one import Many2one
from objects.text.text import Text


class FormView(object):
    def __init__(self, arch, fieldsNameTypeRel):
        self.arch = arch
        self.fieldsNameTypeRel = fieldsNameTypeRel
        self.globalMapping = {}

    def computeArchRecursion(self, parent):
        # TODO:    div name <div name="button_box" class="oe_button_box"> 
        mainVLay = QtGui.QVBoxLayout()
        for childElement in parent:
            childTag = childElement.tag
            if childTag == 'sheet':
                sheetLay = QtGui.QVBoxLayout()
                layout = self.computeArchRecursion(childElement)
                if layout:
                    sheetLay.addLayout(layout)
                mainVLay.addLayout(sheetLay)
            elif childTag == 'header':
                mapping, layout = self.computeHeader(childElement, self.fieldsNameTypeRel)
                if layout:
                    mainVLay.addLayout(layout)
                if mapping:
                    self.globalMapping.update(mapping)
            elif childTag == 'div':
                divVlay = QtGui.QVBoxLayout()
                if childElement.text:
                    label = QtGui.QLabel(childElement.text)
                    divVlay.addWidget(label)
                childLay = self.computeArchRecursion(childElement)
                divVlay.addLayout(childLay)
                mainVLay.addLayout(divVlay)
            elif childTag == 'notebook':
                tabWidget = QtGui.QTabWidget()
                for page in childElement._children:
                    pageString = page.attrib.get('string', '')
                    pageWidget = QtGui.QWidget()
                    childLay = self.computeArchRecursion(page)
                    pageWidget.setLayout(childLay)
                    tabWidget.addTab(pageWidget, pageString)
                mainVLay.addWidget(tabWidget)
            elif childTag == 'group':
                colspan = childElement.attrib.get('colspan', 1)
                col = childElement.attrib.get('col')
                mainVLay.addLayout(self.computeArchRecursion(childElement))
            elif childTag == 'button':
                continue
                buttonObj = button.Button(childElement)
                mainVLay.addWidget(buttonObj.qtObject)
                mapping = {'button_' + unicode(buttonObj.buttonString).replace(' ', '_') : buttonObj}
                self.globalMapping.update(mapping)
                mainVLay.addLayout(self.computeArchRecursion(childElement))
            elif childTag == 'field':
                colspan = childElement.attrib.get('colspan', 1)
                col = childElement.attrib.get('col')
                fieldObj = self.computeField(childElement, self.fieldsNameTypeRel)
                if fieldObj:
                    fieldQt = fieldObj.qtObject
                    if isinstance(fieldQt, QtGui.QLayout):
                        mainVLay.addLayout(fieldQt)
                    elif isinstance(fieldQt, QtGui.QWidget):
                        mainVLay.addWidget(fieldQt)
                    mapping = {'field_' + fieldObj.fieldName: fieldObj}
                    self.globalMapping.update(mapping)
        return mainVLay

    def computeField(self, xmlObj, fieldsDefinition):
        fieldAttributes = xmlObj.attrib
        fieldName = fieldAttributes.get('name', '')
        fieldDefinition = fieldsDefinition.get(fieldName, {})
        fieldType = fieldDefinition.get('type', False)
        fieldObj = None
        if fieldType == 'selection':
            fieldObj = Selection(xmlObj, fieldsDefinition)
        elif fieldType == 'char':
            fieldObj = Charachter(xmlObj, fieldsDefinition)
        elif fieldType == 'integer':
            fieldObj = Integer(xmlObj, fieldsDefinition)
        elif fieldType == 'float':
            fieldObj = Float(xmlObj, fieldsDefinition)
        elif fieldType == 'datetime':
            fieldObj = Datetime(xmlObj, fieldsDefinition)
        elif fieldType == 'many2one':
            fieldObj = Many2one(xmlObj, fieldsDefinition)
        elif fieldType == 'many2many':
            fieldObj = Many2many(xmlObj, fieldsDefinition)
        elif fieldType == 'text':
            fieldObj = Text(xmlObj, fieldsDefinition)
        elif fieldType == 'date':
            fieldObj = Date(xmlObj, fieldsDefinition)
        elif fieldType == 'boolean':
            fieldObj = Boolean(xmlObj, fieldsDefinition)
        return fieldObj

    def computeHeader(self, archHeader, fieldsDefinition):
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
                fieldObj = self.computeField(xmlObj, fieldsDefinition)
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

    def computeArch(self):
        if self.arch:
            etreeObj = ElementTree.fromstring(self.arch)
            return self.computeArchRecursion(etreeObj)

    def loadIds(self, odooIds):
        for odooId in odooIds:
            break
