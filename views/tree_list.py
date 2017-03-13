'''
Created on 3 Feb 2017

@author: Daniel Smerghetto
'''
import xml.etree.cElementTree as ElementTree
from PyQt4 import QtGui
from PyQt4 import QtCore
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
from utils import constants


class TreeViewList(object):

    def __init__(self, arch, fieldsNameTypeRel, rpc, viewCheckBoxes=False):
        self.arch = arch
        self.fieldsNameTypeRel = fieldsNameTypeRel
        self.globalMapping = {}
        self.orderedFields = []
        self.tableWidget = False
        self.viewCheckBoxes = viewCheckBoxes
        self.rpc = rpc

    def computeRecursion(self, parent):
        mainVLay = QtGui.QVBoxLayout()
        for childElement in parent.getchildren():
            childTag = childElement.tag
            if childTag == 'field':
                fieldObj = self.computeField(childElement)
                if fieldObj:
                    self.orderedFields.append(fieldObj.fieldName)
                    self.appendToglobalMapping('field_' + fieldObj.fieldName, fieldObj)
        self.tableWidget = QtGui.QTableWidget()
        flagsDict = {}
        if self.viewCheckBoxes:
            flagsDict = {0: QtCore.Qt.ItemIsUserCheckable}
        utils.commonPopulateTable(self.orderedFields, [], self.tableWidget, flagsDict)
        mainVLay.addWidget(self.tableWidget)
        return mainVLay

    def appendToglobalMapping(self, key, value):
        self.globalMapping.update({key: value})

    def computeField(self, xmlObj):
        fieldAttributes = xmlObj.attrib
        fieldName = fieldAttributes.get('name', '')
        fieldDefinition = self.fieldsNameTypeRel.get(fieldName, {})
        fieldType = fieldDefinition.get('type', False)
        fieldObj = None
        if fieldType == 'selection':
            fieldObj = Selection(xmlObj, self.fieldsNameTypeRel, self.rpc)
        elif fieldType == 'char':
            fieldObj = Charachter(xmlObj, self.fieldsNameTypeRel, self.rpc)
        elif fieldType == 'integer':
            fieldObj = Integer(xmlObj, self.fieldsNameTypeRel, self.rpc)
        elif fieldType == 'float':
            fieldObj = Float(xmlObj, self.fieldsNameTypeRel, self.rpc)
        elif fieldType == 'datetime':
            fieldObj = Datetime(xmlObj, self.fieldsNameTypeRel, self.rpc)
        elif fieldType == 'many2one':
            fieldObj = Many2one(xmlObj, self.fieldsNameTypeRel, self.rpc)
        elif fieldType == 'many2many':
            fieldObj = Many2many(xmlObj, self.fieldsNameTypeRel, self.rpc)
        elif fieldType == 'text':
            fieldObj = Text(xmlObj, self.fieldsNameTypeRel, self.rpc)
        elif fieldType == 'date':
            fieldObj = Date(xmlObj, self.fieldsNameTypeRel, self.rpc)
        elif fieldType == 'boolean':
            fieldObj = Boolean(xmlObj, self.fieldsNameTypeRel, self.rpc)
        return fieldObj

    def computeArchRecursion(self, parent):
        mainVLay = self.computeRecursion(parent)
        self.widgetContents = QtGui.QWidget()
        self.widgetContents.setStyleSheet('background-color:#ffffff;')
        self.widgetContents.setLayout(mainVLay)
        self.scroll = QtGui.QScrollArea()
        outLay = QtGui.QVBoxLayout()
        outLay.addWidget(self.widgetContents)
        return outLay

    def computeArch(self):
        if self.arch:
            return self.computeArchRecursion(ElementTree.XML(self.arch))
