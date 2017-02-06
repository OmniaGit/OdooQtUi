'''
Created on 06 feb 2017

@author: Daniel
'''
from PyQt4 import QtGui


class Button(object):
    def __init__(self, xmlObject):
        self.xmlObject = xmlObject
        self.buttonAttribs = self.xmlObject.attrib
        self.buttonString = self.buttonAttribs.get('string', '')
        self.buttonType = self.buttonAttribs.get('type', '')
        self.buttonName = self.buttonAttribs.get('name', '')
        return super(Button, self).__init__()
    
    def getQtObject(self):
        buttonObj = QtGui.QPushButton(self.buttonString)
        return buttonObj