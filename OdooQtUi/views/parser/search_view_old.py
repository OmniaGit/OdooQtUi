'''
Created on 3 Feb 2017

@author: Daniel Smerghetto
'''
import xml.etree.cElementTree as ElementTree
from PySide2 import QtGui
from PySide2 import QtCore
from functools import partial
from utils_odoo_conn import constants
from utils_odoo_conn import utils
from utils_odoo_conn import utilsUi
import logging
import copy
# Do not delete these, are necessary to compute filters coming from server
import datetime                                 
from dateutil.relativedelta import relativedelta

SEARCH_FOR_STRING = 'Search "%s" for: "'


class SearchView(object):

    def __init__(self, arch='', fieldsNameTypeRel={}, parent=False, searchMode='ilike', advancedFilterFields={}):
        self.searchMode = searchMode
        self.arch = arch
        self.parent = parent
        super(SearchView, self).__init__()
        self.filters = []   # list of objects "Filter" to filter in the tool button choice
        # self.fieldsSearch = []  # list of objects "Field" to filter in the line edit
        self.fieldsSearchTemplate = []  # Template fields for the qcompleter
        self.fieldsSearch = []
        self.timers = []    # timers to add filters in delayed mode
        self.fieldsNameTypeRel = fieldsNameTypeRel  # fields definition of the parent view
        
        self.fieldFilters = []    # filters to be returned (came from fields)
        self.conditionFilters = [] # filters came from tool button (came from filters)
        self.customFilters = [] # filters came from custom dialog
        
        # When signal of filter changed is emitted condition filter are appended to field filters and return the result
        self.advancedFilterFields = advancedFilterFields

    def computeArchRecursion(self, xmlElementParent):
        widgetContents = QtGui.QWidget()
        mainLay = QtGui.QVBoxLayout()
        filterListLay = QtGui.QHBoxLayout()
        mainHLay = self.computeRecursion(xmlParent=xmlElementParent)
        widgetContents.setStyleSheet('background-color:#ffffff;')
        mainLay.addLayout(mainHLay)
        mainLay.addLayout(filterListLay)
        widgetContents.setLayout(mainLay)
        outLay = QtGui.QVBoxLayout()
        outLay.addWidget(widgetContents)
        return outLay

    def computeRecursion(self, xmlElementParent):
        self.mainVLay = QtGui.QVBoxLayout()
        mainHLay = QtGui.QHBoxLayout()
        customFiltersLay = QtGui.QHBoxLayout()
        self.tagsLay = QtGui.QVBoxLayout()
        self.customFiltersTagsLay = QtGui.QVBoxLayout()

        self.buttonFilters = QtGui.QToolButton()
        self.buttonFilters.setText('Filters')
        self.buttonFilters.setStyleSheet(constants.SEARCH_FILTER_TOOLBUTTON)

        self.buttonCustomFilters = QtGui.QPushButton()
        self.buttonCustomFilters.setText('Advanced Filter')
        self.buttonCustomFilters.setStyleSheet(constants.SEARCH_FILTER_TOOLBUTTON)
        self.buttonCustomFilters.setHidden(True)
        self.buttonCustomFilters.clicked.connect(self.customAdvancedFilter)

        customFiltersLay.addLayout(self.customFiltersTagsLay)
        spacer = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.MinimumExpanding)
        customFiltersLay.addSpacerItem(spacer)
        customFiltersLay.addWidget(self.buttonFilters)
        customFiltersLay.addWidget(self.buttonCustomFilters)

        self.toolmenu = QtGui.QMenu()
        for childElement in xmlElementParent.getchildren():
            childTag = childElement.tag
            if childTag == 'filter':
                filterObj = self.computeFilter(childElement)
                action = self.toolmenu.addAction(filterObj.string)
                action.setCheckable(True)
                action.toggled.connect(partial(self.actionSelectionChanged, action))
            elif childTag == 'field':   # Values in the line edit
                self.computeField(childElement)
            elif childTag == 'separator':
                self.toolmenu.addSeparator()
            else:
                logging.warning('Tag %r not supported and not evaluated' % (childElement))
        self.buttonFilters.setMenu(self.toolmenu)
        self.buttonFilters.setPopupMode(QtGui.QToolButton.InstantPopup)
        self.buttonFilters.setHidden(True)
        self.linedit = QtGui.QLineEdit()
        self.linedit.textChanged.connect(self.textChangedEvent)
        self.linedit.returnPressed.connect(self.returnPressedLocal)
        self.completer = CustomQCompleter()
        self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.completer.setWrapAround(True)
        self.filterListModel = QtGui.QStringListModel()
        self.populateCombo()
        self.completer.setModel(self.filterListModel)
        self.linedit.setCompleter(self.completer)
        
        self.searchButton = QtGui.QPushButton('Or')
        self.searchButton.setStyleSheet(constants.BUTTON_STYLE)
        self.searchButton.clicked.connect(self.orCondition)

        self.buttonAdvancedFilter = QtGui.QPushButton('+')
        self.buttonAdvancedFilter.setStyleSheet(constants.SEARCH_ADVANCED_BUTTON)
        self.buttonAdvancedFilter.clicked.connect(self.advancedFilter)

        mainHLay.addWidget(self.linedit)
        mainHLay.addWidget(self.searchButton)
        mainHLay.addWidget(self.buttonAdvancedFilter)
        mainHLay.setSpacing(3)
        
        self.mainVLay.addLayout(mainHLay)
        
        self.filtersGroupsLay = QtGui.QHBoxLayout()
        self.mainVLay.addLayout(self.filtersGroupsLay)
        self.filtersGroupsLay.addLayout(customFiltersLay)
        self.mainVLay.addLayout(self.tagsLay)
        return self.mainVLay

    def customAdvancedFilter(self):
        comboValues = ['Contains', "Doesn't contains", 'Is equal to', 'Is not equal to', 'Is set', 'Is not set']
        comboBoolValues = ['Is true', 'Is false']
        comboFloatValues = ['Is equal to', 'Is not equal to', 'Greater than', 'Less than', 'Greater than or equal to',
                            'Less then or equal to', 'Is set', 'Is not set']
        sortedFields = []
        stringFieldRel = {}
        dial = QtGui.QDialog()
        mainLay = QtGui.QVBoxLayout()
        lay = QtGui.QVBoxLayout()
        mainWidget = QtGui.QWidget()
        comboCharOperator = QtGui.QComboBox()
        comboCharOperator.setStyleSheet(constants.LOGIN_COMBO_STYLE)
        comboBoolOperator = QtGui.QComboBox()
        comboBoolOperator.setStyleSheet(constants.LOGIN_COMBO_STYLE)
        comboDatetimeOperator = QtGui.QComboBox()
        comboDatetimeOperator.setStyleSheet(constants.LOGIN_COMBO_STYLE)
        comboFloatOperator = QtGui.QComboBox()
        comboFloatOperator.setStyleSheet(constants.LOGIN_COMBO_STYLE)
        dateWidget = QtGui.QDateEdit()
        datetimeWidget = QtGui.QDateTimeEdit()
        integerSpinboxWidget = QtGui.QSpinBox()
        mainLineEditWidget = QtGui.QLineEdit()
        
        self.filterMode = '&'

        def acceptDialAnd():
            self.filterMode = '&'
            dial.accept()

        def acceptDialOr():
            self.filterMode = '|'
            dial.accept()

        def rejectDial():
            dial.reject()
        
        def hideAll():
            comboCharOperator.setHidden(True)
            mainLineEditWidget.setHidden(True)
            comboBoolOperator.setHidden(True)
            comboFloatOperator.setHidden(True)
            integerSpinboxWidget.setHidden(True)
            dateWidget.setHidden(True)
            comboDatetimeOperator.setHidden(True)
            datetimeWidget.setHidden(True)
            mainLineEditWidget.setText('')

        def fieldsCustomComboChanged(newIndex):
            fieldString = sortedFields[newIndex]
            fieldName = stringFieldRel.get(fieldString)
            fieldDefinition = self.advancedFilterFields[fieldName]
            fieldType = fieldDefinition.get('type', '')
            hideAll()
            if fieldType in ['char', 'many2one', 'text', 'one2many', 'many2many']:
                comboCharOperator.setHidden(False)
                mainLineEditWidget.setHidden(False)
            elif fieldType == 'boolean':
                comboBoolOperator.setHidden(False)
            elif fieldType == 'float':
                comboFloatOperator.setHidden(False)
                mainLineEditWidget.setHidden(False)
            elif fieldType == 'date':
                dateWidget.setHidden(False)
                comboDatetimeOperator.setHidden(False)
            elif fieldType == 'datetime':
                datetimeWidget.setHidden(False)
                comboDatetimeOperator.setHidden(False)
            elif fieldType == 'integer':
                comboFloatOperator.setHidden(False)
                integerSpinboxWidget.setHidden(False)
            
        # Ok / Cancel buttons and layout
        andButton = QtGui.QPushButton('Filter as And')
        andButton.clicked.connect(acceptDialAnd)
        andButton.setStyleSheet(constants.LOGIN_ACCEPT_BUTTON)
        orButton = QtGui.QPushButton('Filter as Or')
        orButton.setStyleSheet(constants.LOGIN_ACCEPT_BUTTON)
        orButton.clicked.connect(acceptDialOr)
        cancelButt = QtGui.QPushButton('Cancel')
        cancelButt.clicked.connect(rejectDial)
        cancelButt.setStyleSheet(constants.LOGIN_CANCEL_BUTTON)

        okCancelLay = QtGui.QHBoxLayout()
        okCancelLay.addWidget(cancelButt)
        spacer = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.MinimumExpanding)
        okCancelLay.addSpacerItem(spacer)
        okCancelLay.addWidget(andButton)
        okCancelLay.addWidget(orButton)

        # Fields combo
        comboAvailableFields = QtGui.QComboBox()
        comboAvailableFields.setStyleSheet(constants.LOGIN_COMBO_STYLE)
        
        for fieldName in list(self.advancedFilterFields.keys()):
            fieldDefinition = self.advancedFilterFields.get(fieldName)
            fieldString = fieldDefinition.get('string', '')
            fieldType = fieldDefinition.get('type', '')
            if fieldType == 'binary':
                continue
            sortedFields.append(fieldString)
            stringFieldRel[fieldString] = fieldName
        
        sortedFields.sort()
        for fieldString in sortedFields:
            comboAvailableFields.addItem(fieldString)
            comboAvailableFields.currentIndexChanged.connect(fieldsCustomComboChanged)
        
        centerLay = QtGui.QVBoxLayout()
        centerLay.addWidget(comboAvailableFields)
        
        # char
        comboCharOperator.addItems(comboValues)
        centerLay.addWidget(comboCharOperator)
        # bool
        comboBoolOperator.addItems(comboBoolValues)
        centerLay.addWidget(comboBoolOperator)
        # float
        comboFloatOperator.addItems(comboFloatValues)
        centerLay.addWidget(comboFloatOperator)
        # integer
        centerLay.addWidget(integerSpinboxWidget)
        # datetime
        comboDatetimeValues = comboFloatValues
        comboDatetimeValues.append('Is between')
        comboDatetimeOperator.addItems(comboDatetimeValues)
        centerLay.addWidget(comboDatetimeOperator)
        centerLay.addWidget(datetimeWidget)
        # date
        centerLay.addWidget(dateWidget)

        
        
        centerLay.addWidget(mainLineEditWidget)
        hideAll()
        mainLay.addLayout(centerLay)
        mainLay.addLayout(okCancelLay)
        mainLay.setMargin(30)
        mainWidget.setLayout(mainLay)
        mainWidget.setStyleSheet(constants.BACKGROUND_WHITE)
        lay.addWidget(mainWidget)
        dial.setLayout(lay)
        dial.setStyleSheet(constants.VIOLET_BACKGROUND)
        if dial.exec_() == QtGui.QDialog.Accepted:
            newIndex = comboAvailableFields.currentIndex()
            fieldString = sortedFields[newIndex]
            fieldName = stringFieldRel.get(fieldString)
            fieldDefinition = self.advancedFilterFields[fieldName]
            fieldType = fieldDefinition.get('type', '')
            value = str(mainLineEditWidget.text())
            odooCondition = []
            if fieldType in ['char', 'many2one', 'text', 'one2many', 'many2many']:
                operatorIndex = comboCharOperator.currentIndex()
                interfaceVal = comboValues[operatorIndex]
                if interfaceVal == 'Contains':
                    odooCondition = [(fieldName, 'ilike', value)]
                elif interfaceVal == "Doesn't contains":
                    odooCondition = [(fieldName, 'not ilike', value)]
                elif interfaceVal == 'Is equal to':
                    odooCondition = [(fieldName,'=', value)]
                elif interfaceVal == 'Is not equal to':
                    odooCondition = [(fieldName,'!=', value)]
                elif interfaceVal == 'Is set':
                    odooCondition = [(fieldName, '!=', False), '|', (fieldName, '!=', '')]
                elif interfaceVal == 'Is not set':
                    odooCondition = [(fieldName, '=', False), '|', (fieldName, '=', '')]
            elif fieldType == 'boolean':
                operatorIndex = comboBoolOperator.currentIndex()
                interfaceVal = comboBoolValues[operatorIndex]
                if interfaceVal == 'Is true':
                    odooCondition = [(fieldName,'=', True)]
                    value = True
                elif interfaceVal == 'Is false':
                    odooCondition = [(fieldName,'=', False)]
                    value = True
            elif fieldType == 'float':
                try:
                    floatVal = float(value)
                except Exception:
                    utilsUi.popWarning(dial, 'Wrong value for float field!')
                    return
                operatorIndex = comboFloatOperator.currentIndex()
                interfaceVal = comboFloatValues[operatorIndex]
                if interfaceVal == 'Is equal to':
                    odooCondition = [(fieldName,'=', floatVal)]
                elif interfaceVal == 'Is not equal to':
                    odooCondition = [(fieldName,'!=', floatVal)]
                elif interfaceVal == 'Greater than':
                    odooCondition = [(fieldName,'>', floatVal)]
                elif interfaceVal == 'Less than':
                    odooCondition = [(fieldName,'<', floatVal)]
                elif interfaceVal == 'Greater than or equal to':
                    odooCondition = [(fieldName,'>=', floatVal)]
                elif interfaceVal == 'Less then or equal to':
                    odooCondition = [(fieldName,'<=', floatVal)]
                elif interfaceVal == 'Is set':
                    odooCondition = [(fieldName,'!=', False), '|', (fieldName, '!=', 0)]
                elif interfaceVal == 'Is not set':
                    odooCondition = [(fieldName,'=', False), '|', (fieldName, '=', 0)]
                value = floatVal
            elif fieldType == 'date':
                value = str(dateWidget.date().toPyDate())
                operatorIndex = comboDatetimeOperator.currentIndex()
                interfaceVal = comboDatetimeValues[operatorIndex]
                if interfaceVal == 'Is equal to':
                    odooCondition = [(fieldName,'=', value)]
                elif interfaceVal == 'Is not equal to':
                    odooCondition = [(fieldName,'!=', value)]
                elif interfaceVal == 'Greater than':
                    odooCondition = [(fieldName,'>', value)]
                elif interfaceVal == 'Less than':
                    odooCondition = [(fieldName,'<', value)]
                elif interfaceVal == 'Greater than or equal to':
                    odooCondition = [(fieldName,'>=', value)]
                elif interfaceVal == 'Less then or equal to':
                    odooCondition = [(fieldName,'<=', value)]
                elif interfaceVal == 'Is set':
                    odooCondition = [(fieldName,'!=', False), '|', (fieldName, '!=', 0)]
                elif interfaceVal == 'Is not set':
                    odooCondition = [(fieldName,'=', False), '|', (fieldName, '=', 0)]
            elif fieldType == 'datetime':
                operatorIndex = comboDatetimeOperator.currentIndex()
                value = str(datetimeWidget.dateTime().toPyDateTime())
                interfaceVal = comboDatetimeValues[operatorIndex]
                if interfaceVal == 'Is equal to':
                    odooCondition = [(fieldName,'=', value)]
                elif interfaceVal == 'Is not equal to':
                    odooCondition = [(fieldName,'!=', value)]
                elif interfaceVal == 'Greater than':
                    odooCondition = [(fieldName,'>', value)]
                elif interfaceVal == 'Less than':
                    odooCondition = [(fieldName,'<', value)]
                elif interfaceVal == 'Greater than or equal to':
                    odooCondition = [(fieldName,'>=', value)]
                elif interfaceVal == 'Less then or equal to':
                    odooCondition = [(fieldName,'<=', value)]
                elif interfaceVal == 'Is set':
                    odooCondition = [(fieldName,'!=', False), '|', (fieldName, '!=', 0)]
                elif interfaceVal == 'Is not set':
                    odooCondition = [(fieldName,'=', False), '|', (fieldName, '=', 0)]
            elif fieldType == 'integer':
                operatorIndex = comboFloatOperator.currentIndex()
                value = integerSpinboxWidget.value()
                interfaceVal = comboFloatValues[operatorIndex]
                if interfaceVal == 'Is equal to':
                    odooCondition = [(fieldName,'=', value)]
                elif interfaceVal == 'Is not equal to':
                    odooCondition = [(fieldName,'!=', value)]
                elif interfaceVal == 'Greater than':
                    odooCondition = [(fieldName,'>', value)]
                elif interfaceVal == 'Less than':
                    odooCondition = [(fieldName,'<', value)]
                elif interfaceVal == 'Greater than or equal to':
                    odooCondition = [(fieldName,'>=', value)]
                elif interfaceVal == 'Less then or equal to':
                    odooCondition = [(fieldName,'<=', value)]
                elif interfaceVal == 'Is set':
                    odooCondition = [(fieldName,'!=', False), '|', (fieldName, '!=', 0)]
                elif interfaceVal == 'Is not set':
                    odooCondition = [(fieldName,'=', False), '|', (fieldName, '=', 0)]
            if odooCondition:
                odooCond = [self.filterMode]
                odooCond.extend(odooCondition)
                intFilterMode = 'And'
                if self.filterMode == '|':
                    intFilterMode = 'Or'
                intFieldName = fieldDefinition.get('string', fieldName)
                interfaceStr = '%s %s "%s"' % (intFieldName, interfaceVal, value)
                fieldCustomObj = FieldObjCustom()
                fieldCustomObj.domain = odooCond
                fieldCustomObj.interfaceString = interfaceStr
                self.customFilters.append(fieldCustomObj)
                
                hlay = QtGui.QHBoxLayout()
                hlay.setSpacing(0)
                labelText = QtGui.QLabel()
                labelOperator = QtGui.QLabel()
                closeButton = QtGui.QPushButton()
                labelText.setText(interfaceStr)
                labelText.setStyleSheet(constants.TAG_TEXT_STYLE)
                labelOperator.setText(intFilterMode)
                labelOperator.setStyleSheet(constants.OPERATOR_LABEL)
                closeButton.setText('X')
                closeButton.setStyleSheet(constants.BUTTON_STYLE)
                closeButton.clicked.connect(partial(self.removeCustomTag, closeButton, labelOperator, labelText, fieldCustomObj))
                hlay.addWidget(labelOperator)
                hlay.addWidget(labelText)
                hlay.addWidget(closeButton)
                
                
                rowsCount = self.customFiltersTagsLay.count()
                if not rowsCount:
                    rowLay = QtGui.QHBoxLayout()
                    rowLay.addLayout(hlay)
                    spacer = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.MinimumExpanding)
                    rowLay.addSpacerItem(spacer)
                    self.customFiltersTagsLay.addLayout(rowLay)
                else:
                    lastRow = self.customFiltersTagsLay.children()[-1]
                    childrenCount = lastRow.count()
                    if childrenCount >= 4:
                        rowLay = QtGui.QHBoxLayout()
                        rowLay.addLayout(hlay)
                        spacer = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.MinimumExpanding)
                        rowLay.addSpacerItem(spacer)
                        self.customFiltersTagsLay.addLayout(rowLay)
                    else:
                        lastRow.addLayout(hlay)
                self.launchFilterChanged()

    def removeCustomTag(self, removeButton, labelOperator, labelText, fieldCustomObj):
        if fieldCustomObj in self.customFilters:
            removeButton.hide()
            labelOperator.hide()
            labelText.hide()
            self.customFilters.remove(fieldCustomObj)
            self.launchFilterChanged()

    def actionSelectionChanged(self, actionChange=False, newVal=False):
        if not actionChange:
            logging.warning('Action not found')
            return
        stringOption = str(actionChange.iconText())
        filterObj = self.checkFilter(stringOption)
        if filterObj:
            if not newVal:  # Uncheck the filter
                lenFilters = len(self.conditionFilters)
                filterIndex = self.conditionFilters.index(filterObj)
                if filterIndex == 0:    # Remove the first filter
                    if lenFilters == 1:
                        del self.conditionFilters[0]
                    else:
                        del self.conditionFilters[1]    # Remove operator
                        del self.conditionFilters[0]    # Remove filterObject
                else:   # Remove any other filter
                    del self.conditionFilters[filterIndex]    # Remove operator
                    del self.conditionFilters[filterIndex - 1]    # Remove filterObject
            else:   # Check the filter
                if not self.conditionFilters:
                    self.conditionFilters = [filterObj]
                else:
                    self.conditionFilters.append('|')
                    self.conditionFilters.append(filterObj)
            self.launchFilterChanged()
        else:
            logging.warning('Unable to find filter for string %r' % (stringOption))
        
    def advancedFilter(self):
        if self.buttonFilters.isHidden():
            self.buttonFilters.setHidden(False)
            if self.advancedFilterFields:
                self.buttonCustomFilters.setHidden(False)
            self.buttonAdvancedFilter.setText('-')
        else:
            self.buttonFilters.setHidden(True)
            self.buttonCustomFilters.setHidden(True)
            self.buttonAdvancedFilter.setText('+')

    def checkField(self, val):
        for fieldObj in self.fieldFilters:
            if fieldObj.interfaceString == val:
                return fieldObj
        return False

    def checkFieldSearch(self, val):
        for fieldObj in self.fieldsSearch:
            if fieldObj.interfaceStringWithValue == val:
                return fieldObj
        return False
        
    def lastFieldsQCompleter(self, val):
        for fieldObj in self.fieldsSearchTemplate:
            if fieldObj.interfaceStringWithValue == val:
                return fieldObj
        return False

    def checkFilter(self, val):
        for filterObj in self.filters:
            if str(filterObj.string.strip()) == str(val):
                return filterObj
        return False

    def clearQLayoutChildren(self, layout):
        for i in reversed(list(range(layout.count()))): 
            childLay = layout.itemAt(i)
            widget = childLay.widget()
            if widget:
                widget.setParent(None)
            if isinstance(childLay, (QtGui.QHBoxLayout, QtGui.QVBoxLayout)):
                self.clearQLayoutChildren(childLay)

    def reloadFilters(self):
        def computeOperatorForFilterReverse(op):
            if op.upper() == '&':
                return 'And'
            elif op.upper() == '|':
                return 'Or'

        self.clearQLayoutChildren(self.tagsLay)
        newFilters = copy.deepcopy(self.fieldFilters)
        self.fieldFilters = []
        if not newFilters:
            self.launchFilterChanged()
        for operator, fieldObj in newFilters:
            self.addFieldFilter(fieldObj.interfaceStringWithValue, computeOperatorForFilterReverse(operator), fieldObj)
        
    def addFieldFilter(self, filterString, operator='And', objRel=None):

        def computeOperatorForFilter(op):
            if op.upper() == 'AND':
                return '&'
            elif op.upper() == 'OR':
                return '|'

        if not filterString:
            return 
        hlay = QtGui.QHBoxLayout()
        
        if not objRel:
            objRel = self.lastFieldsQCompleter(filterString)
            if not objRel:
                logging.warning('Unable to find filter for string %r' % (filterString))
                return
            objRel = copy.deepcopy(objRel)  # Copied new filter because if you select the same filter again the value will be overwritten
        

        label = QtGui.QLabel(filterString)
        label.setStyleSheet(constants.TAG_TEXT_STYLE)
        
        removeButton = QtGui.QPushButton('X')
        removeButton.setStyleSheet(constants.BUTTON_STYLE)
        removeButton.setMaximumWidth(30)

        labelOperator = QtGui.QLabel(operator)
        labelOperator.setMaximumWidth(50)
        labelOperator.setAlignment(QtCore.Qt.AlignHCenter)
        
        odooOperator = computeOperatorForFilter(operator)
        
        hlay.setSpacing(0)
        hlay.addWidget(labelOperator)
        hlay.addWidget(label)
        hlay.addWidget(removeButton)
        
        maxFiltersInLine = 4

        tupleCondition = (objRel.name, self.searchMode, objRel.value)
        filterTuple = ('&', objRel)
        objRel.conditionComputedFilter = tupleCondition
        if not self.fieldFilters:
            self.fieldFilters.append(filterTuple)
        else:
            filterTuple = (odooOperator, objRel)
            self.fieldFilters.append(filterTuple)

        childrenWidgetsCount = self.tagsLay.count()
        if childrenWidgetsCount == 0:
            hlayRow = QtGui.QHBoxLayout()
            hlayRow.addLayout(hlay)
            self.tagsLay.addLayout(hlayRow)
            removeButton.clicked.connect(partial(self.removeFieldFilter, filterTuple))
        else:
            rowLay = self.tagsLay.children()[-1]
            rowTagsCount = rowLay.count()
            if rowTagsCount <= maxFiltersInLine:
                rowLay.addLayout(hlay)
                removeButton.clicked.connect(partial(self.removeFieldFilter, filterTuple))
            else:
                hlayRow = QtGui.QHBoxLayout()
                hlayRow.addLayout(hlay)
                self.tagsLay.addLayout(hlayRow)
                removeButton.clicked.connect(partial(self.removeFieldFilter, filterTuple))
        
        self.launchFilterChanged()
    
    def orCondition(self):
        self.addFieldFilter(str(self.linedit.text()), 'Or')
        self.linedit.setText('')

    def removeFieldFilter(self, filterTuple):
        if not filterTuple:
            logging.warning('Unable to remove filter %r because obj not found' % (filterTuple))
            return
        if filterTuple in self.fieldFilters:
            self.fieldFilters.remove(filterTuple)
        self.reloadFilters()

    def launchFilterChanged(self):
        outFilters = []
        for operator, fieldObj in self.fieldFilters:
            outFilters.append(operator)
            outFilters.append(fieldObj.conditionComputedFilter)
        if self.customFilters:
            void = False
            if not outFilters:
                void = True
            for filterCustomObj in self.customFilters:
                outFilters.extend(filterCustomObj.domain)
            if void:
                outFilters = outFilters[1:]
        if self.conditionFilters:
            if outFilters:
                outFilters.append('&')
            for elem in self.conditionFilters:
                if isinstance(elem, str):
                    outFilters.append(elem)
                elif isinstance(elem, FilterObj):
                    outFilters.extend(elem.domain)
                else:
                    logging.warning('[launchFilterChanged] Cannot evaluate element %r' % (elem))
        if self.parent:
            self.parent.filter_changed_signal.emit(outFilters)

    def returnPressedLocal(self):
        timer = QtCore.QTimer()
        self.timers.append(timer)
        timer.timeout.connect(self.delayedAddFieldFilter)
        timer.start(500)

    def delayedAddFieldFilter(self):
        filterText = str(self.linedit.text())
        self.addFieldFilter(filterText)
        self.linedit.setText('')
        for timer in self.timers:
            timer.stop()

    def populateCombo(self, fieldsSearch=[], filters=[], currentVal=''):
        '''
            Populate runtime the QCompleter values for line edit
            @currentVal: Current value digited by user
            @fieldsSearchTemplate: List of field objects
            @filters: List of filter objects
        '''
        stringList = []
        if not fieldsSearch:
            fieldsSearch = self.fieldsSearchTemplate
        if currentVal:  # User have digited something
            for fieldObj in fieldsSearch:
                fieldObjRel = self.lastFieldsQCompleter(currentVal)
                if fieldObjRel: # When user goes down with choices I need to restore correct value because everytime line edit changes it's value
                    return # In this case I break the repopulating of the qcompleter because user is going to choice the correct option
                    #currentVal = fieldObjRel.value  # Take clean field name from field object
                fieldObj.value = currentVal
                fieldObj.interfaceStringWithValue = fieldObj.interfaceString + currentVal + '"'
                stringList.append(fieldObj.interfaceStringWithValue)
        self.filterListModel.setStringList(stringList)

    def textChangedEvent(self, newText=''):
        newText = str(newText)
        if newText:
            self.populateCombo(currentVal=str(newText))

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
        
    def computeFilter(self, elemXml):
        fieldAttributes = elemXml.attrib
        filterObj = FilterObj()
        evalDomain = []
        try:
            evalDomain = eval(fieldAttributes.get('domain', ''))
            evalDomain = self.evaluateCondition(evalDomain)
        except Exception as ex:
            logging.error('Unable to compute domain %r. EX: %r' % (fieldAttributes.get('domain', ''), ex))
        filterObj.domain = evalDomain
        filterObj.string = fieldAttributes.get('string', '')
        filterObj.help = fieldAttributes.get('help', '')
        if filterObj.string:
            self.filters.append(filterObj)
        return filterObj

    def computeField(self, elemXml):
        fieldAttributes = elemXml.attrib
        fieldObj = FieldObj()
        fieldObj.name = fieldAttributes.get('name', '')
        fieldObj.fieldDefinition = self.fieldsNameTypeRel.get(fieldObj.name, {})
        fieldObj.string = fieldAttributes.get('string', fieldObj.fieldDefinition.get('string', ''))
        fieldObj.interfaceString = SEARCH_FOR_STRING % (fieldObj.string)
        self.fieldsSearchTemplate.append(fieldObj)
        return fieldObj

    def computeArch(self):
        if self.arch:
            return self.computeArchRecursion(ElementTree.XML(self.arch))


class CustomQCompleter(QtGui.QCompleter):
    def __init__(self, parent=None):
        super(CustomQCompleter, self).__init__(parent)
        self.local_completion_prefix = ""
        self.source_model = None

    def setModel(self, model):
        self.source_model = model
        super(CustomQCompleter, self).setModel(self.source_model)

    def updateModel(self):
        local_completion_prefix = self.local_completion_prefix

        class InnerProxyModel(QtGui.QSortFilterProxyModel):
            def filterAcceptsRow(self, sourceRow, sourceParent):
                index0 = self.sourceModel().index(sourceRow, 0, sourceParent)
                searchStr = local_completion_prefix.lower()
                modelStr = str(self.sourceModel().data(index0, QtCore.Qt.DisplayRole).toLower())
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
        self.domain = []
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

class FieldObjCustom(object):
    def __init__(self):
        self.string = ''
        self.domain = []
        self.interfaceString = ''
