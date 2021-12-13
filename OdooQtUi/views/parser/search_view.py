'''
Created on 3 Feb 2017

@author: Daniel Smerghetto
'''
import copy
import logging
#
# Do not delete these, are necessary to compute filters coming from server
#

import datetime
from dateutil.relativedelta import relativedelta

import xml.etree.cElementTree as ElementTree
from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets
from functools import partial
from OdooQtUi.utils_odoo_conn import constants
from OdooQtUi.utils_odoo_conn import utils
from OdooQtUi.utils_odoo_conn import utilsUi

SEARCH_FOR_STRING = 'Search "%s" for: "'

class SearchView(object):

    def __init__(self, arch='', fieldsNameTypeRel={}, parent=False, searchMode='ilike', advancedFilterFields={}):
        super(SearchView, self).__init__()
        self.searchMode = searchMode
        self.arch = arch
        self.parent = parent
        self.timers = []    # timers to add filters in delayed mode
        self.fieldsNameTypeRel = fieldsNameTypeRel  # Field definition of interface fields
        self.advancedFilterFields = advancedFilterFields    # Field definition of ALL model fields

        self.filters = []  # Filters in the combo and checkboxes
        self.fieldsTemplate = []  # Filters in qCompleter
        self.tmpFields = []  # All qcompleter fields created
        self.outFilters = []

        self.tmpLayouts = []    # Temporary "or layouts" to delete when condition is confirmed
        self.tmpLineEdits = []  # Temporary "or line edits" to read and delete
        self.orPressed = False  # Flag to know if or flag has been pressed
        self.widgetContents = None
        self.globalCondition = []   # List of conditions objects

    def launchFilterChanged(self):
        outFilters = []
        for conditionObj in self.globalCondition:
            outFilters.extend(conditionObj.condition)
        utils.logDebug('OutCondition %r' % (str(outFilters)), 'launchFilterChanged')
        if self.parent:
            self.parent.filter_changed_signal.emit(outFilters)

    def applyCondition(self):
        operators = []
        conditionList = []
        intString = ''
        lineEditList = [self.linedit]
        lineEditList.extend(self.tmpLineEdits)
        for lineEdit in lineEditList:
            text = str(lineEdit.text())
            if text:
                fieldObj = self.getTmpField(text)
                conditionList.append(fieldObj.condition)
                operators.append('|')
                intString = intString + fieldObj.interfaceStringWithValue + '\nOr  '
        intString = intString[:-4]
        operators = operators[1:]
        condObj = self.addCondition(operators + conditionList, intString)
        self.addFieldTag(condObj)
        for lay in self.tmpLayouts:
            self.clearQLayoutChildren(lay)
        self.orPressed = False  # Restored to False the or flag
        self.tmpLineEdits = []  # Cleared the ltmp lineedits widgets
        self.linedit.setText('')

    def addCondition(self, cond, intString):
        conditionObj = Condition()
        conditionObj.condition = cond
        conditionObj.intString = intString
        self.globalCondition.append(conditionObj)
        return conditionObj

    def removeCondition(self, conditionObj):
        if conditionObj in self.globalCondition:
            self.globalCondition.remove(conditionObj)

    def orCondition(self):
        self.orPressed = True
        lineEditLay = QtWidgets.QHBoxLayout()
        lineEdit = self.createCommonLineEdit()
        lineEdit.setCompleter(self.completer)
        orButton, applyButton, removeButton = self.createCommonOrButton()
        lineEditLay.addWidget(lineEdit)
        lineEditLay.addWidget(orButton)
        lineEditLay.addWidget(applyButton)
        lineEditLay.addWidget(removeButton)
        removeButton.clicked.connect(partial(self.removeMultyCondition, lineEditLay, lineEdit))
        self.multipleConditionLay.addLayout(lineEditLay)
        self.tmpLayouts.append(lineEditLay)
        self.tmpLineEdits.append(lineEdit)
        lineEdit.selectAll()
        lineEdit.setFocus()

    def removeMultyCondition(self, lineEditLay, lineEdit):
        self.multipleConditionLay.removeItem(lineEditLay)
        lineEditLay.deleteLater()
        self.tmpLayouts.remove(lineEditLay)
        self.tmpLineEdits.remove(lineEdit)

    def createCommonLineEdit(self):
        linedit = CustomLineEdit(self)
        linedit.textChanged.connect(self.textChangedEvent)
        linedit.returnPressed.connect(self.returnPressedLocal)
        return linedit

    def createCommonOrButton(self):
        orButton = QtWidgets.QPushButton('Or')
        orButton.setStyleSheet(constants.BUTTON_STYLE + 'min-height:25px;')
        orButton.clicked.connect(self.orCondition)
        applyButton = QtWidgets.QPushButton('Apply')
        applyButton.setStyleSheet(constants.BUTTON_STYLE + 'min-height:25px;')
        applyButton.clicked.connect(self.applyCondition)
        removeButton = QtWidgets.QPushButton('X')
        removeButton.setStyleSheet(constants.BUTTON_STYLE + 'min-height:25px;')
        return orButton, applyButton, removeButton

    def computeRecursion(self, xmlElementParent):
        self.mainVLay = QtWidgets.QVBoxLayout()
        self.mainVLay.setSpacing(0)
        self.mainVLay.setMargin(0 )
        mainHLay = QtWidgets.QHBoxLayout()
        mainHLay.setSpacing(0)   
        mainHLay.setMargin(0 )   
        self.multipleConditionLay = QtWidgets.QVBoxLayout()
        lineEditLay = QtWidgets.QHBoxLayout()
        # Setup lineedit
        self.linedit = self.createCommonLineEdit()
        self.tmpLineEdits.append(self.linedit)

        # Setup completer
        self.completer = CustomQCompleter()
        self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.completer.setWrapAround(True)
        self.filterListModel = QtCore.QStringListModel()
        self.computeFieldAndFilters(xmlElementParent)
        self.populateCombo()
        self.completer.setModel(self.filterListModel)
        self.linedit.setCompleter(self.completer)
        lineEditLay.addWidget(self.linedit)
        self.linedit.setStyleSheet(constants.BACKGROUND_WHITE)

        # Setup or button
        orButton, _applyButton, _removeButton = self.createCommonOrButton()
        lineEditLay.addWidget(orButton)
        self.multipleConditionLay.addLayout(lineEditLay)
        mainHLay.addLayout(self.multipleConditionLay)

        # Setup filters menu
        self.buttonFilters = QtWidgets.QToolButton()
        self.buttonFilters.setText('Filters')
        self.buttonFilters.setStyleSheet(constants.SEARCH_FILTER_TOOLBUTTON)
        self.buttonFilters.setMenu(self.toolmenu)
        self.buttonFilters.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.buttonFilters.setHidden(True)
        mainHLay.addWidget(self.buttonFilters)

        # Setup advanced filter
        self.buttonCustomFilters = QtWidgets.QPushButton()
        self.buttonCustomFilters.setText('Advanced Filter')
        self.buttonCustomFilters.setStyleSheet(constants.SEARCH_FILTER_TOOLBUTTON)
        self.buttonCustomFilters.setHidden(True)
        self.buttonCustomFilters.clicked.connect(self.customAdvancedFilter)
        mainHLay.addWidget(self.buttonCustomFilters)

        # Setup plus button
        self.buttonPlus = QtWidgets.QPushButton('+')
        self.buttonPlus.setStyleSheet(constants.SEARCH_ADVANCED_BUTTON)
        self.buttonPlus.clicked.connect(self.advancedFilter)
        mainHLay.addWidget(self.buttonPlus)

        mainHLay.setSpacing(3)
        self.mainVLay.addLayout(mainHLay)
        self.tagsLay = QtWidgets.QVBoxLayout()
        self.mainVLay.addLayout(self.tagsLay)
        return self.mainVLay

    def computeFieldAndFilters(self, xmlElementParent):
        self.toolmenu = QtWidgets.QMenu()
        for childElement in xmlElementParent: #.getchildren():
            childTag = childElement.tag
            if childTag == 'filter':
                filterObj = self.computeFilter(childElement)
                action = self.toolmenu.addAction(filterObj.string)
                action.setCheckable(True)
                action.toggled.connect(partial(self.actionSelectionChanged, action))
            elif childTag == 'separator':
                self.toolmenu.addSeparator()
            elif childTag == 'field':   # Values in the line edit
                self.computeField(childElement)
            else:
                logging.warning('Tag %r not supported and not evaluated' % (childElement))

    def computeFilter(self, elemXml):
        fieldAttributes = elemXml.attrib
        filterObj = FilterObj()
        evalDomain = []
        try:
            evalDomain = eval(fieldAttributes.get('domain', ''))
            evalDomain = self.evaluateCondition(evalDomain)
        except Exception as ex:
            logging.error('Unable to compute domain %r. EX: %r' % (fieldAttributes.get('domain', ''), ex))
        operators = []
        conds = []
        for elem in evalDomain:
            if isinstance(elem, (list, tuple)):
                conds.append(elem)
            else:
                operators.append(elem)
        filterObj.condition = operators + conds
        filterObj.string = fieldAttributes.get('string', '')
        filterObj.help = fieldAttributes.get('help', '')
        filterObj.conditionComputedFilter = evalDomain
        if filterObj.string:
            self.filters.append(filterObj)
        return filterObj

    def removeFilter(self, filterObj):
        if filterObj in self.globalCondition:
            self.globalCondition.remove(filterObj)

    def addFilter(self, filterObj):
        self.globalCondition.append(filterObj)

    def actionSelectionChanged(self, actionChange=False, newVal=False):
        if not actionChange:
            logging.warning('Action not found')
            return
        stringOption = str(actionChange.iconText())
        filterObj = self.checkFilter(stringOption)
        if filterObj:
            if not newVal:  # Uncheck the filter
                self.removeFilter(filterObj)
            else:   # Check the filter
                self.addFilter(filterObj)
            self.launchFilterChanged()
        else:
            logging.warning('Unable to find filter for string %r' % (stringOption))

    def computeField(self, elemXml):
        fieldAttributes = elemXml.attrib
        fieldObj = FieldObj()
        fieldObj.name = fieldAttributes.get('name', '')
        fieldObj.fieldDefinition = self.fieldsNameTypeRel.get(fieldObj.name, {})
        fieldObj.string = fieldAttributes.get('string', fieldObj.fieldDefinition.get('string', ''))
        fieldObj.interfaceString = SEARCH_FOR_STRING % (fieldObj.string)
        self.fieldsTemplate.append(fieldObj)
        return fieldObj

    def populateCombo(self, currentVal=''):
        '''
            Populate runtime the QCompleter values for line edit
            @currentVal: Current value digited by user
            @fields: List of field objects
            @filters: List of filter objects
        '''
        currentVal = str(currentVal)
        stringList = []
        #self.tmpFields = []  # Do not remove this clear or search without selecting a value will be break
        if currentVal:
            for fieldObj in self.fieldsTemplate:
                for tmpField in self.tmpFields:
                    if tmpField.interfaceStringWithValue == currentVal:  # User is going to choice with arrows
                        return
                newInterfaceValue = fieldObj.interfaceString + currentVal + '"'
                tmpField = copy.deepcopy(fieldObj)
                tmpField.value = currentVal
                tmpField.interfaceStringWithValue = newInterfaceValue
                tmpField.condition = (tmpField.name, self.searchMode, currentVal)
                self.tmpFields.append(tmpField)
                stringList.append(tmpField.interfaceStringWithValue)
        self.filterListModel.setStringList(stringList)

    def textChangedEvent(self, newText=''):
        newText = str(newText)
        if newText:
            for tmpField in self.tmpFields:
                if str(tmpField.interfaceStringWithValue) == str(newText):
                    self.populateCombo(currentVal=str(tmpField.value))
                    return
            self.populateCombo(currentVal=str(newText))

    def returnPressedLocal(self):
        if self.orPressed:
            return
        timer = QtCore.QTimer()
        self.timers.append(timer)
        timer.timeout.connect(self.delayedAddFieldFilter)
        timer.start(500)

    def clearQLayoutChildren(self, layout):
        for i in reversed(list(range(layout.count()))):
            childLay = layout.itemAt(i)
            widget = childLay.widget()
            if widget:
                widget.setHidden(True)
                widget.setParent(None)
            if isinstance(childLay, (QtWidgets.QHBoxLayout, QtWidgets.QVBoxLayout)):
                self.clearQLayoutChildren(childLay)
        for elem in layout.children():
            if isinstance(childLay, (QtWidgets.QHBoxLayout, QtWidgets.QVBoxLayout)):
                layout.removeItem(elem)
            else:
                layout.removeWidget(elem)

    def delayedAddFieldFilter(self):
        filterText = str(self.linedit.text())
        tmpField = self.getTmpField(filterText)
        if not tmpField:
            return
        condObj = self.addCondition([tmpField.condition], tmpField.interfaceStringWithValue)
        self.addFieldTag(condObj)
        self.linedit.setText('')
        for timer in self.timers:
            timer.stop()

    def getTmpField(self, val):
        for fieldObj in self.tmpFields:
            if fieldObj.interfaceStringWithValue == val:
                return fieldObj
        if self.tmpFields:  # This is to get value is no element is selected from combo and enter event is pressed
            return self.tmpFields[0]
        return False

    def addFieldTag(self, condObj):
        maxFiltersInLine = 2
        hlay = QtWidgets.QHBoxLayout()
        if isinstance(condObj, FilterObj):
            label = QtWidgets.QLabel(condObj.interfaceString)
        else:
            label = QtWidgets.QLabel(condObj.intString)
        label.setStyleSheet(constants.TAG_TEXT_STYLE)
        removeButton = QtWidgets.QPushButton('X')
        removeButton.setStyleSheet(constants.BUTTON_STYLE)
        removeButton.setMaximumWidth(30)

        hlay.setSpacing(0)
        hlay.addWidget(label)
        hlay.addWidget(removeButton)

        childrenWidgetsCount = self.tagsLay.count()
        if childrenWidgetsCount == 0:
            hlayRow = QtWidgets.QHBoxLayout()
            hlayRow.addLayout(hlay)
            self.tagsLay.addLayout(hlayRow)
            removeButton.clicked.connect(partial(self.removeFieldFilter, condObj))
        else:
            rowLay = self.tagsLay.children()[-1]
            rowTagsCount = rowLay.count()
            if rowTagsCount <= maxFiltersInLine:
                rowLay.addLayout(hlay)
                removeButton.clicked.connect(partial(self.removeFieldFilter, condObj))
            else:
                hlayRow = QtWidgets.QHBoxLayout()
                hlayRow.addLayout(hlay)
                self.tagsLay.addLayout(hlayRow)
                removeButton.clicked.connect(partial(self.removeFieldFilter, condObj))
        self.launchFilterChanged()

    def removeFieldFilter(self, conditionObj):
        self.removeCondition(conditionObj)
        self.reloadFilters()

    def reloadFilters(self):
        self.clearQLayoutChildren(self.tagsLay)
        for condObj in self.globalCondition:
            self.addFieldTag(condObj)
        self.launchFilterChanged()

    def computeArchRecursion(self, xmlElementParent):
        self.widgetContents = QtWidgets.QWidget()
        self.mainLayOut = QtWidgets.QVBoxLayout()
        self.mainLayOut.setSpacing(1)
        self.mainLayOut.setMargin(1)
        self.filterListLay = QtWidgets.QHBoxLayout()
        self.mainHLayRec = self.computeRecursion(xmlElementParent)
        #self.widgetContents.setStyleSheet('background-color:#ffffff;')
        self.mainLayOut.addLayout(self.mainHLayRec)
        self.mainLayOut.addLayout(self.filterListLay)
        self.widgetContents.setLayout(self.mainLayOut)
        self.outLay = QtWidgets.QVBoxLayout()
        self.outLay.setSpacing(1)
        self.outLay.setMargin(1)
        self.outLay.addWidget(self.widgetContents)
        return self.outLay

    # This section is dedicated to advanced custom filter

    def acceptDialAnd(self):
        singleFieldLay = self.getSingleFieldLayoutCustom()
        self.customFiltersAdded.append(singleFieldLay)
        self.conditionsCustomLay.addLayout(singleFieldLay)
        self.filterMode = '&'
        self.orButton.setHidden(True)   # Not allow user to filter in different modes in the same time

    def acceptDialOr(self):
        self.filterMode = '|'
        singleFieldLay = self.getSingleFieldLayoutCustom()
        self.customFiltersAdded.append(singleFieldLay)
        self.conditionsCustomLay.addLayout(singleFieldLay)
        self.andButton.setHidden(True)   # Not allow user to filter in different modes in the same time

    def rejectDial(self):
        self.customFiltersAdded = []
        self.dialCustomFilter.reject()

    def applyCustomFilter(self):
        self.dialCustomFilter.accept()

    def getButtonsLay(self):
        # Ok / Cancel buttons and layout
        self.andButton = QtWidgets.QPushButton('Filter as And')
        self.andButton.clicked.connect(self.acceptDialAnd)
        self.andButton.setStyleSheet(constants.LOGIN_ACCEPT_BUTTON)
        self.orButton = QtWidgets.QPushButton('Filter as Or')
        self.orButton.setStyleSheet(constants.LOGIN_ACCEPT_BUTTON)
        self.orButton.clicked.connect(self.acceptDialOr)
        applyButton = QtWidgets.QPushButton('Apply')
        applyButton.setStyleSheet(constants.LOGIN_ACCEPT_BUTTON)
        applyButton.clicked.connect(self.applyCustomFilter)
        cancelButt = QtWidgets.QPushButton('Cancel')
        cancelButt.clicked.connect(self.rejectDial)
        cancelButt.setStyleSheet(constants.LOGIN_CANCEL_BUTTON)

        okCancelLay = QtWidgets.QHBoxLayout()
        okCancelLay.addWidget(cancelButt)
        spacer = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.MinimumExpanding)
        okCancelLay.addSpacerItem(spacer)
        okCancelLay.addWidget(self.andButton)
        okCancelLay.addWidget(self.orButton)
        okCancelLay.addWidget(applyButton)
        return okCancelLay

    def getSingleFieldLayoutCustom(self):
        singleFieldLay = QVBoxLayCustom(self.advancedFilterFields)
        singleFieldLay.removeButton.clicked.connect(partial(self.removeCustomFilter, singleFieldLay))
        return singleFieldLay

    def removeCustomFilter(self, layoutToRemove):
        if layoutToRemove in self.customFiltersAdded:
            self.customFiltersAdded.remove(layoutToRemove)
        self.clearQLayoutChildren(layoutToRemove)

    def customAdvancedFilter(self):
        self.customFiltersAdded = []
        self.filterMode = '&'
        self.dialCustomFilter = QtWidgets.QDialog()
        lay = QtWidgets.QVBoxLayout()
        mainWidget = QtWidgets.QWidget()
        mainLay = QtWidgets.QVBoxLayout()

        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scrollWidget = QtWidgets.QWidget()
        self.conditionsCustomLay = QtWidgets.QVBoxLayout()
        singleFieldLay = self.getSingleFieldLayoutCustom()
        self.customFiltersAdded.append(singleFieldLay)
        buttonsLay = self.getButtonsLay()
        self.conditionsCustomLay.addLayout(singleFieldLay)
        self.conditionsCustomLay.setSpacing(20)
        self.conditionsCustomLay.setMargin(20)
        self.scrollWidget.setLayout(self.conditionsCustomLay)
        self.scroll.setWidget(self.scrollWidget)
        mainLay.addWidget(self.scroll)
        mainLay.addLayout(buttonsLay)
        mainWidget.setLayout(mainLay)
        mainWidget.setStyleSheet(constants.BACKGROUND_WHITE)
        lay.addWidget(mainWidget)
        self.dialCustomFilter.setLayout(lay)
        #self.dialCustomFilter.setStyleSheet(constants.VIOLET_BACKGROUND)

        self.dialCustomFilter.resize(500, 450)
        if self.dialCustomFilter.exec_() == QtWidgets.QDialog.Accepted:
            conditions = []
            operators = []
            interfaceStringSum = ''
            for layoutObj in self.customFiltersAdded:
                condition, interfaceString = layoutObj.getSingleCondition()
                interfaceStringSum = interfaceStringSum + interfaceString + '\n'
                conditions.extend(condition)
                operators.append(self.filterMode)
            if operators:
                del operators[-1]
            globalCondition = operators + conditions
            condObj = self.addCondition(globalCondition, interfaceStringSum)
            self.addFieldTag(condObj)

    def advancedFilter(self):
        if self.buttonFilters.isHidden():
            self.buttonFilters.setHidden(False)
            if self.advancedFilterFields:
                self.buttonCustomFilters.setHidden(False)
            self.buttonPlus.setText('-')
        else:
            self.buttonFilters.setHidden(True)
            self.buttonCustomFilters.setHidden(True)
            self.buttonPlus.setText('+')

    def checkFilter(self, val):
        for filterObj in self.filters:
            if str(filterObj.string.strip()) == str(val):
                return filterObj
        return False

    def addFieldFilter(self, filterString, operator='And', objRel=None):

        def computeOperatorForFilter(op):
            if op.upper() == 'AND':
                return '&'
            elif op.upper() == 'OR':
                return '|'

        if not filterString:
            return

        if not objRel:
            objRel = self.checkTmpField(filterString)
            if not objRel:
                logging.warning('Unable to find filter for string %r' % (filterString))
                return
            objRel = copy.deepcopy(objRel)  # Copied new filter because if you select the same filter again the value will be overwritten

        odooOperator = computeOperatorForFilter(operator)
        tupleCondition = (objRel.name, self.searchMode, objRel.value)
        filterTuple = (odooOperator, objRel)
        objRel.conditionComputedFilter = [tupleCondition]
        self.outFilters.append(filterTuple)
        self.addFilterInterface(filterString, operator, filterTuple)

    def evaluateCondition(self, conditions):
        outFilter = []
        operators = []
        for elem in conditions:
            if isinstance(elem, str):
                if not operators:
                    operators.append(elem)
            elif isinstance(elem, (tuple, list)):
                if not operators:
                    if outFilter and not isinstance(outFilter[-1], str):
                        outFilter.append('&')
                    outFilter.append(elem)
                else:
                    outFilter.append(elem)
                    outFilter.append(operators[0])
                    del operators[0]
            else:
                logging.warning('[evaluateCondition] Cannot evaluate element %r' % (elem))
        return outFilter

    def computeArch(self):
        if self.arch:
            return self.computeArchRecursion(ElementTree.XML(self.arch.encode('utf-8')))


