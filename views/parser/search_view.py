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


class SearchView(object):

    def __init__(self, arch='', fieldsNameTypeRel={}):
        self.arch = arch
        super(SearchView, self).__init__()
        self.filters = []
        self.fieldsSearch = []
        self.timers = []
        self.fieldStringNameRel = {}
        self.fieldsNameTypeRel = fieldsNameTypeRel
        self.changingCurrentText = ''

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
        self.gridLay = QtGui.QGridLayout()
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
        
        self.searchButton = QtGui.QPushButton('Search')
        self.searchButton.setStyleSheet(constants.BUTTON_STYLE)
        self.searchButton.clicked.connect(self.searchButtClicked)
        mainHLay.addWidget(self.linedit)
        mainHLay.addWidget(self.searchButton)
        mainHLay.setSpacing(3)
        
        self.mainVLay.addLayout(mainHLay)
        self.mainVLay.addLayout(self.gridLay)
        return self.mainVLay

    def addFilter(self, filterString):
        if not filterString:
            return 
        hlay = QtGui.QHBoxLayout()
        filterString = filterString.replace('Search ', '').replace(' for: ', ' is ')
        label = QtGui.QLabel(filterString)
        label.setStyleSheet(constants.TAG_TEXT_STYLE)
        removeButton = QtGui.QPushButton('X')
        # removeButton.setStyleSheet(constants.TAG_BUTTON_STYLE)
        removeButton.setStyleSheet(constants.BUTTON_STYLE)
        removeButton.setMaximumWidth(30)
        removeButton.clicked.connect(partial(self.removeFilter, filterString, label, removeButton))
        
        hlay.setSpacing(0)
        hlay.addWidget(label)
        hlay.addWidget(removeButton)
        
        maxFiltersInLine = 4
        lastRowIndex = self.gridLay.rowCount() - 1
        childrenLenght = len(self.gridLay.children())
        lastColIndex = childrenLenght % maxFiltersInLine
        if lastColIndex == 0 and childrenLenght > 0:
            lastRowIndex = lastRowIndex + 1
        self.gridLay.addLayout(hlay, lastRowIndex, lastColIndex, 1, 1)

    def searchButtClicked(self):
        self.addFilter(unicode(self.linedit.text()))
        self.linedit.setText('')

    def removeFilter(self, filterString, label, removeButton):
        label.hide()
        removeButton.hide()

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
        print 'fieldsSearch: %r, filters: %r, currentVal: %r' % (fieldsSearch, filters, currentVal)
        stringList = []
        if not fieldsSearch:
            fieldsSearch = self.fieldsSearch
        if not filters:
            filters = self.filters
        for fieldString in fieldsSearch:
            strToAppend = fieldString
            if currentVal:
                strToAppend = 'Search %s for: "' % (strToAppend) + currentVal + '"'
            else:
                strToAppend = 'Search for: %s' % (strToAppend)
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
        if newText and (not newText.startswith('Search ') or not newText.startswith('Filter for: ')):
            self.populateCombo(currentVal=unicode(newText))
        print 'Completer index %r' % (self.completer.currentRow())

    def computeFilter(self, elemXml):
        fieldAttributes = elemXml.attrib
        fieldDomain = fieldAttributes.get('domain', '')
        fieldString = fieldAttributes.get('string', '')
        fieldHelp = fieldAttributes.get('help', '')
        if fieldString:
            self.filters.append(fieldString)

    def computeField(self, elemXml):
        fieldAttributes = elemXml.attrib
        fieldName = fieldAttributes.get('name', '')
        fieldString = fieldAttributes.get('string', '')
        fieldDefinition = self.fieldsNameTypeRel.get(fieldName, {})
        fieldStringDefinition = fieldDefinition.get('string', '')
        if fieldString:
            self.fieldsSearch.append(fieldString)
        elif fieldStringDefinition:
            self.fieldsSearch.append(fieldStringDefinition)
        self.fieldStringNameRel[fieldString] = fieldName

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
                # print 'searchStr: %r, modelStr: %r' % (searchStr, modelStr)
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
