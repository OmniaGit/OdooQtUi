'''
Created on 3 Feb 2017

@author: Daniel Smerghetto
'''
import xml.etree.cElementTree as ElementTree
from PySide import QtGui
from OdooQtUi.utils_odoo_conn import constants, utilsUi
from OdooQtUi.utils_odoo_conn import utils
from OdooQtUi.objects.selection.selection import Selection
from OdooQtUi.objects.boolean.boolean import Boolean
from OdooQtUi.objects.char.char import Charachter
from OdooQtUi.objects.date.date import Date
from OdooQtUi.objects.datetimee.datetimee import Datetime
from OdooQtUi.objects.float.float import Float
from OdooQtUi.objects.integer.integer import Integer
from OdooQtUi.objects.many2many.many2many import Many2many
from OdooQtUi.objects.many2one.many2one import Many2one
from OdooQtUi.objects.text.text import Text
from OdooQtUi.objects.one2many.one2many import One2many



class TreeViewList(object):

    def __init__(self, arch, fieldsNameTypeRel, rpc, viewCheckBoxes={}, odooConnector=None):
        self.arch = arch
        self.odooConnector = odooConnector
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
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        flagsDict = {}
        if self.viewCheckBoxes:
            flagsDict = self.viewCheckBoxes
        utilsUi.commonPopulateTable(self.orderedFields, [], self.tableWidget, flagsDict)
        mainVLay.addWidget(self.tableWidget)
        self.tableWidget.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.tableWidget.horizontalHeader().setStyleSheet('::section {background-color:#a2b0ff;color:black;font-weight:bold;}')
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
            fieldObj = Many2one(xmlObj, self.fieldsNameTypeRel, self.rpc, self.odooConnector)
        elif fieldType == 'many2many':
            fieldObj = Many2many(xmlObj, self.fieldsNameTypeRel, self.rpc, self.odooConnector)
        elif fieldType == 'one2many':
            fieldObj = One2many(xmlObj, self.fieldsNameTypeRel, self.rpc, self.odooConnector)
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
        self.widgetContents.setStyleSheet(constants.TREE_LIST_BACKGROUND_COLOR)
        self.widgetContents.setLayout(mainVLay)
        outLay = QtGui.QVBoxLayout()
        outLay.addWidget(self.widgetContents)
        return outLay

    def computeArch(self):
        if self.arch:
            return self.computeArchRecursion(ElementTree.XML(self.arch.encode('utf-8')))