class CustomQCompleter(QtWidgets.QCompleter):
    def __init__(self, parent=None):
        super(CustomQCompleter, self).__init__(parent)
        self.local_completion_prefix = ""
        self.source_model = None

    def setModel(self, model):
        self.source_model = model
        super(CustomQCompleter, self).setModel(self.source_model)

    def updateModel(self):
        local_completion_prefix = self.local_completion_prefix

        class InnerProxyModel(QtCore.QSortFilterProxyModel):
            def filterAcceptsRow(self, sourceRow, sourceParent):
                index0 = self.sourceModel().index(sourceRow, 0, sourceParent)
                searchStr = local_completion_prefix.lower()
                modelStr = self.sourceModel().data(index0, QtCore.Qt.DisplayRole).lower()
                return searchStr in modelStr

        proxy_model = InnerProxyModel()
        proxy_model.setSourceModel(self.source_model)
        super(CustomQCompleter, self).setModel(proxy_model)
        cr = QtCore.QRect(QtCore.QPoint(1, 1), QtCore.QSize(1, 1))
        self.complete(cr)

    def splitPath(self, path):
        self.local_completion_prefix = str(path)
        self.updateModel()
        return ""


class FilterObj(object):
    def __init__(self):
        self.condition = []
        self.string = ''
        self.help = ''
        self.interfaceString = ''
        self.value = ''
        self.conditionComputedFilter = []


