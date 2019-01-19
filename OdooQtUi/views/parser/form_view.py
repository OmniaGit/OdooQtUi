'''
Created on 3 Feb 2017

@author: Daniel Smerghetto
'''
import json
import logging
import xml.etree.cElementTree as ElementTree

from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets

from OdooQtUi.utils_odoo_conn import utils, utilsUi
from OdooQtUi.utils_odoo_conn import constants
from OdooQtUi.objects import button
from OdooQtUi.objects.selection.selection import Selection
from OdooQtUi.objects.boolean.boolean import Boolean
from OdooQtUi.objects.char.char import Charachter
from OdooQtUi.objects.date.date import Date
from OdooQtUi.objects.datetimee.datetimee import Datetime
from OdooQtUi.objects.float.float import Float
from OdooQtUi.objects.integer.integer import Integer
from OdooQtUi.objects.many2many.many2many import Many2many
from OdooQtUi.objects.many2one.many2one import Many2one
from OdooQtUi.objects.one2many.one2many import One2many
from OdooQtUi.objects.binary.binary import Binary
from OdooQtUi.objects.text.text import Text


class FormView(QtCore.QObject, object):

    nootebook_changed_signal = QtCore.Signal(int)

    def __init__(self, arch, fieldsNameTypeRel, rpc, useHeader=False, useChatter=False, odooConnector=None):
        super(FormView, self).__init__()
        self.odooConnector = odooConnector
        self.arch = arch
        self.fieldsNameTypeRel = fieldsNameTypeRel
        self.globalMapping = {}
        self.aloneLabels = {}
        self.rpc = rpc
        self.notebookTabsNotComputed = {}
        self.nootebookFieldsToCompute = {}  # {nootebookIndex: {'fieldName': fieldObj}}
        self.useHeader = useHeader
        self.useChatter = useChatter

    def computeNooteBookPage(self, pageIndex=False):
        values = self.notebookTabsNotComputed.get(pageIndex, {})
        if values:
            del self.notebookTabsNotComputed[pageIndex]
            self.nootebook_changed_signal.emit(pageIndex)

    def computeRecursion(self, parent, nootebookIndex=0):
        # TODO:    div name <div name="button_box" class="oe_button_box">
        mainVLay = QtWidgets.QVBoxLayout()
        for childElement in parent.getchildren():
            childTag = childElement.tag
            if childTag == 'sheet':
                sheetLay = QtWidgets.QVBoxLayout()
                utilsUi.setLayoutMarginAndSpacing(sheetLay)
                layout = self.computeRecursion(childElement)
                if layout:
                    sheetLay.addLayout(layout)
                mainVLay.addLayout(sheetLay)
            elif childTag == 'header':
                logging.warning('Header not implemented')
                continue
                mapping, layout = self.computeHeader(childElement, self.useHeader)
                if layout:
                    if self.useHeader:
                        mainVLay.addLayout(layout)
                    else:
                        layout.deleteLater()
                if mapping:
                    self.globalMapping.update(mapping)
            elif childTag == 'div':
                divAttrib = childElement.attrib
                divClass = divAttrib.get('class', '')
                divVlay = QtWidgets.QVBoxLayout()
                utilsUi.setLayoutMarginAndSpacing(divVlay)
                if divClass == 'oe_chatter':
                    if not self.useChatter:
                        logging.warning('Chatter not implemented')
                        continue
                    else:
                        self.computeChatter(divVlay, childElement)
                elif childElement.text:
                    label = QtWidgets.QLabel(childElement.text)
                    label.setStyleSheet(constants.LABEL_SEPARATOR)
                    divVlay.addWidget(label)
                    childLay = self.computeRecursion(childElement)
                    divVlay.addLayout(childLay)
                mainVLay.addLayout(divVlay)
            elif childTag == 'notebook':
                self.tabWidget = QtWidgets.QTabWidget()
                self.tabWidget.setStyleSheet(constants.NOOTEBOOK_STYLE)
                self.tabWidgetBar = self.tabWidget.tabBar()
                self.tabWidgetBar.setStyleSheet(constants.NOOTEBOOK_TABBAR_STYLE)
                nootebookIndex = 0
                for page in childElement.getchildren():
                    pageString = page.attrib.get('string', '')
                    invisible = page.attrib.get('invisible', False)
                    modifInvisible, modifReadonly = utils.evaluateModifiers(page.attrib.get('modifiers', {}))
                    if invisible or modifInvisible:
                        continue
                    pageWidget = QtWidgets.QWidget()
                    if modifReadonly:
                        pageWidget.setDisabled(True)
                    if nootebookIndex != 0:
                        self.notebookTabsNotComputed[nootebookIndex] = {'xmlPage': page, 'pageWidget': pageWidget}
                    childLay = self.computeRecursion(page, nootebookIndex)
                    pageWidget.setLayout(childLay)
                    self.tabWidget.addTab(pageWidget, pageString)
                    nootebookIndex = nootebookIndex + 1
                mainVLay.addWidget(self.tabWidget)
                self.tabWidget.computeNooteBookPage = self.computeNooteBookPage
                self.tabWidget.currentChanged.connect(self.computeNooteBookPage)
            elif childTag == 'group':
                layout = self.computeGroup(childElement, nootebookIndex)
                mainVLay.addLayout(layout)
            elif childTag == 'button':
                logging.warning('Buttons not implemented at first level of form')
                continue
                buttonObj = button.Button(childElement)
                key = 'button_' + str(buttonObj.buttonString).replace(' ', '_')
                self.appendToglobalMapping(key, buttonObj)
                mainVLay.addWidget(buttonObj.qtObject)
                divClass = parent.attrib.get('class', '')
                if divClass == 'oe_button_box':
                    buttonObj.qtObject.setHidden(True)
            elif childTag == 'separator':
                childAttrs = childElement.attrib
                separatorVal = childAttrs.get('string', '')
                if separatorVal:
                    labelObj = QtWidgets.QLabel(separatorVal)
                    labelObj.setStyleSheet(constants.LABEL_SEPARATOR)
                    mainVLay.addWidget(labelObj)
            elif childTag == 'field':
                fieldObj = self.computeField(childElement)
                if fieldObj:
                    fieldQt = fieldObj.qtObject
                    if isinstance(fieldQt, QtWidgets.QLayout):
                        mainVLay.addLayout(fieldQt)
                    elif isinstance(fieldQt, QtWidgets.QWidget):
                        mainVLay.addWidget(fieldQt)
                    self.appendToglobalMapping('field_' + fieldObj.fieldName, fieldObj)
            elif childTag == 'h1':
                layout = self.computeGroup(childElement, nootebookIndex)
                mainVLay.addLayout(layout)
            elif childTag == 'label':
                childAttrs = childElement.attrib
                fieldRelated = childAttrs.get('for', '')
                labelObj = QtWidgets.QLabel()
                labelObj.setStyleSheet(constants.LABEL_STYLE)
                self.aloneLabels[fieldRelated] = labelObj
                mainVLay.addWidget(labelObj)
            else:
                logging.warning('Tag %r not supported and not evaluated' % (childElement))
        mainVLay.setSpacing(3)
        return mainVLay

    def computeChatter(self, divVlay, childElement):
        hlay = QtWidgets.QHBoxLayout()
        count = 0
        for fieldObj in childElement.getchildren():
            if fieldObj.tag == 'field':
                pyObject = self.computeField(fieldObj)
                if pyObject:
                    fieldQt = pyObject.qtObject
                    if isinstance(fieldQt, QtWidgets.QLayout):
                        hlay.insertLayout(0, fieldQt)
                        if count == 0:
                            hlay.insertSpacerItem(0, QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum))
                            count = count + 1
                    elif isinstance(fieldQt, QtWidgets.QWidget):
                        hlay.insertWidget(0, fieldQt)
                    self.appendToglobalMapping('field_' + pyObject.fieldName, pyObject)
            else:
                utils.logMessage('warning', 'Unable to compute tag in chatter %r' % (fieldObj.tag), 'computeChatter')
        divVlay.addLayout(hlay)

    def computeArchRecursion(self, parent):
        widgetContents = QtWidgets.QWidget()
        mainVLay = self.computeRecursion(parent)
        widgetContents.setStyleSheet('background-color:#ffffff;')
        widgetContents.setLayout(mainVLay)
        scroll = QtWidgets.QScrollArea()
        scroll.setWidget(widgetContents)
        scroll.setWidgetResizable(True)
        self.outLay = QtWidgets.QVBoxLayout()
        self.outLay.addWidget(scroll)
        return self.outLay

    def computeGroup(self, groupXmlObj, nootebookIndex=0):
        def computeCol(val):
            try:
                if isinstance(val, str):
                    val = json.loads(val)
                if val % 2 == 0:
                    return val / 2
                if val == 1:
                    return 1
                return (val - 1) / 2
            except Exception as ex:
                utils.logMessage('error', 'Error during computing col and colspan %r' % (ex), 'computeCol')
                return 1

        childColCount = computeCol(groupXmlObj.attrib.get('col', 2))
        childColCount = childColCount * 2
        globalLay = QtWidgets.QGridLayout()
        globalLay.setHorizontalSpacing(40)
        colCount = 0
        rowCount = 0
        for childElement in groupXmlObj.getchildren():
            if colCount >= childColCount:
                colCount = 0
                rowCount = rowCount + 1
            childTag = childElement.tag
            childAttrs = childElement.attrib
            utils.logMessage('info', 'create filed: %r' % (childAttrs.get('name')))
            childColSpan = int(childAttrs.get('colspan', 2))
            if childTag == 'group' or childTag == 'h1' or childTag == 'div':
                groupString = childAttrs.get('string', '')
                if groupString:
                    label = QtWidgets.QLabel(groupString)
                    label.setStyleSheet(constants.LABEL_SEPARATOR + 'font-size:17px;margin-top:20px;')
                    globalLay.addWidget(label, rowCount, colCount, 1, childColSpan)
                    rowCount = rowCount + 1
                layout = self.computeGroup(childElement, nootebookIndex)
                globalLay.addLayout(layout, rowCount, colCount, 1, childColSpan)
                colCount = colCount + childColSpan
            elif childTag == 'newline':
                colCount = 0
                rowCount = rowCount + 1
            elif childTag == 'strong':
                layout = self.computeGroup(childElement, nootebookIndex)
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
                    if nootebookIndex > 0 and fieldObj.fieldType in ['many2many', 'one2many']:
                        if nootebookIndex not in list(self.nootebookFieldsToCompute.keys()):
                            self.nootebookFieldsToCompute[nootebookIndex] = {}
                        self.nootebookFieldsToCompute[nootebookIndex][fieldObj.fieldName] = fieldObj
            elif childTag == 'separator':
                separatorVal = childAttrs.get('string', '')
                if separatorVal:
                    labelObj = QtWidgets.QLabel(separatorVal)
                    labelObj.setStyleSheet(constants.LABEL_SEPARATOR)
                    globalLay.addWidget(labelObj, rowCount, colCount, 1, childColSpan)
                    colCount = 0
                    rowCount = rowCount + 1
            elif childTag == 'label':
                fieldRelated = childAttrs.get('for', '')
                labelObj = QtWidgets.QLabel()
                labelObj.setStyleSheet(constants.LABEL_STYLE)
                self.aloneLabels[fieldRelated] = labelObj
                globalLay.addWidget(labelObj, rowCount, colCount, 1, childColSpan)
                colCount = colCount + childColSpan
            elif childTag == 'button':
                buttonObj = button.Button(childElement)
                globalLay.addWidget(buttonObj.qtObject, rowCount, colCount, 1, childColSpan)
                key = 'button_' + str(buttonObj.buttonString).replace(' ', '_')
                self.appendToglobalMapping(key, buttonObj)
                colCount = colCount + childColSpan
            else:
                utils.logMessage('warning', 'Unable to parse element %r' % (childTag), 'computeGroup')
        utilsUi.setLayoutMarginAndSpacing(globalLay)
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
            fieldObj = Many2one(xmlObj, self.fieldsNameTypeRel, self.rpc, self.odooConnector)
        elif fieldType == 'many2many':
            fieldObj = Many2many(xmlObj, self.fieldsNameTypeRel, self.rpc, self.odooConnector)
        elif fieldType == 'text':
            fieldObj = Text(xmlObj, self.fieldsNameTypeRel, self.rpc)
        elif fieldType == 'date':
            fieldObj = Date(xmlObj, self.fieldsNameTypeRel, self.rpc)
        elif fieldType == 'boolean':
            fieldObj = Boolean(xmlObj, self.fieldsNameTypeRel, self.rpc)
        elif fieldType == 'one2many':
            fieldObj = One2many(xmlObj, self.fieldsNameTypeRel, self.rpc, self.odooConnector)
        elif fieldType == 'binary':
            fieldObj = Binary(xmlObj, self.fieldsNameTypeRel, self.rpc)
        else:
            utils.logMessage('warning', 'Field %r not supported' % (fieldType), 'computeField')
        return fieldObj

    def computeHeader(self, archHeader, useHeader=False):
        mapping = {}

        def commonAppend(key, vals):
            if key not in mapping:
                mapping[key] = vals
            else:
                utils.logMessage('warning', 'multiple widgets with the same key: %r' % (key), 'computeHeader')

        headerLayout = QtWidgets.QHBoxLayout()
        utilsUi.setLayoutMarginAndSpacing(headerLayout)
        for xmlObj in archHeader.getchildren():
            if xmlObj.tag == 'button':
                buttonObj = button.Button(xmlObj)
                headerLayout.addWidget(buttonObj.qtObject)
                commonAppend('button_header_' + str(buttonObj.buttonString).replace(' ', '_'), buttonObj)
            elif xmlObj.tag == 'field':
                fieldObj = self.computeField(xmlObj)
                fieldQt = fieldObj.qtObject
                fieldName = fieldObj.fieldName
                if not fieldQt:
                    utils.logMessage('warning', 'Qt field %r could not be loaded' % (fieldName), 'computeHeader')
                    continue
                if isinstance(fieldQt, QtWidgets.QLayout):
                    headerLayout.addLayout(fieldQt)
                elif isinstance(fieldQt, QtWidgets.QWidget):
                    headerLayout.addWidget(fieldQt)
                else:
                    utils.logMessage('warning', 'Field %r could not be added to layout' % (fieldName), 'computeHeader')
                    continue
                commonAppend('field_header_' + str(fieldName), fieldObj)
            else:
                pass
        return mapping, headerLayout

    @utils.timeit
    def computeArch(self):
        if self.arch:
            return self.computeArchRecursion(ElementTree.XML(self.arch.encode('utf-8')))
