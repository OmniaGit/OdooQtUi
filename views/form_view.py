'''
Created on 3 Feb 2017

@author: Daniel Smerghetto
'''
import xml.etree.ElementTree as ElementTree
import utilsView
from PyQt4 import QtGui


class FormView(object):
    def __init__(self, arch, fieldsNameTypeRel):
        self.arch = arch
        self.fieldsNameTypeRel = fieldsNameTypeRel
        self.globalMapping = {}

    def computeArchRecursion(self, parent):
        mainVLay = QtGui.QVBoxLayout()
        for childElement in parent:
            childTag = childElement.tag
            if childTag == 'sheet':
                sheetLay = QtGui.QVBoxLayout()
                layout = self.computeArchRecursion(childElement)
                if layout:
                    sheetLay.addLayout(layout)
            elif childTag == 'header':
                mapping, layout = utilsView.computeHeader(childElement, self.fieldsNameTypeRel)
                if layout:
                    mainVLay.addLayout(layout)
                if mapping:
                    self.globalMapping.update(mapping)
            elif childTag == 'div':
                self.computeArchRecursion(childElement)
            elif childTag == 'group':
                self.computeArchRecursion(childElement)
            elif childTag == 'field':
                fieldObj = utilsView.computeField(childElement, self.fieldsNameTypeRel)
        return mainVLay

    def computeArch(self):
        if self.arch:
            etreeObj = ElementTree.fromstring(self.arch)
            return self.computeArchRecursion(etreeObj)

    def loadIds(self, odooIds):
        for odooId in odooIds:
            pass
            break