class FieldObj(object):
    def __init__(self):
        self.string = ''
        self.name = ''
        self.fieldDefinition = {}
        self.interfaceStringWithValue = ''
        self.interfaceString = ''
        self.value = ''
        self.condition = []


class FieldObjCustom(object):
    def __init__(self):
        self.string = ''
        self.condition = []
        self.interfaceString = ''


class Condition():
    def __init__(self):
        self.condition = ''
        self.intString = ''


class QVBoxLayCustom(QtWidgets.QVBoxLayout):
    def __init__(self, advancedFilterFields):
        super(QVBoxLayCustom, self).__init__()
        self.mainWidget = QtWidgets.QWidget()
        self.removeLay = QtWidgets.QHBoxLayout()
        self.mainLay = QtWidgets.QVBoxLayout()

        self.advancedFilterFields = advancedFilterFields
        # Remove button
        self.removeButton = QtWidgets.QPushButton('X')
        self.removeButton.setHidden(True)
        self.removeButton.setStyleSheet(constants.LOGIN_CANCEL_BUTTON + 'max-height:15px; max-width:7px;height:15px; width:7px;font-weight:bold;')
        self.spacer = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.MinimumExpanding)
        # Fields
        self.widgetsLay = QtWidgets.QVBoxLayout()
        self.combo = self.getComboFields()
        self.widgetsLay.addWidget(self.combo)

        # Create fields widgets
        self.comboCharOperator = QtWidgets.QComboBox()
        self.comboBoolOperator = QtWidgets.QComboBox()
        self.comboFloatOperator = QtWidgets.QComboBox()
        self.comboDatetimeOperator = QtWidgets.QComboBox()
        self.mainLineEditWidget = QtWidgets.QLineEdit()
        self.dateWidget = QtWidgets.QDateEdit()
        self.datetimeWidget = QtWidgets.QDateTimeEdit()
        self.integerSpinboxWidget = QtWidgets.QSpinBox()
        self.comboCharOperator.setStyleSheet(constants.LOGIN_COMBO_STYLE)
        self.comboBoolOperator.setStyleSheet(constants.LOGIN_COMBO_STYLE)
        self.comboFloatOperator.setStyleSheet(constants.LOGIN_COMBO_STYLE)
        self.comboDatetimeOperator.setStyleSheet(constants.LOGIN_COMBO_STYLE)
        self.mainLineEditWidget.setStyleSheet(constants.LOGIN_LINEEDIT_STYLE)
        self.dateWidget.setStyleSheet(constants.LOGIN_LINEEDIT_STYLE)
        self.datetimeWidget.setStyleSheet(constants.LOGIN_LINEEDIT_STYLE)
        self.integerSpinboxWidget.setStyleSheet(constants.LOGIN_LINEEDIT_STYLE)
        self.widgetsLay.addWidget(self.comboCharOperator)
        self.widgetsLay.addWidget(self.comboBoolOperator)
        self.widgetsLay.addWidget(self.comboFloatOperator)
        self.widgetsLay.addWidget(self.comboDatetimeOperator)
        self.widgetsLay.addWidget(self.mainLineEditWidget)
        self.widgetsLay.addWidget(self.dateWidget)
        self.widgetsLay.addWidget(self.datetimeWidget)
        self.widgetsLay.addWidget(self.integerSpinboxWidget)
        self.comboValues = ['Contains',
                            "Doesn't contains",
                            'Is equal to',
                            'Is not equal to',
                            'Is set',
                            'Is not set']
        self.comboBoolValues = ['Is true', 'Is false']
        self.comboFloatValues = ['Is equal to',
                                 'Is not equal to',
                                 'Greater than',
                                 'Less than',
                                 'Greater than or equal to',
                                 'Less then or equal to',
                                 'Is set',
                                 'Is not set']
        self.comboDatetimeValues = self.comboFloatValues
        self.comboDatetimeValues.append('Is between')
        self.comboDatetimeOperator.addItems(self.comboDatetimeValues)
        self.comboBoolOperator.addItems(self.comboBoolValues)
        self.comboFloatOperator.addItems(self.comboFloatValues)
        self.comboCharOperator.addItems(self.comboValues)
        self.hideAll()
        self.mainLay.addLayout(self.widgetsLay)
        self.removeLay.addLayout(self.mainLay)
        self.removeLay.addWidget(self.removeButton)
        self.mainWidget.setLayout(self.removeLay)
        self.addWidget(self.mainWidget)
        self.mainWidget.setStyleSheet(constants.BACKGROUND_LIGHT_BLUE)

    def getSelectedFieldName(self):
        comboIndex = self.combo.currentIndex()
        fieldString = self.comboFieldsList[comboIndex]
        return self.stringFieldRel[fieldString], fieldString

    def getSingleCondition(self):
        fieldName, fieldString = self.getSelectedFieldName()
        return self.getCondition(fieldName, fieldString)

    def fieldsCustomComboChanged(self, newIndex):
        self.removeButton.setHidden(False)
        fieldString = self.comboFieldsList[newIndex]
        fieldName = self.stringFieldRel.get(fieldString)
        fieldDefinition = self.advancedFilterFields[fieldName]
        fieldType = fieldDefinition.get('type', '')
        self.hideAll()
        if fieldType in ['char', 'many2one', 'text', 'one2many', 'many2many']:
            self.comboCharOperator.setHidden(False)
            self.mainLineEditWidget.setHidden(False)
        elif fieldType == 'boolean':
            self.comboBoolOperator.setHidden(False)
        elif fieldType == 'float':
            self.comboFloatOperator.setHidden(False)
            self.mainLineEditWidget.setHidden(False)
        elif fieldType == 'date':
            self.dateWidget.setHidden(False)
            self.comboDatetimeOperator.setHidden(False)
        elif fieldType == 'datetime':
            self.datetimeWidget.setHidden(False)
            self.comboDatetimeOperator.setHidden(False)
        elif fieldType == 'integer':
            self.comboFloatOperator.setHidden(False)
            self.integerSpinboxWidget.setHidden(False)

    def getValue(self, fieldType):
        if fieldType in ['char', 'many2one', 'text', 'one2many', 'many2many']:
            return str(self.mainLineEditWidget.text())
        elif fieldType == 'boolean':
            return ''
        elif fieldType == 'date':
            return str(self.dateWidget.date().toPyDate())
        elif fieldType == 'datetime':
            return str(self.datetimeWidget.dateTime().toPyDateTime())
        elif fieldType == 'integer':
            return self.integerSpinboxWidget.value()
        elif fieldType == 'float':
            try:
                return float(str(self.mainLineEditWidget.text()))
            except Exception as ex:
                utils.logMessage('warning', str(ex), 'getValue')
                utilsUi.popWarning(None, 'Wrong value for float field!')
                return 0

    def hideAll(self):
        self.comboCharOperator.setHidden(True)
        self.mainLineEditWidget.setHidden(True)
        self.comboBoolOperator.setHidden(True)
        self.comboFloatOperator.setHidden(True)
        self.integerSpinboxWidget.setHidden(True)
        self.dateWidget.setHidden(True)
        self.comboDatetimeOperator.setHidden(True)
        self.datetimeWidget.setHidden(True)
        self.mainLineEditWidget.setText('')

    def getComboFields(self):
        # Fields combo
        sortedFields = []
        self.stringFieldRel = {}
        comboAllFields = QtWidgets.QComboBox()
        comboAllFields.setStyleSheet(constants.LOGIN_COMBO_STYLE)

        for fieldName in list(self.advancedFilterFields.keys()):
            fieldDefinition = self.advancedFilterFields.get(fieldName)
            fieldString = fieldDefinition.get('string', '')
            fieldType = fieldDefinition.get('type', '')
            if fieldType == 'binary':
                continue
            sortedFields.append(fieldString)
            self.stringFieldRel[fieldString] = fieldName

        sortedFields.sort()
        self.comboFieldsList = sortedFields
        for fieldString in sortedFields:
            comboAllFields.addItem(fieldString)
        comboAllFields.currentIndexChanged.connect(self.fieldsCustomComboChanged)
        return comboAllFields

    def getCondition(self, fieldName, fieldString):
        fieldDefinition = self.advancedFilterFields[fieldName]
        fieldType = fieldDefinition.get('type', '')
        value = self.getValue(fieldType)
        if fieldType in ['char', 'many2one', 'text', 'one2many', 'many2many']:
            operatorIndex = self.comboCharOperator.currentIndex()
            interfaceVal = self.comboValues[operatorIndex]
            if interfaceVal == 'Contains':
                return [(fieldName, 'ilike', value)], '%r %r %r' % (fieldString, interfaceVal, value)
            elif interfaceVal == "Doesn't contains":
                return [(fieldName, 'not ilike', value)], '%r %r %r' % (fieldString, interfaceVal, value)
            elif interfaceVal == 'Is equal to':
                return [(fieldName, '=', value)], '%r %r %r' % (fieldString, interfaceVal, value)
            elif interfaceVal == 'Is not equal to':
                return [(fieldName, '!=', value)], '%r %r %r' % (fieldString, interfaceVal, value)
            elif interfaceVal == 'Is set':
                return [(fieldName, '!=', False), '|', (fieldName, '!=', '')], '%r %r %r' % (fieldString, interfaceVal)
            elif interfaceVal == 'Is not set':
                return [(fieldName, '=', False), '|', (fieldName, '=', '')], '%r %r %r' % (fieldString, interfaceVal)
        elif fieldType == 'boolean':
            operatorIndex = self.comboBoolOperator.currentIndex()
            interfaceVal = self.comboBoolValues[operatorIndex]
            if interfaceVal == 'Is true':
                return [(fieldName, '=', True)], '%r %r %r' % (fieldString, interfaceVal)
            elif interfaceVal == 'Is false':
                return [(fieldName, '=', False)], '%r %r %r' % (fieldString, interfaceVal)
        elif fieldType == 'float':
            operatorIndex = self.comboFloatOperator.currentIndex()
            interfaceVal = self.comboFloatValues[operatorIndex]
            if interfaceVal == 'Is equal to':
                return [(fieldName, '=', value)], '%r %r %r' % (fieldString, interfaceVal, value)
            elif interfaceVal == 'Is not equal to':
                return [(fieldName, '!=', value)], '%r %r %r' % (fieldString, interfaceVal, value)
            elif interfaceVal == 'Greater than':
                return [(fieldName, '>', value)], '%r %r %r' % (fieldString, interfaceVal, value)
            elif interfaceVal == 'Less than':
                return [(fieldName, '<', value)], '%r %r %r' % (fieldString, interfaceVal, value)
            elif interfaceVal == 'Greater than or equal to':
                return [(fieldName, '>=', value)], '%r %r %r' % (fieldString, interfaceVal, value)
            elif interfaceVal == 'Less then or equal to':
                return [(fieldName, '<=', value)], '%r %r %r' % (fieldString, interfaceVal, value)
            elif interfaceVal == 'Is set':
                return [(fieldName, '!=', False), '|', (fieldName, '!=', 0)], '%r %r %r' % (fieldString, interfaceVal)
            elif interfaceVal == 'Is not set':
                return [(fieldName, '=', False), '|', (fieldName, '=', 0)], '%r %r %r' % (fieldString, interfaceVal)
        elif fieldType == 'date':
            operatorIndex = self.comboDatetimeOperator.currentIndex()
            interfaceVal = self.comboDatetimeValues[operatorIndex]
            if interfaceVal == 'Is equal to':
                return [(fieldName, '=', value)], '%r %r %r' % (fieldString, interfaceVal, value)
            elif interfaceVal == 'Is not equal to':
                return [(fieldName, '!=', value)], '%r %r %r' % (fieldString, interfaceVal, value)
            elif interfaceVal == 'Greater than':
                return [(fieldName, '>', value)], '%r %r %r' % (fieldString, interfaceVal, value)
            elif interfaceVal == 'Less than':
                return [(fieldName, '<', value)], '%r %r %r' % (fieldString, interfaceVal, value)
            elif interfaceVal == 'Greater than or equal to':
                return [(fieldName, '>=', value)], '%r %r %r' % (fieldString, interfaceVal, value)
            elif interfaceVal == 'Less then or equal to':
                return [(fieldName, '<=', value)], '%r %r %r' % (fieldString, interfaceVal, value)
            elif interfaceVal == 'Is set':
                return [(fieldName, '!=', False), '|', (fieldName, '!=', 0)], '%r %r %r' % (fieldString, interfaceVal)
            elif interfaceVal == 'Is not set':
                return [(fieldName, '=', False), '|', (fieldName, '=', 0)], '%r %r %r' % (fieldString, interfaceVal)
        elif fieldType == 'datetime':
            operatorIndex = self.comboDatetimeOperator.currentIndex()
            interfaceVal = self.comboDatetimeValues[operatorIndex]
            if interfaceVal == 'Is equal to':
                return [(fieldName, '=', value)], '%r %r %r' % (fieldString, interfaceVal, value)
            elif interfaceVal == 'Is not equal to':
                return [(fieldName, '!=', value)], '%r %r %r' % (fieldString, interfaceVal, value)
            elif interfaceVal == 'Greater than':
                return [(fieldName, '>', value)], '%r %r %r' % (fieldString, interfaceVal, value)
            elif interfaceVal == 'Less than':
                return [(fieldName, '<', value)], '%r %r %r' % (fieldString, interfaceVal, value)
            elif interfaceVal == 'Greater than or equal to':
                return [(fieldName, '>=', value)], '%r %r %r' % (fieldString, interfaceVal, value)
            elif interfaceVal == 'Less then or equal to':
                return [(fieldName, '<=', value)], '%r %r %r' % (fieldString, interfaceVal, value)
            elif interfaceVal == 'Is set':
                return [(fieldName, '!=', False), '|', (fieldName, '!=', 0)], '%r %r %r' % (fieldString, interfaceVal)
            elif interfaceVal == 'Is not set':
                return [(fieldName, '=', False), '|', (fieldName, '=', 0)], '%r %r %r' % (fieldString, interfaceVal)
        elif fieldType == 'integer':
            operatorIndex = self.comboFloatOperator.currentIndex()
            interfaceVal = self.comboFloatValues[operatorIndex]
            if interfaceVal == 'Is equal to':
                return [(fieldName, '=', value)], '%r %r %r' % (fieldString, interfaceVal, value)
            elif interfaceVal == 'Is not equal to':
                return [(fieldName, '!=', value)], '%r %r %r' % (fieldString, interfaceVal, value)
            elif interfaceVal == 'Greater than':
                return [(fieldName, '>', value)], '%r %r %r' % (fieldString, interfaceVal, value)
            elif interfaceVal == 'Less than':
                return [(fieldName, '<', value)], '%r %r %r' % (fieldString, interfaceVal, value)
            elif interfaceVal == 'Greater than or equal to':
                return [(fieldName, '>=', value)], '%r %r %r' % (fieldString, interfaceVal, value)
            elif interfaceVal == 'Less then or equal to':
                return [(fieldName, '<=', value)], '%r %r %r' % (fieldString, interfaceVal, value)
            elif interfaceVal == 'Is set':
                return [(fieldName, '!=', False), '|', (fieldName, '!=', 0)], '%r %r %r' % (fieldString, interfaceVal)
            elif interfaceVal == 'Is not set':
                return [(fieldName, '=', False), '|', (fieldName, '=', 0)], '%r %r %r' % (fieldString, interfaceVal)
        return []


class CustomLineEdit(QtWidgets.QLineEdit):
    def __init__(self, parentClass):
        self.parentClass = parentClass
        return super(CustomLineEdit, self).__init__()

    def keyPressEvent(self, event):
        key = event.key()
        modifiers = int(event.modifiers())
        if key == QtCore.Qt.Key_Return:
            if modifiers == QtCore.Qt.CTRL:
                self.parentClass.orCondition()
        return super(CustomLineEdit, self).keyPressEvent(event)
