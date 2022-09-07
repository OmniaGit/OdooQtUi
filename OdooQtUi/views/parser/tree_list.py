'''
Created on 3 Feb 2017

@author: Daniel Smerghetto
'''
import json
import xml.etree.cElementTree as ElementTree
from PySide2 import QtWidgets
from OdooQtUi.utils_odoo_conn import constants
from OdooQtUi.utils_odoo_conn import utilsUi
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
from OdooQtUi.objects.text.text import TextHtml
from OdooQtUi.objects.one2many.one2many import One2many
from OdooQtUi.utils_odoo_conn import utils
from OdooQtUi.utils_odoo_conn.utils import timeit


class TreeViewList(QtWidgets.QWidget):
    def __init__(self,
                 qtParent,
                 arch,
                 fieldsNameTypeRel,
                 viewCheckBoxes={},
                 odooConnector=None):
        super(TreeViewList, self).__init__(qtParent)
        self.arch = arch
        self.odooConnector = odooConnector
        self.fieldsNameTypeRel = fieldsNameTypeRel
        self.globalMapping = {}
        self.orderedFields = []
        self.widgets_to_add_in_line = {}
        self.tableWidget = False
        self.viewCheckBoxes = viewCheckBoxes
        self.widgetContents = None

    def computeRecursion(self, parent):
        headers = []
        mainVLay = QtWidgets.QVBoxLayout()
        mainVLay.setMargin(0)
        mainVLay.setSpacing(0)
        for childElement in parent: #.getchildren():
            childTag = childElement.tag
            if childTag == 'field':
                fieldName = childElement.attrib.get('name', '')
                self.orderedFields.append(fieldName)
                headers.append(self.fieldsNameTypeRel.get(fieldName, {}).get('string', fieldName))
            elif childTag == 'button':
                headers.append('')
                self.orderedFields.append('')
            self.widgets_to_add_in_line[len(self.orderedFields) - 1] = childElement
        self.tableWidget = QtWidgets.QTableWidget()
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        flagsDict = {}
        if self.viewCheckBoxes:
            flagsDict = self.viewCheckBoxes
        utilsUi.commonPopulateTable(headers, [], self.tableWidget, flagsDict)
        mainVLay.addWidget(self.tableWidget)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        return mainVLay

    def appendToglobalMapping(self, key, value):
        self.globalMapping.update({key: value})

    def computeWidget(self, xmlObj):
        # if xmlObj.tag == 'field':
        #     field_obj = self.computeField(xmlObj)
        #     if field_obj:
        #         #self.appendToglobalMapping('field_' + field_obj.fieldName)
        #         return field_obj
        if xmlObj.tag == 'button':
            button_obj = self.computeButton(xmlObj)
            if button_obj:
                #self.appendToglobalMapping('button_' + button_obj.label, button_obj)
                return button_obj
                
    def computeButton(self, xmlObj):
        button = False
        attrs = xmlObj.attrib
        odoo_func_name = attrs.get('name', '')
        icon = attrs.get('icon', '')
        butt_type = attrs.get('type', '')
        attrs_extra = attrs.get('attrs', '')
        label = attrs.get('string', '')
        modifiers = json.loads(attrs.get('modifiers', '{}'))
        context = attrs.get('context', {})
        if butt_type == 'object': # Call Odoo function
            button = QtWidgets.QPushButton(parent=self.tableWidget)
            button.setText(label)
        if button:
            button.record = None
            button.context = context
            button.butt_type = butt_type
            button.odoo_func = odoo_func_name
            button.label = label
            button.modifiers = modifiers
            button.readonly = utils.evaluateBoolean(attrs.get('readonly', False))
            button.required = utils.evaluateBoolean(attrs.get('required', False))
            button.invisible = utils.evaluateBoolean(attrs.get('invisible', False))
        button.setStyleSheet(constants.BUTTON_STYLE_REVERSED)
        return button

    def computeField(self, xmlObj):
        fieldAttributes = xmlObj.attrib
        fieldName = fieldAttributes.get('name', '')
        fieldDefinition = self.fieldsNameTypeRel.get(fieldName, {})
        fieldType = fieldDefinition.get('type', False)
        fieldObj = None
        if fieldType == 'selection':
            fieldObj = Selection(self, xmlObj, self.fieldsNameTypeRel, self.rpc)
        elif fieldType == 'char':
            fieldObj = Charachter(self, xmlObj, self.fieldsNameTypeRel, self.rpc)
        elif fieldType == 'integer':
            fieldObj = Integer(self, xmlObj, self.fieldsNameTypeRel, self.rpc)
        elif fieldType == 'float':
            fieldObj = Float(self, xmlObj, self.fieldsNameTypeRel, self.rpc)
        elif fieldType == 'datetime':
            fieldObj = Datetime(self, xmlObj, self.fieldsNameTypeRel, self.rpc)
        elif fieldType == 'many2one':
            fieldObj = Many2one(self, xmlObj, self.fieldsNameTypeRel, self.rpc, self.odooConnector)
        elif fieldType == 'many2many':
            fieldObj = Many2many(self, xmlObj, self.fieldsNameTypeRel, self.rpc, self.odooConnector, parent_view_type='tree')
        elif fieldType == 'one2many':
            fieldObj = One2many(self, xmlObj, self.fieldsNameTypeRel, self.rpc, self.odooConnector, parent_view_type='tree')
        elif fieldType == 'text':
            fieldObj = Text(self, xmlObj, self.fieldsNameTypeRel, self.rpc)
        elif fieldType == 'html':
            fieldObj = TextHtml(self, xmlObj, self.fieldsNameTypeRel, self.rpc)
        elif fieldType == 'date':
            fieldObj = Date(self, xmlObj, self.fieldsNameTypeRel, self.rpc)
        elif fieldType == 'boolean':
            fieldObj = Boolean(self, xmlObj, self.fieldsNameTypeRel, self.rpc)
        return fieldObj

    def computeArchRecursion(self, parent):
        mainVLay = self.computeRecursion(parent)
        self.setStyleSheet(constants.TREE_LIST_BACKGROUND_COLOR)
        self.setLayout(mainVLay)

    def computeArch(self):
        if self.arch:
            return self.computeArchRecursion(ElementTree.XML(self.arch.encode('utf-8')))
