'''
Created on 3 Feb 2017

@author: Daniel Smerghetto
'''
import xml.etree.cElementTree as ElementTree
from PyQt4 import QtGui
from PyQt4 import QtCore
from functools import partial
from utils_odoo_conn import constants
import logging
import copy


class SearchView(object):

    def __init__(self, arch='', fieldsNameTypeRel={}, parent=False):
        self.arch = arch
        self.parent = parent
        super(SearchView, self).__init__()
        self.filters = []
        self.fieldsSearch = []
        self.timers = []
        self.fieldStringNameRel = {}
        self.fieldsNameTypeRel = fieldsNameTypeRel
        self.changingCurrentText = ''
        self.currentFilters = []

    def computeArchRecursion(self, xmlElementParent):
        widgetContents = QtGui.QWidget()
        mainLay = QtGui.QVBoxLayout()
        filterListLay = QtGui.QHBoxLayout()
        mainHLay = self.computeRecursion(xmlElementParent)
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
        for childElement in xmlElementParent.getchildren():
            childTag = childElement.tag
            if childTag == 'filter':
                self.computeFilter(childElement)
            elif childTag == 'field':
                self.computeField(childElement)
            else:
                logging.warning('Tag %r not supported and not evaluated' % (childElement))
        self.tagsLay = QtGui.QVBoxLayout()
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
        mainHLay.addWidget(self.linedit)
        mainHLay.addWidget(self.searchButton)
        mainHLay.setSpacing(3)
        
        self.mainVLay.addLayout(mainHLay)
        self.mainVLay.addLayout(self.tagsLay)
        return self.mainVLay

    def checkField(self, val):
        for fieldObj in self.fieldsSearch:
            if fieldObj.interfaceString == val:
                return fieldObj
        return False
    
    def checkFilter(self, val):
        for filterObj in self.filters:
            if filterObj.interfaceString == val:
                return filterObj
        return False

    def addFilter(self, filterString, operator='And'):

        def computeOperatorForFilter(op):
            if op.upper() == 'AND':
                return '&'
            elif op.upper() == 'OR':
                return '|'

        newFilter = []
        if not filterString:
            return 
        hlay = QtGui.QHBoxLayout()
        self.fieldsSearch
        objRel = self.checkField(filterString)
        if not objRel:
            objRel = self.checkFilter(filterString)
        if not objRel:
            logging.warning('Unable to find filter for string %r' % (filterString))
            return
        objRel = copy.deepcopy(objRel)  # Copied new filter because if you select the same filter again tha value will be overwritten
