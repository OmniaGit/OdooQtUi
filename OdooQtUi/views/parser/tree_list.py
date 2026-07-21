'''
Created on 3 Feb 2017

@author: Daniel Smerghetto
'''
import json
import xml.etree.cElementTree as ElementTree
from PySide6 import QtWidgets
from PySide6 import QtCore
from ...utils_odoo_conn import constants, utilsUi, utils
from ...objects.selection.selection import Selection
from ...objects.boolean.boolean import Boolean
from ...objects.char.char import Charachter
from ...objects.date.date import Date
from ...objects.datetimee.datetimee import Datetime
from ...objects.float.float import Float
from ...objects.integer.integer import Integer
from ...objects.many2many.many2many import Many2many
from ...objects.many2one.many2one import Many2one
from ...objects.text.text import Text
from ...objects.text.text import TextHtml
from ...objects.one2many.one2many import One2many

class OdooQtUiPushButton(QtWidgets.QPushButton):
    def __init__(self,
                 parent,
                 xmlObj):
        super().__init__(parent)
        #
        self.attrs = xmlObj.attrib
        odoo_func_name = self.attrs.get('name', '')
        #icon = self.attrs.get('icon', '')
        butt_type = self.attrs.get('type', '')
        #attrs_extra = self.attrs.get('attrs', '')
        label = self.attrs.get('string', '')
        modifiers = json.loads(self.attrs.get('modifiers', '{}'))
        context = self.attrs.get('context', {})
        self.record = None
        if butt_type == 'object': # Call Odoo function
            self.setText(label)
            self.context = context
            self.butt_type = butt_type
            self.odoo_func = odoo_func_name
            self.label = label
            self.modifiers = modifiers
            self.update_eval_attributes()
        self.setStyleSheet(constants.BUTTON_STYLE_REVERSED)

    def update_eval_attributes(self):
        self.modifiers={'readonly': self.attrs.get('readonly', False),
                        'required': self.attrs.get('required', False),
                        'invisible': self.attrs.get('invisible', False)
                        }
        if self.record:
            self.readonly = utils.evaluateBoolean(self.attrs.get('readonly', False), self.record)
            self.required = utils.evaluateBoolean(self.attrs.get('required', False), self.record)
            self.invisible = utils.evaluateBoolean(self.attrs.get('invisible', False), self.record)
        else:
            self.readonly = utils.evaluateBoolean(self.attrs.get('readonly', False))
            self.required = utils.evaluateBoolean(self.attrs.get('required', False))
            self.invisible = utils.evaluateBoolean(self.attrs.get('invisible', False))
        #
        def hideButtonWithStyle(butt, flag):
            if butt:
                if flag:
                    butt.setStyleSheet('color:#dddddd; border:none;background-color:#dddddd;')
                else:
                    butt.setStyleSheet(constants.BUTTON_STYLE_REVERSED)
                butt.setDisabled(flag)
        hideButtonWithStyle(self, self.invisible)

class TreeViewList(QtWidgets.QWidget):
    drop_in = QtCore.Signal(QtCore.QEvent)
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
        self.setAcceptDrops(True)

    def dragEnterEvent(self, e):
        e.accept()

    def dropEvent(self, e):
        self.drop_in.emit(e)
        e.accept()        

    def computeRecursion(self, parent):
        headers = []
        mainVLay = QtWidgets.QVBoxLayout()
        mainVLay.setContentsMargins(0, 0, 0, 0)
        mainVLay.setSpacing(0)
        for childElement in parent: #.getchildren():
            childTag = childElement.tag
            if childTag == 'field':
                fieldName = childElement.attrib.get('name', '')
                self.orderedFields.append(fieldName)
                headers.append(self.fieldsNameTypeRel.get(fieldName, {}).get('string', fieldName))
            elif childTag == 'button':
                function_call = childElement.attrib.get('name', '')
                name =  childElement.attrib.get('string', '')
                headers.append(name)
                self.orderedFields.append(function_call)
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
        return OdooQtUiPushButton(self.tableWidget,
                                  xmlObj)

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
