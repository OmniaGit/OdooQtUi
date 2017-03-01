'''
Created on 3 Feb 2017

@author: Daniel Smerghetto
'''
#import xml.etree.ElementTree as ElementTree
import xml.etree.cElementTree as ElementTree
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
from utils import constants
import json


class FormView(object):
    def __init__(self, arch, fieldsNameTypeRel, rpc):
        self.arch = arch
        self.fieldsNameTypeRel = fieldsNameTypeRel
        self.globalMapping = {}
        self.aloneLabels = {}
        self.rpc = rpc

    def computeRecursion(self, parent):
        # TODO:    div name <div name="button_box" class="oe_button_box">
        mainVLay = QtGui.QVBoxLayout()
        for childElement in parent.getchildren():
            childTag = childElement.tag
            if childTag == 'sheet':
                sheetLay = QtGui.QVBoxLayout()
                layout = self.computeRecursion(childElement)
                if layout:
                    sheetLay.addLayout(layout)
                mainVLay.addLayout(sheetLay)
            elif childTag == 'header':
                mapping, layout = self.computeHeader(childElement)
                if layout:
                    mainVLay.addLayout(layout)
                if mapping:
                    self.globalMapping.update(mapping)
            elif childTag == 'div':
                divVlay = QtGui.QVBoxLayout()
                if childElement.text:
                    label = QtGui.QLabel(childElement.text)
                    label.setStyleSheet(constants.LABEL_SEPARATOR)
                    divVlay.addWidget(label)
                childLay = self.computeRecursion(childElement)
                divVlay.addLayout(childLay)
                mainVLay.addLayout(divVlay)
            elif childTag == 'notebook':
                tabWidget = QtGui.QTabWidget()
                tabWidget.setStyleSheet(constants.NOOTEBOOK_STYLE)
                tabWidgetBar = tabWidget.tabBar()
                tabWidgetBar.setStyleSheet(constants.NOOTEBOOK_TABBAR_STYLE)
                for page in childElement.getchildren():
                    pageString = page.attrib.get('string', '')
                    invisible = page.attrib.get('invisible', False)
                    modifInvisible, modifReadonly = utils.evaluateModifiers(page.attrib.get('modifiers', {}))
                    if invisible or modifInvisible:
                        continue
                    pageWidget = QtGui.QWidget()
                    if modifReadonly:
                        pageWidget.setDisabled(True)
                    childLay = self.computeRecursion(page)
                    pageWidget.setLayout(childLay)
                    tabWidget.addTab(pageWidget, pageString)
                mainVLay.addWidget(tabWidget)
            elif childTag == 'group':
                layout = self.computeGroup(childElement)
                mainVLay.addLayout(layout)
            elif childTag == 'button':
                continue
                buttonObj = button.Button(childElement)
                mainVLay.addWidget(buttonObj.qtObject)
                key = 'button_' + unicode(buttonObj.buttonString).replace(' ', '_')
                self.appendToglobalMapping(key, buttonObj)
            elif childTag == 'separator':
                childAttrs = childElement.attrib
                separatorVal = childAttrs.get('string', '')
                if separatorVal:
                    labelObj = QtGui.QLabel(separatorVal)
                    labelObj.setStyleSheet(constants.LABEL_SEPARATOR)
                    mainVLay.addWidget(labelObj)
            elif childTag == 'field':
