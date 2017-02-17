'''
Created on 06 feb 2017

@author: Daniel
'''
from PyQt4 import QtGui
from utils import utils
from utils import constants
import json


class Button(object):
    def __init__(self, xmlObject):
        self.xmlObject = xmlObject
        self.buttonAttribs = self.xmlObject.attrib
        self.buttonString = self.buttonAttribs.get('string', '')
        self.buttonType = self.buttonAttribs.get('type', '')
        self.buttonName = self.buttonAttribs.get('name', '')
        self.modifiers = json.loads(self.buttonAttribs.get('modifiers', '{}'))
        self.buttonObj = self.getQtObject()
        self.invisible = utils.evaluateBoolean(self.buttonAttribs.get('invisible', False))
        self.readonly = utils.evaluateBoolean(self.buttonAttribs.get('readonly', False))
        self.buttonObj.setDisabled(self.readonly)
        self.buttonObj.setHidden(self.invisible)
        self.invisibleConditions, self.readonlyConditions = utils.evaluateModifiers(self.modifiers)
        self.buttonObj.setStyleSheet(constants.BUTTON_STYLE)
        return super(Button, self).__init__()

    @property
    def qtObject(self):
        return self.buttonObj

    def getQtObject(self):
        self.buttonObj = QtGui.QPushButton(self.buttonString)
        self.buttonObj.setMaximumWidth(200)
        return self.buttonObj

    def setReadonly(self, val=False):
        self.buttonObj.setDisabled(val)

    def setInvisible(self, val=False):
        self.buttonObj.setHidden(val)