#         if 'Search ' not in filterString:
#             filterString = 'Name is ' + filterString
#             newFilter = [newFilter, computeOperatorForFilter(operator), ['name', '=', unicode(filterString)]]
#         else:
#             filterString = filterString.replace('Search ', '').replace(' for: ', ' is ')
#             values = filterString.split('"')
#             value = values[-2]
#             fieldName = self.fieldStringNameRel.get(values[1])
#             newFilter = [newFilter, computeOperatorForFilter(operator), [fieldName, '=', unicode(value)]]
        
        label = QtGui.QLabel(filterString)
        label.setStyleSheet(constants.TAG_TEXT_STYLE)
        
        removeButton = QtGui.QPushButton('X')
        removeButton.setStyleSheet(constants.BUTTON_STYLE)
        removeButton.setMaximumWidth(30)
        
        
        hlay.setSpacing(0)
        hlay.addWidget(label)
        hlay.addWidget(removeButton)
        
        maxFiltersInLine = 4
        
        childrenWidgetsCount = self.tagsLay.count()
        if childrenWidgetsCount == 0:
            hlayRow = QtGui.QHBoxLayout()
            hlayRow.addLayout(hlay)
            self.tagsLay.addLayout(hlayRow)
            removeButton.clicked.connect(partial(self.removeFilter, filterString, label, removeButton, False, objRel))
        else:
            rowLay = self.tagsLay.children()[-1]
            rowTagsCount = rowLay.count()
            if rowTagsCount <= maxFiltersInLine:
                labelOperator = QtGui.QLabel(operator)
                labelOperator.setMaximumWidth(50)
                labelOperator.setAlignment(QtCore.Qt.AlignHCenter)
                rowLay.addWidget(labelOperator)
                rowLay.addLayout(hlay)
                removeButton.clicked.connect(partial(self.removeFilter, filterString, label, removeButton, labelOperator, objRel))
            else:
                hlayRow = QtGui.QHBoxLayout()
                labelOperator = QtGui.QLabel(operator)
                labelOperator.setMaximumWidth(50)
                labelOperator.setAlignment(QtCore.Qt.AlignHCenter)
                rowLay.addWidget(labelOperator)
                hlayRow.addLayout(hlay)
                self.tagsLay.addLayout(hlayRow)
                removeButton.clicked.connect(partial(self.removeFilter, filterString, label, removeButton, labelOperator, objRel))
        
        if not self.currentFilters:
            self.currentFilters.append(objRel)
        else:
            self.currentFilters.append(computeOperatorForFilter(operator))
            self.currentFilters.append(objRel)
        self.launchFilterChanged()
    
    def launchFilterChanged(self):
        if self.parent:
            self.parent.filter_changed_signal.emit(self.currentFilters)

    def orCondition(self):
        self.addFilter(unicode(self.linedit.text()), 'Or')
        self.linedit.setText('')

    def removeFilter(self, filterString, label, removeButton, labelOperator=False, objRel=False):
        if not objRel:
            logging.warning('Unable to remove filter %r because obj not found' % (filterString))
            return
        label.hide()
        removeButton.hide()
        if labelOperator:
            labelOperator.hide()
        if objRel in self.fieldsSearch:
            self.fieldsSearch.remove(objRel)
        elif objRel in self.filters:
            self.filters.remove(objRel)
        if objRel in self.currentFilters:
            if self.currentFilters[0] == objRel:
                self.currentFilters = self.currentFilters[2:]
            else:
                index = self.currentFilters.index(objRel)
                del self.currentFilters[index - 1]   # Remove operator
                del self.currentFilters[index - 1]   # Remove filter

    def returnPressedLocal(self):
        timer = QtCore.QTimer()
        self.timers.append(timer)
        timer.timeout.connect(self.delayedAddFilter)
        timer.start(500)

    def delayedAddFilter(self):
        filterText = unicode(self.linedit.text())
        self.addFilter(filterText)
        self.linedit.setText('')
        for timer in self.timers:
            timer.stop()

    def populateCombo(self, fieldsSearch=[], filters=[], currentVal=''):
        stringList = []
        if not fieldsSearch:
            fieldsSearch = self.fieldsSearch
        if not filters:
            filters = self.filters
        for fieldObj in fieldsSearch:
            strToAppend = fieldObj.string
            if currentVal:
                fieldObjRel = self.checkField(currentVal)
                if fieldObjRel:
                    currentVal = fieldObjRel.value
                else:
                    filterObjRel = self.checkFilter(currentVal)
                    if filterObjRel:
                        currentVal = filterObjRel.value
                strToAppend = 'Search "%s" for: "' % (strToAppend) + currentVal + '"'
                fieldObj.value = currentVal
            else: # Case of first time, user don't have already digited any key, so no choice is available
                continue
            fieldObj.interfaceString = strToAppend
            print fieldObj.interfaceString
            stringList.append(strToAppend)
        # Commented to work only with search fields
#         for filterStr in filters:
#             strToAppend2 = filterStr
#             if currentVal:
#                 strToAppend2 = 'Filter for: %r, %r' % (strToAppend2, currentVal)
#             else:
#                 strToAppend2 = 'Filter for: %r' % (strToAppend2)
#             stringList.append(strToAppend2)
        self.filterListModel.setStringList(stringList)

    def textChangedEvent(self, newText=''):
        newText = unicode(newText)
        if newText:
            self.populateCombo(currentVal=unicode(newText))

    def computeFilter(self, elemXml):
        fieldAttributes = elemXml.attrib
        filterObj = FilterObj()
        filterObj.domain = fieldAttributes.get('domain', '')
        filterObj.string = fieldAttributes.get('string', '')
        filterObj.help = fieldAttributes.get('help', '')
        if filterObj.string:
            self.filters.append(filterObj)

    def computeField(self, elemXml):
        fieldAttributes = elemXml.attrib
        fieldObj = FieldObj()
        fieldObj.name = fieldAttributes.get('name', '')
        fieldObj.string = fieldAttributes.get('string', '')
        fieldObj.fieldDefinition = self.fieldsNameTypeRel.get(fieldObj.name, {})
        if not fieldObj.string:
            fieldObj.string = fieldObj.fieldDefinition.get('string', '')
        self.fieldsSearch.append(fieldObj)
        # self.fieldStringNameRel[fieldString] = fieldName

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
                modelStr = unicode(self.sourceModel().data(index0, QtCore.Qt.DisplayRole).toString().toLower())
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

class FieldObj(object):
    def __init__(self):
        self.string = ''
        self.name = ''
        self.fieldDefinition = {}
        self.interfaceString = ''
        self.value = ''