#                 colspan = childElement.attrib.get('colspan', 1)
#                 col = childElement.attrib.get('col')
                fieldObj = self.computeField(childElement)
                if fieldObj:
                    fieldQt = fieldObj.qtObject
                    if isinstance(fieldQt, QtGui.QLayout):
                        mainVLay.addLayout(fieldQt)
                    elif isinstance(fieldQt, QtGui.QWidget):
                        mainVLay.addWidget(fieldQt)
                    self.appendToglobalMapping('field_' + fieldObj.fieldName, fieldObj)
        mainVLay.setSpacing(3)
        return mainVLay

    @utils.timeit
    def computeArchRecursion(self, parent):
        mainVLay = self.computeRecursion(parent)
        widgetContents = QtGui.QWidget()
        widgetContents.setStyleSheet('background-color:#ffffff;')
        widgetContents.setLayout(mainVLay)
        scroll = QtGui.QScrollArea()
        scroll.setWidget(widgetContents)
        scroll.setWidgetResizable(True)
        outLay = QtGui.QVBoxLayout()
        outLay.addWidget(scroll)
        return outLay

    def computeGroup(self, groupXmlObj):
        def computeCol(val):
            try:
                if isinstance(val, (str, unicode)):
                    val = json.loads(val)
                if val % 2 == 0:
                    return val / 2
                if val == 1:
                    return 1
                return (val - 1) / 2
            except Exception, ex:
                utils.logMessage('error', 'Error during computing col and colspan %r' % (ex), 'computeCol')
                return 1

        childColCount = computeCol(groupXmlObj.attrib.get('col', 2))
        childColCount = childColCount * 2
        globalLay = QtGui.QGridLayout()
        colCount = 0
        rowCount = 0
        for childElement in groupXmlObj.getchildren():
            if colCount >= childColCount:
                colCount = 0
                rowCount = rowCount + 1
            childTag = childElement.tag
            childAttrs = childElement.attrib
            childColSpan = int(childAttrs.get('colspan', 2))
            if childTag == 'group':
                groupString = childAttrs.get('string', '')
                if groupString:
                    label = QtGui.QLabel(groupString)
                    label.setStyleSheet(constants.LABEL_SEPARATOR)
                    globalLay.addWidget(label, rowCount, colCount, 1, childColSpan)
                    rowCount = rowCount + 1
                layout = self.computeGroup(childElement)
                globalLay.addLayout(layout, rowCount, colCount, 1, childColSpan)
                colCount = colCount + childColSpan
            elif childTag == 'newline':
                colCount = 0
                rowCount = rowCount + 1
            elif childTag == 'strong':
                layout = self.computeGroup(childElement)
                globalLay.addLayout(layout, rowCount, colCount, 1, childColSpan)
                colCount = colCount + childColSpan
            elif childTag == 'field':
                fieldObj = self.computeField(childElement)
                if fieldObj:
                    nolabel = childAttrs.get('nolabel', False)
                    if nolabel:
                        labelObj = self.aloneLabels.get(fieldObj.fieldName, '')
                        if labelObj:
                            fieldObj.labelQtObj = labelObj
                            labelObj.setText(fieldObj.fieldName)
                            del self.aloneLabels[fieldObj.fieldName]
                    else:
                        globalLay.addWidget(fieldObj.labelQtObj, rowCount, colCount, 1, 1)
                        colCount = colCount + 1
                        if childColSpan > 1:
                            childColSpan = childColSpan - 1
                    globalLay.addLayout(fieldObj.widgetLyQtObject, rowCount, colCount, 1, childColSpan)
                    self.appendToglobalMapping('field_' + fieldObj.fieldName, fieldObj)
                    colCount = colCount + childColSpan
            elif childTag == 'separator':
                separatorVal = childAttrs.get('string', '')
                if separatorVal:
                    labelObj = QtGui.QLabel(separatorVal)
                    labelObj.setStyleSheet(constants.LABEL_SEPARATOR)
                    globalLay.addWidget(labelObj, rowCount, colCount, 1, childColSpan)
                    colCount = 0
                    rowCount = rowCount + 1
            elif childTag == 'label':
                fieldRelated = childAttrs.get('for', '')
                labelObj = QtGui.QLabel()
                labelObj.setStyleSheet(constants.LABEL_STYLE)
                self.aloneLabels[fieldRelated] = labelObj
                globalLay.addWidget(labelObj, rowCount, colCount, 1, childColSpan)
                colCount = colCount + childColSpan
            elif childTag == 'button':
                buttonObj = button.Button(childElement)
                globalLay.addWidget(buttonObj.qtObject, rowCount, colCount, 1, childColSpan)
                key = 'button_' + unicode(buttonObj.buttonString).replace(' ', '_')
                self.appendToglobalMapping(key, buttonObj)
                colCount = colCount + childColSpan
        return globalLay

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

    def computeHeader(self, archHeader):
        mapping = {}

        def commonAppend(key, vals):
            if key not in mapping:
                mapping[key] = vals
            else:
                utils.logMessage('warning', 'multiple widgets with the same key: %r' % (key), 'computeHeader')

        headerLayout = QtGui.QHBoxLayout()
        for xmlObj in archHeader.getchildren():
            if xmlObj.tag == 'button':
                buttonObj = button.Button(xmlObj)
                headerLayout.addWidget(buttonObj.qtObject)
                commonAppend('button_header_' + unicode(buttonObj.buttonString).replace(' ', '_'), buttonObj)
            elif xmlObj.tag == 'field':
                fieldObj = self.computeField(xmlObj)
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
                commonAppend('field_header_' + unicode(fieldName), fieldObj)
            else:
                pass
        return mapping, headerLayout

    def computeArch(self):
        if self.arch:
            return self.computeArchRecursion(ElementTree.XML(self.arch))
