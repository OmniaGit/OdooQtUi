'''
Created on 3 Feb 2017

@author: Daniel Smerghetto
'''
import xml.etree.cElementTree as ElementTree
from PyQt4 import QtGui
from PyQt4 import QtCore
import logging


class SearchView(object):

    def __init__(self, arch='', fieldsNameTypeRel={}):
        self.arch = arch
        super(SearchView, self).__init__()
        self.filters = []
        self.fieldsSearch = []
        self.fieldStringNameRel = {}
        self.fieldsNameTypeRel = fieldsNameTypeRel

    def computeArchRecursion(self, xmlElementParent):
        widgetContents = QtGui.QWidget()
        mainVLay = self.computeRecursion(xmlElementParent)
        widgetContents.setStyleSheet('background-color:#ffffff;')
        widgetContents.setLayout(mainVLay)
        outLay = QtGui.QVBoxLayout()
        outLay.addWidget(widgetContents)
        return outLay

    def computeRecursion(self, xmlElementParent):
        mainVLay = QtGui.QHBoxLayout()
        for childElement in xmlElementParent.getchildren():
            childTag = childElement.tag
            if childTag == 'filter':
                self.computeFilter(childElement)
            elif childTag == 'field':
                self.computeField(childElement)
            else:
                logging.warning('Tag %r not supported and not evaluated' % (childElement))
        self.linedit = QtGui.QLineEdit()
        self.linedit.textChanged.connect(self.textChangedEvent)
        self.completer = CustomQCompleter()
        self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.completer.setWrapAround(True)
        self.filterListModel = QtGui.QStringListModel()
        self.populateCombo()
        self.completer.setModel(self.filterListModel)
        self.linedit.setCompleter(self.completer)
        mainVLay.addWidget(self.linedit)
        mainVLay.setSpacing(3)
        return mainVLay

    def populateCombo(self, fieldsSearch=[], filters=[], currentVal=''):
        stringList = []
        if not fieldsSearch:
            fieldsSearch = self.fieldsSearch
        if not filters:
            filters = self.filters
        for fieldString in fieldsSearch:
            strToAppend = fieldString
            if currentVal:
                strToAppend = 'Search %r for: %r' % (strToAppend, currentVal)
            else:
                strToAppend = 'Search for: %r' % (strToAppend)
            stringList.append(strToAppend)
        for filterStr in filters:
            strToAppend2 = filterStr
            if currentVal:
                strToAppend2 = 'Filter for: %r, %r' % (strToAppend2, currentVal)
            else:
                strToAppend2 = 'Filter for: %r' % (strToAppend2)
            stringList.append(strToAppend2)
        self.filterListModel.setStringList(stringList)

    def textChangedEvent(self, newText=''):
        newText = unicode(newText)
        print newText
        if newText and (not newText.startswith('Search ') or not newText.startswith('Filter for: ')):
            self.populateCombo(currentVal=unicode(newText))

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
                print searchStr
                modelStr = self.sourceModel().data(index0, QtCore.Qt.DisplayRole).toString().toLower()
                print modelStr
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
