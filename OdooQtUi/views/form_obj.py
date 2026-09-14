# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011-2026 OmniaSolutions and the OdooQtUi contributors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of OdooQtUi, released under the Apache License 2.0.
# Redistributions must keep the attribution in the NOTICE file.
# See the LICENSE and NOTICE files at the root of the project.

'''
Created on 24 Mar 2017

@author: dsmerghetto
'''
import copy
import json
import logging
import xml.etree.cElementTree as ElementTree
from functools import partial
from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

from OdooQtUi.views.templateView import TemplateView
from OdooQtUi.utils_odoo_conn import utils
from OdooQtUi.utils_odoo_conn import utilsUi
from OdooQtUi.utils_odoo_conn import constants
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
from OdooQtUi.objects import button


class TemplateFormView(TemplateView):
    nootebook_changed_signal = QtCore.Signal(int)
    form_changed = QtCore.Signal(str)

    def __init__(self,
                 viewObj,
                 odooConnector=None,
                 hideFormContent=False):
        self.globalMapping = {}
        self.aloneLabels = {}
        self.notebookTabsNotComputed = {}
        # [(invisible expression, callable taking hidden)] for the div, group
        # and page nodes whose visibility depends on the record.
        self.containerModifiers = []
        self.nootebookFieldsToCompute = {}  # {nootebookIndex: {'fieldName': fieldObj}}
        self.requiredFields = {}
        self.readonlyFields = {}
        self.invisibleFields = {}
        self.fieldDefaultVals = {}  # {'fieldName' : fieldval}
        self.skipOnChange = False
        self.readonly = False
        self.activeIds = []         # must be one
        self.hideFormContent = hideFormContent
        #
        super(TemplateFormView, self).__init__(odooConnector=odooConnector,
                                               viewObj=viewObj)
        #
        self.objectsInit = copy.deepcopy(self.fields)
        self._initViewObj()
        self.nootebook_changed_signal.connect(self.updateDataStructure)
        self.setMinimumSize(0, 0)
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        

    def _initViewObj(self):
        if self.fieldsNameTypeRel:
            self.startingFieldValues = self.fieldsNameTypeRel.get('fields', {})
            self.RenderArch()
            self.mappingInterface = self.globalMapping
            self.addToObject()
            self._setFieldModifiers()
        else:
            utils.logWarning('Unable to get fields view definition!', '_initViewObj')

    @utils.timeit
    def RenderArch(self):
        if self.arch:
            self.setStyleSheet(constants.MAIN_STYLE)
            vertical_layout = QtWidgets.QVBoxLayout()
            vertical_layout.setSpacing(0)
            self.computeRecursion(qvboxLayout=vertical_layout,
                                  xmlParent=ElementTree.XML(self.arch.encode('utf-8')))
            verticalSpacer = QtWidgets.QSpacerItem(40, 100, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            vertical_layout.addItem(verticalSpacer)
            self.setLayout(vertical_layout)
        else:
            utils.logWarning('No arch set impossible to compute structure')

    def computeRecursion(self,
                         qvboxLayout=False,
                         xmlParent=None,
                         nootebookIndex=0,
                         row_widget_limit=4):
        # TODO:    div name <div name="button_box" class="oe_button_box">
        row_widget_count = 0
        if not qvboxLayout:
            qvboxLayout = QtWidgets.QVBoxLayout()
            qvboxLayout.setSpacing(0)
            qvboxLayout.setContentsMargins(0, 0, 0, 0)
        if constants.DEBUG:
            line = QtWidgets.QLineEdit()
            line.setStyleSheet("border:2px solid blue;")
            qvboxLayout.addWidget(line)
        row_container = QtWidgets.QHBoxLayout()
        row_container.setSpacing(0)
        #
        for childXlmElement in xmlParent:
            childXmlTag = childXlmElement.tag
            xmlAttrs = childXlmElement.attrib
            if childXmlTag == 'sheet' and not self.hideFormContent:
                self.sheet_layout = self.computeRecursion(qvboxLayout=qvboxLayout,
                                                          xmlParent=childXlmElement)
            elif childXmlTag == 'header' and self.useHeader:
                mapping, layout = self.computeHeader(archHeader=childXlmElement, useHeader=self.useHeader)
                if layout:
                    if self.useHeader:
                        qvboxLayout.addLayout(layout)
                    else:
                        layout.deleteLater()
                if mapping:
                    self.globalMapping.update(mapping)
            elif childXmlTag == 'div':
                divAttrib = childXlmElement.attrib
                divClass = divAttrib.get('class', '')
                if divClass == 'oe_chatter':
                    if not self.useChatter:
                        utils.logWarning('Chatter not implemented')
                        continue
                    else:
                        self.computeChatter(qvboxLayout, childXlmElement)
                elif divClass == 'oe_button_box':
                    pass
                elif divClass == 'oe_title':
                    self.computeRecursion(qvboxLayout=self._conditionalLayout(childXlmElement, qvboxLayout),
                                          xmlParent=childXlmElement)
                elif childXlmElement.text and len(childXlmElement.text.strip()) > 0:
                    divLayout = self._conditionalLayout(childXlmElement, qvboxLayout)
                    label = QtWidgets.QLabel(childXlmElement.text)
                    label.setStyleSheet(constants.LABEL_SEPARATOR)
                    divLayout.addWidget(label)
                    self.computeRecursion(qvboxLayout=divLayout,
                                          xmlParent=childXlmElement)
                else:
                    qvboxLayout.addLayout(row_container)
                    self.computeRecursion(qvboxLayout=self._conditionalLayout(childXlmElement, qvboxLayout),
                                          xmlParent=childXlmElement)
            elif childXmlTag == 'notebook':
                qvboxLayout.addLayout(row_container)
                tabWidget = QtWidgets.QTabWidget(self)
                tabWidget.setStyleSheet(constants.NOOTEBOOK_STYLE)
                tabWidgetBar = tabWidget.tabBar()
                tabWidgetBar.setStyleSheet(constants.NOOTEBOOK_TABBAR_STYLE)
                nootebookIndex = 0
                for page in childXlmElement:
                    pageString = page.attrib.get('string', '')
                    invisible = page.attrib.get('invisible', False)
                    modifInvisible, modifReadonly = utils.evaluateModifiers(page.attrib.get('modifiers', {}))
                    # An expression is not a yes: "not is_company" is a
                    # non-empty string, and read as a boolean it dropped the
                    # page for every record. Only a page that is always hidden
                    # is left out; one that depends on the record is built and
                    # its tab shown or hidden by _setFieldModifiers.
                    constantInvisible = utils.isConstantModifier(invisible) and utils.evaluateExpression(invisible)
                    if constantInvisible or modifInvisible:
                        continue
                    pageWidget = QtWidgets.QWidget(tabWidget)
                    pageVboxLayout = QtWidgets.QVBoxLayout()
                    pageVboxLayout.setSpacing(0)
                    if modifReadonly:
                        pageWidget.setDisabled(True)
                    if nootebookIndex != 0:
                        self.notebookTabsNotComputed[nootebookIndex] = {'xmlPage': page, 'pageWidget': pageWidget}
                    self.computeRecursion(qvboxLayout=pageVboxLayout,
                                          xmlParent=page,
                                          nootebookIndex=nootebookIndex)
                    pageVboxLayout.addSpacerItem(QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
                    pageWidget.setLayout(pageVboxLayout)
                    tabIndex = tabWidget.addTab(pageWidget, pageString)
                    if not utils.isConstantModifier(invisible):
                        self.containerModifiers.append(
                            (invisible, partial(self._setTabHidden, tabWidget, tabIndex)))
                    nootebookIndex = nootebookIndex + 1
                qvboxLayout.addWidget(tabWidget)
                # tabWidget.currentChanged.connect(partial(self.computeNooteBookPage, tabWidget))
            elif childXmlTag == 'group':
                colspan = xmlAttrs.get('col', None)
                if colspan:
                    colspan = eval(colspan)
                else:
                    colspan = row_widget_limit
                qvboxLayout.addLayout(row_container)
                self.computeRecursion(qvboxLayout=self._conditionalLayout(childXlmElement, qvboxLayout),
                                      xmlParent=childXlmElement,
                                      row_widget_limit=colspan)
            elif childXmlTag == 'button':
                buttonObj = button.Button(qtParent=self,
                                          xmlObject=childXlmElement,
                                          model=self.model,
                                          odooConnector=self.odooConnector)
                key = 'button_' + str(buttonObj.buttonName).replace(' ', '_')
                self.appendToglobalMapping(key, buttonObj)
                qvboxLayout.addWidget(buttonObj)
                divClass = xmlParent.attrib.get('class', '')
                if divClass == 'oe_button_box':
                    buttonObj.setHidden(True)
            elif childXmlTag == 'separator':
                childAttrs = childXlmElement.attrib
                separatorVal = childAttrs.get('string', '')
                if separatorVal:
                    labelObj = QtWidgets.QLabel(separatorVal)
                    labelObj.setStyleSheet(constants.LABEL_SEPARATOR)
                    qvboxLayout.addWidget(labelObj)
            elif childXmlTag == 'field':
                fieldQHLayout = self.computeField(childXlmElement)
                if fieldQHLayout:
                    row_container.addWidget(fieldQHLayout)
                    row_widget_count += 2
                    self.appendToglobalMapping('field_' + fieldQHLayout.fieldName, fieldQHLayout)
            elif childXmlTag == 'h1':
                self.computeRecursion(qvboxLayout=qvboxLayout,
                                      xmlParent=childXlmElement)
            elif childXmlTag == 'label':
                childAttrs = childXlmElement.attrib
                fieldRelated = childAttrs.get('for', False)
                if fieldRelated:
                    continue
                labelObj = False
                if fieldRelated:
                    labelObj = QtWidgets.QLabel()
                    self.aloneLabels[fieldRelated] = labelObj
                fieldRelated = childAttrs.get('string', False)
                if fieldRelated:
                    labelObj = QtWidgets.QLabel(fieldRelated)
                if labelObj:
                    labelObj.setStyleSheet(constants.LABEL_STYLE)
                    qvboxLayout.addWidget(labelObj)
            else:
                utils.logWarning('Tag %r not supported and not evaluated' % (childXlmElement))
            if row_widget_count >= row_widget_limit:
                row_widget_count = 0
                qvboxLayout.addLayout(row_container)
                row_container = QtWidgets.QHBoxLayout()
                row_container.setSpacing(0)
                # no more available on pyside row_container.setMargin(0)
        if constants.DEBUG:
            line = QtWidgets.QLineEdit()
            line.setStyleSheet("border:2px solid blue;")
            qvboxLayout.addWidget(line)
        if not row_container.parent():
            qvboxLayout.addLayout(row_container)
        return qvboxLayout

    def _conditionalLayout(self, xmlElement, parentLayout):
        """The layout the children of a div or a group go into.

        Odoo 17 and later hide a whole block with `invisible` on its container
        -- "Potential duplicates", the company name of a person -- far more
        often than on the fields inside it. A layout cannot be hidden, so a
        container with an `invisible` gets a widget of its own, and the
        expression is kept to be evaluated against the record by
        _setFieldModifiers. One without it goes straight into the parent layout
        as it always did.
        """
        invisible = xmlElement.attrib.get('invisible')
        if invisible is None or (utils.isConstantModifier(invisible)
                                 and not utils.evaluateExpression(invisible)):
            return parentLayout
        container = QtWidgets.QWidget(self)
        layout = QtWidgets.QVBoxLayout(container)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        parentLayout.addWidget(container)
        if utils.isConstantModifier(invisible):
            # Always hidden: built all the same, since the fields inside still
            # hold values the other expressions read.
            container.setHidden(True)
        else:
            self.containerModifiers.append((invisible, container.setHidden))
        return layout

    def _setTabHidden(self, tabWidget, tabIndex, hidden):
        tabWidget.setTabVisible(tabIndex, not hidden)

    def _setContainerModifiers(self, values, context):
        for expression, setHidden in self.containerModifiers:
            setHidden(utils.evaluateExpression(expression, values, context))

    def computeHeader(self, archHeader, useHeader=False):
        mapping = {}

        def commonAppend(key, vals):
            if key not in mapping:
                mapping[key] = vals
            else:
                utils.logMessage('warning', 'multiple widgets with the same key: %r' % (key), 'computeHeader')

        # Two rows and not one: the buttons where Odoo puts them, and the
        # statusbar under them across the whole form. In Odoo it sits at the
        # right end of the same row; here it is the one thing in the header
        # worth the full width -- asked for on 2026-09-13 -- and a row of
        # chevrons squeezed next to three buttons reads as nothing at all.
        headerLayout = QtWidgets.QVBoxLayout()
        # No margin of its own, and set by hand: setLayoutMarginAndSpacing reads
        # a 0 as "no value given" and puts the default 6 back. Six above and six
        # below, twice over for the two layouts, is a band of empty space
        # between a title and the statusbar it belongs to -- and the band is
        # there even when the row holds nothing, which is every state whose
        # buttons the modifiers have hidden.
        headerLayout.setContentsMargins(0, 0, 0, 0)
        headerLayout.setSpacing(2)
        buttonsRow = QtWidgets.QHBoxLayout()
        buttonsRow.setContentsMargins(0, 0, 0, 0)
        buttonsRow.setSpacing(4)
        headerLayout.addLayout(buttonsRow)
        statusBars = []
        for xmlObj in archHeader:
            if xmlObj.tag == 'button':
                buttonObj = button.Button(qtParent=self,
                                          xmlObject=xmlObj,
                                          model=self.model,
                                          odooConnector=self.odooConnector)
                buttonsRow.addWidget(buttonObj)
                commonAppend('button_' + str(buttonObj.buttonString).replace(' ', '_'), buttonObj)
            elif xmlObj.tag == 'field':
                fieldObj = self.computeField(xmlObj)
                fieldQt = fieldObj
                fieldName = fieldObj.fieldName
                if not fieldQt:
                    utils.logMessage('warning', 'Qt field %r could not be loaded' % (fieldName), 'computeHeader')
                    continue
                if getattr(fieldObj, 'widget', '') == 'statusbar':
                    statusBars.append(fieldQt)
                elif isinstance(fieldQt, QtWidgets.QLayout):
                    buttonsRow.addLayout(fieldQt)
                elif isinstance(fieldQt, QtWidgets.QWidget):
                    buttonsRow.addWidget(fieldQt)
                else:
                    utils.logMessage('warning', 'Field %r could not be added to layout' % (fieldName), 'computeHeader')
                    continue
                commonAppend('field_' + str(fieldName), fieldObj)
            else:
                pass
        # The buttons stay where they were put, on the left, whatever room the
        # row is given.
        buttonsRow.addStretch(1)
        for statusBar in statusBars:
            headerLayout.addWidget(statusBar)
        return mapping, headerLayout

    def computeField(self, xmlObj, isChatterWidget=False):
        fieldAttributes = xmlObj.attrib
        fieldName = fieldAttributes.get('name', '')
        fieldDefinition = self.fieldsNameTypeRel.get(fieldName, {})
        fieldType = fieldDefinition.get('type', False)
        fieldObj = None
        if fieldType == 'selection':
            fieldObj = Selection(self, xmlObj, self.fieldsNameTypeRel, self.odooConnector, isChatterWidget)
        elif fieldType == 'char':
            fieldObj = Charachter(self, xmlObj, self.fieldsNameTypeRel, self.odooConnector, isChatterWidget)
        elif fieldType == 'integer':
            fieldObj = Integer(self, xmlObj, self.fieldsNameTypeRel, self.odooConnector, isChatterWidget)
        elif fieldType == 'float':
            fieldObj = Float(self, xmlObj, self.fieldsNameTypeRel, self.odooConnector, isChatterWidget)
        elif fieldType == 'datetime':
            fieldObj = Datetime(self, xmlObj, self.fieldsNameTypeRel, self.odooConnector, isChatterWidget)
        elif fieldType == 'many2one':
            fieldObj = Many2one(qtParent=self,
                                xmlField=xmlObj,
                                fieldsDefinition=self.fieldsNameTypeRel,
                                odooConnector=self.odooConnector,
                                isChatterWidget=isChatterWidget)
        elif fieldType == 'many2many':
            fieldObj = Many2many(qtParent=self,
                                 xmlField=xmlObj,
                                 fieldsDefinition=self.fieldsNameTypeRel,
                                 odooConnector=self.odooConnector,
                                 isChatterWidget=isChatterWidget)
        elif fieldType == 'text':
            fieldObj = Text(self, xmlObj, self.fieldsNameTypeRel, self.odooConnector, isChatterWidget)
        elif fieldType == 'date':
            fieldObj = Date(self, xmlObj, self.fieldsNameTypeRel, self.odooConnector, isChatterWidget)
        elif fieldType == 'boolean':
            fieldObj = Boolean(self, xmlObj, self.fieldsNameTypeRel, self.odooConnector, isChatterWidget)
        elif fieldType == 'one2many':
            fieldObj = One2many(qtParent=self,
                                xmlField=xmlObj,
                                fieldsDefinition=self.fieldsNameTypeRel,
                                odooConnector=self.odooConnector,
                                isChatterWidget=isChatterWidget)
        elif fieldType == 'binary':
            fieldObj = Binary(self, xmlObj, self.fieldsNameTypeRel, self.odooConnector, isChatterWidget)
        else:
            utils.logMessage('warning', 'Field %r not supported' % (fieldType), 'computeField')
        return fieldObj

    def computeNooteBookPage(self, tabObject, pageIndex=False):
#         tabObject.nootebook_changed_signal.emit(pageIndex)
#         return
        values = tabObject.get(pageIndex, {})
        if values:
            del tabObject[pageIndex]
            self.nootebook_changed_signal.emit(pageIndex)

    def computeChatter(self, divVlay, childElement):
        self.chatterLay = QtWidgets.QVBoxLayout()
        self.chatterButton = QtWidgets.QPushButton('↓↓↓   Show Chatter   ↓↓↓')
        self.chatterButton.setStyleSheet(constants.BUTTON_STYLE + constants.VIOLET_BACKGROUND)
        self.chatterButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.chatterButton.clicked.connect(self.showChatter)
        self.chatterWidgets = []
        count = 0
        for fieldObj in childElement:
            if fieldObj.tag == 'field':
                qtWidgetField = self.computeField(fieldObj, isChatterWidget=True)
                if qtWidgetField:
                    if isinstance(qtWidgetField, QtWidgets.QLayout):
                        self.chatterLay.insertLayout(0, qtWidgetField)
                        if count == 0:
                            self.chatterLay.insertSpacerItem(0, QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum))
                            count = count + 1
                    elif isinstance(qtWidgetField, QtWidgets.QWidget):
                        self.chatterLay.insertWidget(0, qtWidgetField)
                        qtWidgetField.hide()
                        self.chatterWidgets.append(qtWidgetField)
                    self.appendToglobalMapping('field_' + qtWidgetField.fieldName, qtWidgetField)
            else:
                utils.logMessage('warning', 'Unable to compute tag in chatter %r' % (fieldObj.tag), 'computeChatter')
        self.chatterLay.insertWidget(0, self.chatterButton)
        utilsUi.setLayoutMarginAndSpacing(self.chatterLay, constants.LAY_OUT_SPACING + 20)
        self.chatterLay.setSpacing(constants.LAY_OUT_SPACING)
        divVlay.addLayout(self.chatterLay)

    def showChatter(self):
        for chatterWidget in self.chatterWidgets:
            chatterWidget.showChatterWidget()
        self.chatterButton.hide()

    def updateDataStructure(self, pageIndex=0):
        utils.logDebug('compute Notebook fields: %r' % (pageIndex), 'updateDataStructure')
        if pageIndex > 0 and pageIndex in self.nootebookFieldsToCompute:
            dictFieldsToUpdate = self.nootebookFieldsToCompute[pageIndex]
            fieldNamesToUpdate = list(dictFieldsToUpdate.keys())
            self.loadIds(self.activeIds, {}, {}, {}, fieldNamesToUpdate, True)

    def setDefaults(self, fieldsToRead=[]):
        if not fieldsToRead:
            fieldsToRead = list(self.interfaceFieldsDict.keys())
        if fieldsToRead:
            self.fieldDefaultVals = self.odooConnector.rpc_connector.defaultGet(self.model, fieldsToRead)
            self.skipOnChange = True
            if self.fieldDefaultVals:
                for fieldName, fieldVal in list(self.fieldDefaultVals.items()):
                    self.setValueField(fieldName, fieldVal)
                    self._valueChanged(fieldName)
        else:
            logging.warning("unable to load default field from model %s " % self.model)
        self.skipOnChange = False

    def removeNootebookFields(self, fieldsToRead):
        mainDict = {}
        for fieldsDict in list(self.nootebookFieldsToCompute.values()):
            mainDict.update(fieldsDict)
        for fieldName in list(mainDict.keys()):
            if fieldName in fieldsToRead:
                fieldsToRead.remove(fieldName)
        return fieldsToRead

    @utils.timeit
    def loadIds(self,
                objIds=[],
                forceFieldValues={},
                readonlyFields={},
                invisibleFields={},
                fieldsToRead=[],
                skipRemoveNootebook=False):
        """
        refresh the user interface with the given odooid
        """
        if objIds is None or not objIds:
            objIds = []
        if isinstance(objIds, int):
            objIds = [objIds]
        self.activeIds = objIds
        if not fieldsToRead:
            fieldsToRead = list(self.interfaceFieldsDict.keys())
        if not skipRemoveNootebook:
            fieldsToRead = self.removeNootebookFields(fieldsToRead)
        if len(objIds) > 1:
            utilsUi.popWarning(None, 'You cannot load multiple ids on form or search view!')
            return False
        fromId = False
        if objIds:
            fromId = objIds[0]
            formVals = self.odooConnector.rpc_connector.read(self.model, fieldsToRead, [fromId], {'lang': self.odooConnector.activeLanguage})
            if not formVals:
                utils.logMessage('warning', 'No values found for id %r and model %r' % (fromId, self.model), 'loadIds')
                fromId = False
                self.skipOnChange = True
                self.setDefaults()
                self.skipOnChange = False
            else:
                self.skipOnChange = True
                self.formVals = formVals[0]
                for fieldName, fieldVal in list(self.formVals.items()):
                    self.setValueField(fieldName, fieldVal)
                    self.setFieldParentAttrs(fieldName)
                for button in self.buttons.__dict__.values():
                    button.odooId=fromId
                self.skipOnChange = False
        else:
            self.setDefaults(fieldsToRead)
        
        for fieldName, fieldVal in list(forceFieldValues.items()):
            self.setValueField(fieldName, fieldVal, )

        # The modifiers of the record just loaded, before what the caller
        # forces below, so that what the caller forces wins.
        self._setFieldModifiers()

        for readonlyField, fieldAttr in list(readonlyFields.items()):
            self.setReadonlyField(readonlyField, fieldAttr)
        
        for invisibleField, fieldAttr in list(invisibleFields.items()):
            self.setInvisibleField(invisibleField, fieldAttr)
        
        self._setButtonsModifiers()
        self.objectsInit = copy.copy(self.fields)
        self.form_changed.emit("Reloaded")

    def setFieldParentAttrs(self, fieldName):
        fieldObj = self.interfaceFieldsDict.get(fieldName, None)
        if not fieldObj:
            utils.logMessage('warning', 'Field %r not found in the local fields' % (fieldName), 'setValueField')
        else:
            fieldObj.setParentAttrs(self.activeIds, self.model)

    def _setFieldModifiers(self):
        fieldDict = self.interfaceFieldsDict
        # What the record holds, for the expressions Odoo 17 and later send in
        # place of the modifiers -- see utils.widgetModifier.
        values = utils.recordValues(fieldDict, getattr(self, 'formVals', {}))
        for fieldObj in list(fieldDict.values()):
            client_context = dict(self.odooConnector.rpc_connector.contextUser)
            client_context.update(utils.evaluateContext(fieldObj.context, fieldDict))
            val = utils.widgetModifier(fieldObj, 'readonly', fieldDict,
                                       values, client_context)
            if val is None:
                fieldObj.setReadonly(fieldObj.readonly)
            else:
                fieldObj.setReadonly(val)
                self.commonEval(val, self.readonlyFields, fieldObj)
            val = utils.widgetModifier(fieldObj, 'invisible', fieldDict,
                                       values, client_context)
            if val is None:
                fieldObj.setInvisible(fieldObj.invisible)
            else:
                fieldObj.setInvisible(val)
                self.commonEval(val, self.invisibleFields, fieldObj)
            # Required is a modifier like the other two from 17 onwards, and
            # this is the list the save dialog reads before letting a save go.
            val = utils.widgetModifier(fieldObj, 'required', fieldDict,
                                       values, client_context)
            if val is not None:
                fieldObj.required = val
            if fieldObj.required:
                self.requiredFields[fieldObj.fieldName] = fieldObj
            elif fieldObj.fieldName in self.requiredFields:
                del self.requiredFields[fieldObj.fieldName]
        self._setContainerModifiers(values, dict(self.odooConnector.rpc_connector.contextUser))

    def checkRequiredFieldsEvaluated(self, showMessage=False):
        fieldsToEvaluate = []
        message = 'These required fields needs to be evaluated:'
        for fieldObject in list(self.requiredFields.values()):
            if not fieldObject.value and not isinstance(fieldObject.value, (int, float)):
                fieldsToEvaluate.append(fieldObject.fieldStringInterface)
                message = message + '\n %r' % (fieldObject.fieldStringInterface)
        if showMessage and fieldsToEvaluate:
            utilsUi.popWarning(None, message)
        return fieldsToEvaluate

    def setInvisibleField(self, fieldName, val=False):
        fieldObj = self.interfaceFieldsDict.get(fieldName, None)
        if not fieldObj:
            utils.logMessage('warning', f'Field {fieldName} not found in the local fields', 'setInvisibleField')
            return
        fieldObj.setInvisible(val)
        self.commonEval(val, self.invisibleFields, fieldObj)
    
    def setReadonlyField(self, fieldName, val=False):
        fieldObj = self.interfaceFieldsDict.get(fieldName, None)
        if not fieldObj:
            utils.logMessage('warning', 'Field %r not found in the local fields' % (fieldName), 'setReadonlyField')
            return
        fieldObj.setReadonly(val)
        self.commonEval(val, self.readonlyFields, fieldObj)

    def commonEval(self, val, localDict, fieldObj):
        if val:
            localDict[fieldObj.fieldName] = fieldObj
        else:
            if fieldObj.fieldName in list(localDict.keys()):
                del localDict[fieldObj.fieldName]

    def getAllOnChange(self):
        outDict = {}
        for fieldName, fieldObject in list(self.interfaceFieldsDict.items()):
            outDict[fieldName] = fieldObject.on_change
        return outDict
    
    def _on_change(self, fieldName):
        '''
            [
            [id],
            {all values},
            launcher field name,
            {All form on_changes},
            {context},
            ]
        '''
        if self.skipOnChange:
            return {}
        rpc = self.odooConnector.rpc_connector
        if rpc.serverVersion >= 17:
            values, fieldsSpec = self._onchangeValuesAndSpec()
            result = rpc.onchange(self.model, self.activeIds, values, [fieldName], fieldsSpec)
            result = dict(result) if isinstance(result, dict) else {}
            result['value'] = {name: utils.onchangeValueToWidget(value)
                               for name, value in (result.get('value') or {}).items()}
            return result
        allVals = self.getAllFieldsValues()
        allOnchanges = self.getAllOnChange()
        return rpc.on_change(self.model, self.activeIds, allVals, fieldName, allOnchanges, {})

    def _onchangeValuesAndSpec(self):
        """What the onchange of Odoo 17 and later is sent: values and spec.

        One2many, many2many and binary fields are left out of both. What is not
        sent the server takes from the record as it is stored, which is what
        these widgets hold until the form is saved; and they are not asked back,
        since an x2many answers in commands these widgets do not read.
        """
        values = {}
        fieldsSpec = {}
        for name, fieldObj in list(self.interfaceFieldsDict.items()):
            fieldName = name[7:] if name.startswith('header_') else name
            fieldType = self.fieldsNameTypeRel.get(fieldName, {}).get('type') \
                or getattr(fieldObj, 'fieldType', '')
            if fieldType in ('one2many', 'many2many', 'binary'):
                continue
            try:
                value = utils.widgetValueToOnchange(fieldObj.value, fieldType)
            except ValueError:
                continue
            values[fieldName] = value
            if fieldType == 'many2one':
                fieldsSpec[fieldName] = {'fields': {'display_name': {}}}
            else:
                fieldsSpec[fieldName] = {}
        return values, fieldsSpec

    def addToObject(self):
        fieldIdentifier = 'field_'
        buttonIdentifier = 'button_'
        for key, obj in list(self.mappingInterface.items()):
            if key.startswith(fieldIdentifier):
                newKey = key.replace(fieldIdentifier, '')
                self.interfaceFieldsDict[newKey] = obj
                obj.value_changed_signal.connect(self._valueChanged)
                obj.translation_clicked.connect(self.translationDial)
            elif key.startswith(buttonIdentifier):
                newKey = key.replace(buttonIdentifier, '')
                self.buttons.__dict__[newKey] = obj
        return True

    def _valueChangedExt(self, fieldName):
        '''
            To allow external oveload
        '''
        pass

    def _valueChanged(self, fieldName):
        fieldName = str(fieldName)
        fieldObj = self.interfaceFieldsDict.get(fieldName)
        if not fieldObj:
            utils.logMessage('warning', 'Field %r not found in interfacefieldsdict' % (fieldName), '_valueChanged')
            return
        changeResult = self._on_change(fieldObj.fieldName)
        changedValues = changeResult.get('value', {})
        # The server answers with everything the change leads to, cascade
        # included: setting those values must not send one onchange per field.
        skipOnChange, self.skipOnChange = self.skipOnChange, True
        try:
            for fieldNameFromServer, fieldValueFromServer in list(changedValues.items()):
                fieldObj1 = self.interfaceFieldsDict.get(str(fieldNameFromServer))
                if fieldObj1 is None:
                    continue
                fieldObj1.setValue(fieldValueFromServer)
                if self._isSavable(fieldObj1):
                    self.fieldsChanged[fieldObj1.fieldName] = fieldObj1
        finally:
            self.skipOnChange = skipOnChange
        # skipOnChange is up while the form writes values itself -- a record
        # being loaded, the defaults, an onchange answer. Those are not changes
        # to save: marked, a record just opened wrote back twenty fields, the
        # server's readonly ones among them.
        if not skipOnChange and self._isSavable(fieldObj):
            self.fieldsChanged[fieldName] = fieldObj
        self._setFieldModifiers()
        self._valueChangedExt(fieldName)

    def _isSavable(self, fieldObj):
        """Whether a change to the field is one to write, as the web client sees it.

        Not a field the server defines readonly, nor one a modifier makes
        readonly on this record -- unless the view says force_save.
        """
        if str(getattr(fieldObj, 'fieldXmlAttributes', {}).get('force_save', '')).lower() in ('1', 'true'):
            return True
        attributes = getattr(fieldObj, 'fieldXmlAttributes', {})
        viewDecides = (getattr(fieldObj, 'modifiers', {}) or {}).get('readonly') \
            or 'readonly' in attributes
        definition = self.fieldsNameTypeRel.get(fieldObj.fieldName, {})
        if definition.get('readonly') is True and not viewDecides:
            # A view that says readonly for the field -- `states` up to 16, an
            # expression from 17 -- has the last word, and readonlyFields holds
            # what it said for this record.
            return False
        return fieldObj.fieldName not in self.readonlyFields

    def translationDial(self, fieldName):
        if not self.activeIds:
            utilsUi.popWarning(None, 'Translations are available only on already created records.')
            return
        fieldName = str(fieldName)
        fieldObj = self.interfaceFieldsDict.get(fieldName)

        def acceptTransDial():
            translationDial.accept()

        def rejectTransDial():
            translationDial.reject()

        translationDial = QtWidgets.QDialog()
        mainLay = QtWidgets.QVBoxLayout()
        tableWidget = QtWidgets.QTableWidget()
        model = self.model
        if model == 'product.product':
            model = 'product.template'
        translationName = str(model + ',' + fieldName)
        filterList = [('res_id', '=', self.activeIds[0]),
                      ('name', '=', translationName)
                      ]
        headers = ['Source value', 'Translated Value', 'Language', 'Name']
        fieldNames = ['source', 'translated', 'lang', 'name']
        values = []
        translationObj = 'ir.translation'
        res = self.odooConnector.rpc_connector.readSearch(translationObj, ['src', 'value', 'lang'], filterList)
        if not res:
            res = []
            installedLangs = self.odooConnector.rpc_connector.readSearch('res.lang', ['code', 'name'], [('active', '=', True)])
            for resDict in installedLangs:
                code = resDict.get('code', '')
                createDict = {
                    'type': 'model',
                    'value': fieldObj.value,
                    'state': 'translated',
                    'module': '',
                    'res_id': self.activeIds[0],
                    'name': translationName,
                    'src': fieldObj.value,
                    'lang': code,
                }
                transId = self.odooConnector.rpc_connector.create(translationObj, createDict)
                createDict['id'] = transId
                res.append(createDict)
        for elemDict in res:
            src = elemDict.get('src', '')
            value = elemDict.get('value', '')
            lang = elemDict.get('lang', '')
            values.append([src, value, lang, translationName])
        tableFlags = {1: QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable,
                      }
        utilsUi.commonPopulateTable(headers, values, tableWidget, tableFlags)
        mainLay.addWidget(tableWidget)
        layButtons, okButt, cancelButt = utilsUi.getButtonBox()
        okButt.clicked.connect(acceptTransDial)
        cancelButt.clicked.connect(rejectTransDial)
        mainLay.addLayout(layButtons)
        translationDial.setLayout(mainLay)
        translationDial.resize(800, 400)
        tableWidget.resizeColumnsToContents()
        tableWidget.horizontalHeader().setStretchLastSection(True)
        if translationDial.exec() == QtWidgets.QDialog.Accepted:
            rowsDict = utils.getRowsFromTableWidget(tableWidget, 'dict', fieldNames)
            for rowDict in list(rowsDict.values()):
                elemId = False
                translated = str(rowDict.get('translated', ''))
                source = str(rowDict.get('source', ''))
                lang = str(rowDict.get('lang', ''))
                for elem in res:
                    sourceRel = elem.get('src', '')
                    langRel = elem.get('lang', '')
                    if source == sourceRel and lang == langRel:
                        elemId = elem.get('id', False)
                        break
                if elemId:
                    self.odooConnector.rpc_connector.write(translationObj, {'value': translated}, [elemId])
                    if lang == self.activeLanguageCode:
                        self.setValueField(fieldName, translated)

    def appendToglobalMapping(self, key, value):
        self.globalMapping.update({key: value})

    def save(self):
        """
        save the current values
        """
        to_write = {}
        if self.activeIds:
            for k, v in self.fieldsChanged.items():
                fieldObj1 = self.interfaceFieldsDict.get(k)
                if fieldObj1.fieldType in ['one2many','many2many']:
                    to_write[k] = [(6, False, v.value)]
                else:
                    to_write[k] = v.value
            self.odooConnector.rpc_connector.write(self.model, to_write,  self.activeIds)
        else:
            for k, v in self.getAllFieldsValues().items():
                fieldObj1 = self.interfaceFieldsDict.get(k)
                if fieldObj1.fieldType in ['one2many','many2many']:
                    to_write[k] = [(6, False, v)]
                else:
                    to_write[k] = v
            self.activeIds = self.odooConnector.rpc_connector.create(self.model, to_write)
        return self.activeIds
