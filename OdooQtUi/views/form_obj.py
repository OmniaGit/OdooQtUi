'''
Created on 24 Mar 2017

@author: dsmerghetto
'''
import copy
import json
import xml.etree.cElementTree as ElementTree
from functools import partial
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

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


class QtFormView(TemplateView):
    nootebook_changed_signal = QtCore.Signal(int)

    def __init__(self, rpcObject, viewObj, activeLanguageCode='en_US', odooConnector=None):
        self.globalMapping = {}
        self.aloneLabels = {}
        self.notebookTabsNotComputed = {}
        self.nootebookFieldsToCompute = {}  # {nootebookIndex: {'fieldName': fieldObj}}
        self.requiredFields = {}
        self.readonlyFields = {}
        self.invisibleFields = {}
        self.fieldDefaultVals = {}  # {'fieldName' : fieldval}
        self.skipOnChange = False
        self.readonly = False
        self.activeIds = []         # must be one
        super(QtFormView, self).__init__(rpcObject, viewObj, activeLanguageCode)
        self.odooConnector = odooConnector
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
            vertical_layout.setMargin(0)
            self.computeRecursion(qvboxLayout=vertical_layout,
                                  xmlParent=ElementTree.XML(self.arch.encode('utf-8')))
            verticalSpacer = QtWidgets.QSpacerItem(40, 100, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            vertical_layout.addItem(verticalSpacer)
            self.setLayout(vertical_layout)
        else:
            utils.logWarning('No arch set impossible to compute structure')

    def computeRecursion(self, qvboxLayout=False, xmlParent=None, nootebookIndex=0):
        # TODO:    div name <div name="button_box" class="oe_button_box">
        if not qvboxLayout:
            qvboxLayout = QtWidgets.QVBoxLayout()
            qvboxLayout.setSpacing(0)
            qvboxLayout.setMargin(0)
        if constants.DEBUG:
            line = QtWidgets.QFrame(self)
            line.setFrameShape(QtWidgets.QFrame.HLine)
            line.setFrameShadow(QtWidgets.QFrame.Sunken)
            line.setLineWidth(100)
            line.setStyleSheet("color: blue;")
            qvboxLayout.addWidget(line)
        for childXlmElement in xmlParent.getchildren():
            childXmlTag = childXlmElement.tag
            if childXmlTag == 'sheet':
                self.computeRecursion(qvboxLayout=qvboxLayout,
                                      xmlParent=childXlmElement)
            elif childXmlTag == 'header':
                utils.logWarning('Header not implemented', 'computeRecursion')
                continue
#                 mapping, layout = self.computeHeader(xmlParent=childXlmElement, nootebookIndex=self.useHeader)
#                 if layout:
#                     if self.useHeader:
#                         qvboxLayout.addLayout(layout)
#                     else:
#                         layout.deleteLater()
#                 if mapping:
#                     self.globalMapping.update(mapping)
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
                    self.computeRecursion(qvboxLayout=qvboxLayout,
                                          xmlParent=childXlmElement)
                elif childXlmElement.text and len(childXlmElement.text.strip()) > 0:
                    label = QtWidgets.QLabel(childXlmElement.text)
                    label.setStyleSheet(constants.LABEL_SEPARATOR)
                    qvboxLayout.addWidget(label)
                    self.computeRecursion(qvboxLayout=qvboxLayout,
                                          xmlParent=childXlmElement)
                else:
                    self.computeRecursion(qvboxLayout=qvboxLayout,
                                          xmlParent=childXlmElement)
            elif childXmlTag == 'notebook':
                tabWidget = QtWidgets.QTabWidget(self)
                tabWidget.setStyleSheet(constants.NOOTEBOOK_STYLE)
                tabWidgetBar = tabWidget.tabBar()
                tabWidgetBar.setStyleSheet(constants.NOOTEBOOK_TABBAR_STYLE)
                nootebookIndex = 0
                for page in childXlmElement.getchildren():
                    pageString = page.attrib.get('string', '')
                    invisible = page.attrib.get('invisible', False)
                    modifInvisible, modifReadonly = utils.evaluateModifiers(page.attrib.get('modifiers', {}))
                    if invisible or modifInvisible:
                        continue
                    pageWidget = QtWidgets.QWidget(tabWidget)
                    pageVboxLayout = QtWidgets.QVBoxLayout()
                    pageVboxLayout.setSpacing(0)
                    pageVboxLayout.setMargin(0)
                    if modifReadonly:
                        pageWidget.setDisabled(True)
                    if nootebookIndex != 0:
                        self.notebookTabsNotComputed[nootebookIndex] = {'xmlPage': page, 'pageWidget': pageWidget}
                    self.computeRecursion(qvboxLayout=pageVboxLayout,
                                          xmlParent=page,
                                          nootebookIndex=nootebookIndex)
                    pageWidget.setLayout(pageVboxLayout)
                    tabWidget.addTab(pageWidget, pageString)
                    nootebookIndex = nootebookIndex + 1
                qvboxLayout.addWidget(tabWidget)
                tabWidget.currentChanged.connect(partial(self.computeNooteBookPage, tabWidget))
            elif childXmlTag == 'group':
                self.computeRecursion(qvboxLayout=qvboxLayout,
                                      xmlParent=childXlmElement)
            elif childXmlTag == 'button':
                utils.logWarning('Buttons not implemented at first level of form')
                continue
#                 buttonObj = button.Button(childXlmElement)
#                 key = 'button_' + str(buttonObj.buttonString).replace(' ', '_')
#                 self.appendToglobalMapping(key, buttonObj)
#                 qvboxLayout.addWidget(buttonObj)
#                 divClass = parent.attrib.get('class', '')
#                 if divClass == 'oe_button_box':
#                     buttonObj.setHidden(True)
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
                    qvboxLayout.addWidget(fieldQHLayout)
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
        if constants.DEBUG:
            line = QtWidgets.QFrame(self)
            line.setFrameShape(QtWidgets.QFrame.HLine)
            line.setFrameShadow(QtWidgets.QFrame.Sunken)
            line.setLineWidth(300)
            line.setStyleSheet("color: blue;")
            qvboxLayout.addWidget(line)
        return qvboxLayout

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
                headerLayout.addWidget(buttonObj)
                commonAppend('button_header_' + str(buttonObj.buttonString).replace(' ', '_'), buttonObj)
            elif xmlObj.tag == 'field':
                fieldObj = self.computeField(xmlObj)
                fieldQt = fieldObj
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

    def computeField(self, xmlObj):
        fieldAttributes = xmlObj.attrib
        fieldName = fieldAttributes.get('name', '')
        fieldDefinition = self.fieldsNameTypeRel.get(fieldName, {})
        fieldType = fieldDefinition.get('type', False)
        fieldObj = None
        if fieldType == 'selection':
            fieldObj = Selection(self, xmlObj, self.fieldsNameTypeRel, self.rpcObject)
        elif fieldType == 'char':
            fieldObj = Charachter(self, xmlObj, self.fieldsNameTypeRel, self.rpcObject)
        elif fieldType == 'integer':
            fieldObj = Integer(self, xmlObj, self.fieldsNameTypeRel, self.rpcObject)
        elif fieldType == 'float':
            fieldObj = Float(self, xmlObj, self.fieldsNameTypeRel, self.rpcObject)
        elif fieldType == 'datetime':
            fieldObj = Datetime(self, xmlObj, self.fieldsNameTypeRel, self.rpcObject)
        elif fieldType == 'many2one':
            fieldObj = Many2one(self, xmlObj, self.fieldsNameTypeRel, self.rpcObject, self.odooConnector)
        elif fieldType == 'many2many':
            fieldObj = Many2many(self, xmlObj, self.fieldsNameTypeRel, self.rpcObject, self.odooConnector)
        elif fieldType == 'text':
            fieldObj = Text(self, xmlObj, self.fieldsNameTypeRel, self.rpcObject)
        elif fieldType == 'date':
            fieldObj = Date(self, xmlObj, self.fieldsNameTypeRel, self.rpcObject)
        elif fieldType == 'boolean':
            fieldObj = Boolean(self, xmlObj, self.fieldsNameTypeRel, self.rpcObject)
        elif fieldType == 'one2many':
            fieldObj = One2many(self, xmlObj, self.fieldsNameTypeRel, self.rpcObject, self.odooConnector)
        elif fieldType == 'binary':
            fieldObj = Binary(self, xmlObj, self.fieldsNameTypeRel, self.rpcObject)
        else:
            utils.logMessage('warning', 'Field %r not supported' % (fieldType), 'computeField')
        return fieldObj

    def computeNooteBookPage(self, tabObject, pageIndex=False):
        tabObject.nootebook_changed_signal.emit(pageIndex)
        return
        values = tabObject.get(pageIndex, {})
        if values:
            del tabObject[pageIndex]
            self.nootebook_changed_signal.emit(pageIndex)

    def computeChatter(self, divVlay, childElement):
        hlay = QtWidgets.QHBoxLayout()
        count = 0
        for fieldObj in childElement.getchildren():
            if fieldObj.tag == 'field':
                qtWidgetField = self.computeField(fieldObj)
                if qtWidgetField:
                    if isinstance(qtWidgetField, QtWidgets.QLayout):
                        hlay.insertLayout(0, qtWidgetField)
                        if count == 0:
                            hlay.insertSpacerItem(0, QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum))
                            count = count + 1
                    elif isinstance(qtWidgetField, QtWidgets.QWidget):
                        hlay.insertWidget(0, qtWidgetField)
                    self.appendToglobalMapping('field_' + qtWidgetField.fieldName, qtWidgetField)
            else:
                utils.logMessage('warning', 'Unable to compute tag in chatter %r' % (fieldObj.tag), 'computeChatter')
        divVlay.addLayout(hlay)

    def updateDataStructure(self, pageIndex=0):
        utils.logDebug('compute Notebook fields: %r' % (pageIndex), 'updateDataStructure')
        if pageIndex > 0 and pageIndex in self.nootebookFieldsToCompute:
            dictFieldsToUpdate = self.nootebookFieldsToCompute[pageIndex]
            fieldNamesToUpdate = list(dictFieldsToUpdate.keys())
            self.loadIds(self.activeIds, {}, {}, {}, fieldNamesToUpdate, True)

    def setDefaults(self, fieldsToRead=[]):
        if not fieldsToRead:
            fieldsToRead = list(self.interfaceFieldsDict.keys())
        self.fieldDefaultVals = self.rpcObject.defaultGet(self.model, fieldsToRead)
        self.skipOnChange = True
        for fieldName, fieldVal in list(self.fieldDefaultVals.items()):
            self.setValueField(fieldName, fieldVal)
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
    def loadIds(self, objIds=[], forceFieldValues={}, readonlyFields={}, invisibleFields={}, fieldsToRead=[], skipRemoveNootebook=False):
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
            utilsUi.launchMessage('You cannot load multiple ids on form or search view!', 'warning')
            return False
        formId = False
        if objIds:
            formId = objIds[0]
            formVals = self.rpcObject.read(self.model, fieldsToRead, [formId], {'lang': self.activeLanguageCode})
            if not formVals:
                utils.logMessage('warning', 'No values found for id %r and model %r' % (formId, self.model), 'loadIds')
                formId = False
                self.skipOnChange = True
                self.setDefaults()
                self.skipOnChange = False
            else:
                self.skipOnChange = True
                self.formVals = formVals[0]
                for fieldName, fieldVal in list(self.formVals.items()):
                    self.setValueField(fieldName, fieldVal)
                    self.setFieldParentAttrs(fieldName)
                self.skipOnChange = False
        else:
            self.setDefaults(fieldsToRead)
        for fieldName, fieldVal in list(forceFieldValues.items()):
            self.setValueField(fieldName, fieldVal)
        self._setFieldModifiers()
        for readonlyField, fieldAttr in list(readonlyFields.items()):
            self.setReadonlyField(readonlyField, fieldAttr)
        for invisibleField, fieldAttr in list(invisibleFields.items()):
            self.setInvisibleField(invisibleField, fieldAttr)
        self._setButtonsModifiers()
        self.objectsInit = copy.copy(self.fields)

    def setFieldParentAttrs(self, fieldName):
        fieldObj = self.interfaceFieldsDict.get(fieldName, None)
        if not fieldObj:
            utils.logMessage('warning', 'Field %r not found in the local fields' % (fieldName), 'setValueField')
        else:
            fieldObj.setParentAttrs(self.activeIds, self.model)

    def _setFieldModifiers(self):
        fieldDict = self.interfaceFieldsDict
        for fieldObj in list(fieldDict.values()):
            readonlyModif = fieldObj.modifiers.get('readonly', {})
            invisibleModif = fieldObj.modifiers.get('invisible', {})
            if readonlyModif:
                val = utils.evaluateAttrs(fieldDict, readonlyModif)
                fieldObj.setReadonly(val)
                self.commonEval(val, self.readonlyFields, fieldObj)
            else:
                fieldObj.setReadonly(fieldObj.readonly)
            if invisibleModif:
                val = utils.evaluateAttrs(fieldDict, invisibleModif)
                fieldObj.setInvisible(val)
                self.commonEval(val, self.invisibleFields, fieldObj)
            else:
                fieldObj.setInvisible(fieldObj.invisible)
            if fieldObj.required:
                self.requiredFields[fieldObj.fieldName] = fieldObj

    def checkRequiredFieldsEvaluated(self, showMessage=False):
        fieldsToEvaluate = []
        message = 'These required fields needs to be evaluated:'
        for fieldObject in list(self.requiredFields.values()):
            if not fieldObject.value and not isinstance(fieldObject.value, (int, float)):
                fieldsToEvaluate.append(fieldObject.fieldStringInterface)
                message = message + '\n %r' % (fieldObject.fieldStringInterface)
        if showMessage and fieldsToEvaluate:
            utilsUi.launchMessage(message, 'warning')
        return fieldsToEvaluate

    def setInvisibleField(self, fieldName, val=False):
        fieldObj = self.interfaceFieldsDict.get(fieldName, None)
        if not fieldObj:
            utils.logMessage('warning', 'Field %r not found in the local fields' % (fieldName), 'setInvisibleField')
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
        allVals = self.getAllFieldsValues()
        allOnchanges = self.getAllOnChange()
        return self.rpcObject.on_change(self.model, self.activeIds, allVals, fieldName, allOnchanges, {})

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

    def _valueChanged(self, fieldName):
        fieldName = str(fieldName)
        fieldObj = self.interfaceFieldsDict.get(fieldName)
        if not fieldObj:
            utils.logMessage('warning', 'Field %r not found in interfacefieldsdict' % (fieldName), '_valueChanged')
        changeResult = self._on_change(fieldObj.fieldName)
        changedValues = changeResult.get('value', {})
        for fieldNameFromServer, fieldValueFromServer in list(changedValues.items()):
            fieldObj1 = self.interfaceFieldsDict.get(str(fieldNameFromServer))
            fieldObj1.setValue(fieldValueFromServer)
        self.fieldsChanged[fieldName] = fieldObj
        self._setFieldModifiers()

    def translationDial(self, fieldName):
        if not self.activeIds:
            utilsUi.launchMessage('Translations are available only on already created records.', 'warning')
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
        res = self.rpcObject.readSearch(translationObj, ['src', 'value', 'lang'], filterList)
        if not res:
            res = []
            installedLangs = self.rpcObject.readSearch('res.lang', ['code', 'name'], [('active', '=', True)])
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
                transId = self.rpcObject.create(translationObj, createDict)
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
        if translationDial.exec_() == QtWidgets.QDialog.Accepted:
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
                    self.rpcObject.write(translationObj, {'value': translated}, [elemId])
                    if lang == self.activeLanguageCode:
                        self.setValueField(fieldName, translated)

    def appendToglobalMapping(self, key, value):
        self.globalMapping.update({key: value})
