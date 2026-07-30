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
from PySide6 import QtGui
from PySide6 import QtCore
from PySide6 import QtWidgets
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
        if isinstance(conditionObj, FilterObj) and getattr(conditionObj, 'action', None):
            conditionObj.action.blockSignals(True)
            conditionObj.action.setChecked(False)
            conditionObj.action.blockSignals(False)

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

    def createSearchIcon(self):
        pixmap = QtGui.QPixmap(16, 16)
        pixmap.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        pen = QtGui.QPen(QtGui.QColor('#64748b'), 1.8)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        painter.setPen(pen)
        painter.drawEllipse(3, 3, 7, 7)
        painter.drawLine(9, 9, 13, 13)
        painter.end()
        return pixmap

    def createFilterPillIcon(self, is_filter=True):
        pixmap = QtGui.QPixmap(14, 14)
        pixmap.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        if is_filter:
            # Funnel icon (Purple tone like Odoo)
            painter.setBrush(QtGui.QBrush(QtGui.QColor('#7c3aed')))
            painter.setPen(QtCore.Qt.NoPen)
            path = QtGui.QPainterPath()
            path.moveTo(2, 3)
            path.lineTo(12, 3)
            path.lineTo(8, 7.5)
            path.lineTo(8, 11.5)
            path.lineTo(6, 10)
            path.lineTo(6, 7.5)
            path.closeSubpath()
            painter.drawPath(path)
        else:
            # Layers / Tag icon (Teal tone like Odoo)
            painter.setBrush(QtGui.QBrush(QtGui.QColor('#0d9488')))
            painter.setPen(QtCore.Qt.NoPen)
            path = QtGui.QPainterPath()
            path.moveTo(2, 4)
            path.lineTo(7, 1.5)
            path.lineTo(12, 4)
            path.lineTo(7, 6.5)
            path.closeSubpath()
            painter.drawPath(path)

            path2 = QtGui.QPainterPath()
            path2.moveTo(2, 7.5)
            path2.lineTo(7, 10)
            path2.lineTo(12, 7.5)
            path2.lineTo(7, 9)
            path2.closeSubpath()
            painter.drawPath(path2)
        painter.end()
        return pixmap

    def createCommonLineEdit(self):
        linedit = CustomLineEdit(self)
        linedit.textChanged.connect(self.textChangedEvent)
        linedit.returnPressed.connect(self.returnPressedLocal)
        linedit.setPlaceholderText('Search...')
        return linedit

    def createCommonOrButton(self):
        orButton = QtWidgets.QPushButton('Or')
        orButton.setStyleSheet(constants.SEARCH_OR_BUTTON)
        orShadow = QtWidgets.QGraphicsDropShadowEffect(orButton)
        orShadow.setBlurRadius(18)
        orShadow.setXOffset(0)
        orShadow.setYOffset(4)
        orShadow.setColor(QtGui.QColor(120, 140, 170, 90))
        orButton.setGraphicsEffect(orShadow)
        orButton.clicked.connect(self.orCondition)

        applyButton = QtWidgets.QPushButton('Apply')
        applyButton.setStyleSheet(constants.SEARCH_APPLY_BUTTON)
        applyShadow = QtWidgets.QGraphicsDropShadowEffect(applyButton)
        applyShadow.setBlurRadius(18)
        applyShadow.setXOffset(0)
        applyShadow.setYOffset(4)
        applyShadow.setColor(QtGui.QColor(120, 140, 170, 90))
        applyButton.setGraphicsEffect(applyShadow)
        applyButton.clicked.connect(self.applyCondition)

        removeButton = QtWidgets.QPushButton('X')
        removeButton.setStyleSheet(constants.SEARCH_REMOVE_BUTTON)
        removeShadow = QtWidgets.QGraphicsDropShadowEffect(removeButton)
        removeShadow.setBlurRadius(18)
        removeShadow.setXOffset(0)
        removeShadow.setYOffset(4)
        removeShadow.setColor(QtGui.QColor(120, 140, 170, 90))
        removeButton.setGraphicsEffect(removeShadow)

        return orButton, applyButton, removeButton

    def orCondition(self):
        self.orPressed = True
        lineEditLay = QtWidgets.QHBoxLayout()

        searchBoxContainer = QtWidgets.QWidget()
        searchBoxContainer.setObjectName("searchBoxContainer")
        searchBoxContainer.setStyleSheet("""
            QWidget#searchBoxContainer {
                background-color: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 4px;
                min-height: 28px;
            }
        """)
        searchBoxLay = QtWidgets.QHBoxLayout(searchBoxContainer)
        searchBoxLay.setContentsMargins(6, 2, 6, 2)
        searchBoxLay.setSpacing(4)

        searchIconLabel = QtWidgets.QLabel()
        searchIconLabel.setPixmap(self.createSearchIcon())
        searchIconLabel.setStyleSheet("border: none; background: transparent;")
        searchBoxLay.addWidget(searchIconLabel)

        lineEdit = self.createCommonLineEdit()
        lineEdit.setStyleSheet("background: transparent; border: none; min-height: 22px; padding: 0px;")
        lineEdit.setCompleter(self.completer)
        searchBoxLay.addWidget(lineEdit, 1)

        orButton, applyButton, removeButton = self.createCommonOrButton()
        lineEditLay.addWidget(searchBoxContainer)
        lineEditLay.addWidget(orButton)
        lineEditLay.addWidget(applyButton)
        lineEditLay.addWidget(removeButton)
        removeButton.clicked.connect(partial(self.removeMultyCondition, lineEditLay, lineEdit))
        self.multipleConditionLay.addLayout(lineEditLay)
        self.tmpLayouts.append(lineEditLay)
        self.tmpLineEdits.append(lineEdit)
        lineEdit.selectAll()
        lineEdit.setFocus()

    def computeRecursion(self, xmlElementParent):
        self.mainVLay = QtWidgets.QVBoxLayout()
        self.mainVLay.setSpacing(0)
        self.mainVLay.setContentsMargins(0, 0, 0, 0)
        mainHLay = QtWidgets.QHBoxLayout()
        mainHLay.setSpacing(0)
        mainHLay.setContentsMargins(0, 0, 0, 0)
        self.multipleConditionLay = QtWidgets.QVBoxLayout()
        lineEditLay = QtWidgets.QHBoxLayout()

        # Build inline search box container
        self.searchBoxContainer = QtWidgets.QWidget()
        self.searchBoxContainer.setObjectName("searchBoxContainer")
        self.searchBoxContainer.setStyleSheet("""
            QWidget#searchBoxContainer {
                background-color: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 4px;
                min-height: 28px;
            }
        """)
        searchBoxLay = QtWidgets.QHBoxLayout(self.searchBoxContainer)
        searchBoxLay.setContentsMargins(6, 2, 6, 2)
        searchBoxLay.setSpacing(4)

        # Search Icon Label
        self.searchIconLabel = QtWidgets.QLabel()
        self.searchIconLabel.setPixmap(self.createSearchIcon())
        self.searchIconLabel.setStyleSheet("border: none; background: transparent;")
        searchBoxLay.addWidget(self.searchIconLabel)

        # Inline Tags Layout
        self.tagsLay = QtWidgets.QHBoxLayout()
        self.tagsLay.setContentsMargins(0, 0, 0, 0)
        self.tagsLay.setSpacing(4)
        searchBoxLay.addLayout(self.tagsLay)

        # Setup lineedit inside container
        self.linedit = self.createCommonLineEdit()
        self.tmpLineEdits.append(self.linedit)
        self.linedit.setStyleSheet("background: transparent; border: none; min-height: 22px; padding: 0px;")
        searchBoxLay.addWidget(self.linedit, 1)

        # Setup completer
        self.completer = CustomQCompleter()
        self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.completer.setWrapAround(True)
        self.filterListModel = QtCore.QStringListModel()
        self.computeFieldAndFilters(xmlElementParent)
        self.populateCombo()
        self.completer.setModel(self.filterListModel)
        self.linedit.setCompleter(self.completer)

        lineEditLay.addWidget(self.searchBoxContainer)

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
        plusShadow = QtWidgets.QGraphicsDropShadowEffect(self.buttonPlus)
        plusShadow.setBlurRadius(18)
        plusShadow.setXOffset(0)
        plusShadow.setYOffset(4)
        plusShadow.setColor(QtGui.QColor(120, 140, 170, 90))
        self.buttonPlus.setGraphicsEffect(plusShadow)
        self.buttonPlus.clicked.connect(self.advancedFilter)
        mainHLay.addWidget(self.buttonPlus)

        mainHLay.setSpacing(3)
        self.mainVLay.addLayout(mainHLay)
        return self.mainVLay

    def computeFieldAndFilters(self, xmlElementParent):
        self.toolmenu = QtWidgets.QMenu()
        self._parseFilterElements(xmlElementParent)

    def _parseFilterElements(self, xmlElementParent):
        for childElement in xmlElementParent: #.getchildren():
            childTag = childElement.tag
            if childTag == 'filter':
                filterObj = self.computeFilter(childElement)
                if filterObj and filterObj.string:
                    action = self.toolmenu.addAction(filterObj.string)
                    action.setCheckable(True)
                    filterObj.action = action
                    action.toggled.connect(partial(self.actionSelectionChanged, filterObj))
            elif childTag == 'separator':
                self.toolmenu.addSeparator()
            elif childTag == 'field':   # Values in the line edit
                self.computeField(childElement)
            elif childTag == 'group':   # Recurse into group elements
                self._parseFilterElements(childElement)
            else:
                logging.warning('Tag %r not supported and not evaluated' % (childElement))

    def computeFilter(self, elemXml):
        fieldAttributes = elemXml.attrib
        filterObj = FilterObj()
        evalDomain = []
        try:
            evalGlobals = dict(globals())
            evalGlobals['uid'] = getattr(getattr(getattr(self.parent, 'odooConnector', False), 'rpc_connector', False),
                                         'userId', False)
            evalGlobals['parent'] = self.parent
            evalDomain = eval(fieldAttributes.get('domain', ''), evalGlobals)
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
        self.removeCondition(filterObj)

    def addFilter(self, filterObj):
        if filterObj not in self.globalCondition:
            self.globalCondition.append(filterObj)

    def actionSelectionChanged(self, filterObj, checked=False):
        if not filterObj:
            logging.warning('Filter object not found')
            return
        if checked:
            self.addFilter(filterObj)
        else:
            self.removeFilter(filterObj)
        self.reloadFilters()

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
        if not layout:
            return
        while layout.count() > 0:
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clearQLayoutChildren(item.layout())

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

    def addFieldTag(self, condObj, emit_signal=True):
        is_filter = isinstance(condObj, FilterObj)
        if is_filter:
            display_text = condObj.string or condObj.interfaceString
        else:
            display_text = getattr(condObj, 'intString', str(condObj))

        # Format display text nicely (e.g. Search "Attachment" for: "Req" -> Attachment: Req)
        if display_text.startswith('Search "') and '" for: "' in display_text:
            try:
                parts = display_text.split('" for: "')
                field_part = parts[0].replace('Search "', '')
                val_part = parts[1].rstrip('"')
                display_text = f"{field_part}: {val_part}"
            except Exception:
                pass

        tagWidget = QtWidgets.QWidget()
        if is_filter:
            # Purple theme for Filters
            tagWidget.setStyleSheet("""
                QWidget {
                    background-color: #f3e8ff;
                    border: 1px solid #c084fc;
                    border-radius: 4px;
                }
            """)
        else:
            # Teal theme for Custom Search Tags
            tagWidget.setStyleSheet("""
                QWidget {
                    background-color: #ccfbf1;
                    border: 1px solid #5eead4;
                    border-radius: 4px;
                }
            """)

        tagLay = QtWidgets.QHBoxLayout(tagWidget)
        tagLay.setContentsMargins(4, 1, 4, 1)
        tagLay.setSpacing(4)

        iconLabel = QtWidgets.QLabel()
        iconLabel.setPixmap(self.createFilterPillIcon(is_filter=is_filter))
        iconLabel.setStyleSheet("border: none; background: transparent;")
        tagLay.addWidget(iconLabel)

        textLabel = QtWidgets.QLabel(display_text)
        text_color = "#581c87" if is_filter else "#115e59"
        textLabel.setStyleSheet(f"border: none; background: transparent; color: {text_color}; font-size: 11px; font-weight: bold;")
        tagLay.addWidget(textLabel)

        removeButton = QtWidgets.QPushButton("×")
        removeButton.setCursor(QtCore.Qt.PointingHandCursor)
        removeButton.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
                color: #64748b;
                font-weight: bold;
                font-size: 13px;
                padding: 0px 2px;
                max-width: 14px;
                max-height: 14px;
            }
            QPushButton:hover {
                color: #ef4444;
            }
        """)
        removeButton.clicked.connect(partial(self.removeFieldFilter, condObj))
        tagLay.addWidget(removeButton)

        self.tagsLay.addWidget(tagWidget)
        if emit_signal:
            self.launchFilterChanged()

    def removeFieldFilter(self, conditionObj):
        self.removeCondition(conditionObj)
        self.reloadFilters()

    def reloadFilters(self):
        self.clearQLayoutChildren(self.tagsLay)
        for condObj in self.globalCondition:
            self.addFieldTag(condObj, emit_signal=False)
        self.launchFilterChanged()

    def computeArchRecursion(self, xmlElementParent):
        self.widgetContents = QtWidgets.QWidget()
        self.mainLayOut = QtWidgets.QVBoxLayout()
        self.mainLayOut.setSpacing(1)
        self.mainLayOut.setContentsMargins(1, 1, 1, 1)
        self.filterListLay = QtWidgets.QHBoxLayout()
        self.mainHLayRec = self.computeRecursion(xmlElementParent)
        #self.widgetContents.setStyleSheet('background-color:#ffffff;')
        self.mainLayOut.addLayout(self.mainHLayRec)
        self.mainLayOut.addLayout(self.filterListLay)
        self.widgetContents.setLayout(self.mainLayOut)
        self.outLay = QtWidgets.QVBoxLayout()
        self.outLay.setSpacing(1)
        self.outLay.setContentsMargins(1, 1, 1, 1)
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
        self.andButton.setStyleSheet(constants.ADV_FILTER_ACTION_BUTTON)
        self.orButton = QtWidgets.QPushButton('Filter as Or')
        self.orButton.setStyleSheet(constants.ADV_FILTER_ACTION_BUTTON)
        self.orButton.clicked.connect(self.acceptDialOr)
        applyButton = QtWidgets.QPushButton('Apply')
        applyButton.setStyleSheet(constants.ADV_FILTER_ACTION_BUTTON)
        applyButton.clicked.connect(self.applyCustomFilter)
        cancelButt = QtWidgets.QPushButton('Cancel')
        cancelButt.clicked.connect(self.rejectDial)
        cancelButt.setStyleSheet(constants.ADV_FILTER_CANCEL_BUTTON)

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
        self.dialCustomFilter.setWindowTitle("Advanced Filter")
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
        self.conditionsCustomLay.setContentsMargins(20, 20, 20, 20)
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
        if self.dialCustomFilter.exec() == QtWidgets.QDialog.Accepted:
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
        self.removeButton.setStyleSheet(constants.ADV_FILTER_CANCEL_BUTTON + 'max-height:15px; max-width:7px;height:15px; width:7px;font-weight:bold;')
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
        self.comboCharOperator.setStyleSheet(constants.ADV_FILTER_COMBO_STYLE)
        self.comboBoolOperator.setStyleSheet(constants.ADV_FILTER_COMBO_STYLE)
        self.comboFloatOperator.setStyleSheet(constants.ADV_FILTER_COMBO_STYLE)
        self.comboDatetimeOperator.setStyleSheet(constants.ADV_FILTER_COMBO_STYLE)
        self.mainLineEditWidget.setStyleSheet(constants.ADV_FILTER_LINEEDIT_STYLE)
        self.dateWidget.setStyleSheet(constants.ADV_FILTER_LINEEDIT_STYLE)
        self.datetimeWidget.setStyleSheet(constants.ADV_FILTER_LINEEDIT_STYLE)
        self.integerSpinboxWidget.setStyleSheet(constants.ADV_FILTER_LINEEDIT_STYLE)
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
        self.comboDatetimeValues = list(self.comboFloatValues)
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
        self.mainWidget.setStyleSheet(constants.ADV_FILTER_ROW_BACKGROUND)
        if self.combo.count() > 0:
            self.fieldsCustomComboChanged(self.combo.currentIndex())

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
        if fieldType in ['char', 'many2one', 'text', 'one2many', 'many2many', 'selection']:
            self.comboCharOperator.setHidden(False)
            self.mainLineEditWidget.setHidden(False)
        elif fieldType == 'boolean':
            self.comboBoolOperator.setHidden(False)
        elif fieldType in ['float', 'monetary']:
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
        if fieldType in ['char', 'many2one', 'text', 'one2many', 'many2many', 'selection']:
            return str(self.mainLineEditWidget.text())
        elif fieldType == 'boolean':
            return ''
        elif fieldType == 'date':
            return str(self.dateWidget.date().toPyDate())
        elif fieldType == 'datetime':
            return str(self.datetimeWidget.dateTime().toPyDateTime())
        elif fieldType == 'integer':
            return self.integerSpinboxWidget.value()
        elif fieldType in ['float', 'monetary']:
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
        comboAllFields.setStyleSheet(constants.ADV_FILTER_COMBO_STYLE)

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
        if fieldType in ['char', 'many2one', 'text', 'one2many', 'many2many', 'selection']:
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
        elif fieldType in ['float', 'monetary']:
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
        if key == QtCore.Qt.Key_Return:
            if event.modifiers() & QtCore.Qt.ControlModifier:
                self.parentClass.orCondition()
        return super(CustomLineEdit, self).keyPressEvent(event)
