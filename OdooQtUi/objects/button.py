'''
Created on 06 feb 2017

@author: Daniel
'''
import json

from PySide2 import QtGui
from PySide2 import QtWidgets
from OdooQtUi.utils_odoo_conn import utils
from OdooQtUi.utils_odoo_conn import constants
from OdooQtUi.objects.fieldTemplate import OdooFieldTemplate


class Button(OdooFieldTemplate):
    def __init__(self, xmlObject, forceHidden=False):
        super(Button, self).__init__(xmlObject, fieldsDefinition={}, rpc=False)
        self.xmlObject = xmlObject
        self.buttonAttribs = self.xmlObject.attrib
        self.buttonString = self.buttonAttribs.get('string', '')
        self.buttonType = self.buttonAttribs.get('type', '')
        self.buttonName = self.buttonAttribs.get('name', '')
        self.modifiers = json.loads(self.buttonAttribs.get('modifiers', '{}'))
        self.buttonObj = QtWidgets.QPushButton(self.buttonString)
        self.addWidget(self.buttonObj)
        self.invisible = utils.evaluateBoolean(self.buttonAttribs.get('invisible', False))
        self.readonly = utils.evaluateBoolean(self.buttonAttribs.get('readonly', False))
        self.buttonObj.setDisabled(self.readonly)
        if forceHidden:
            self.buttonObj.hide()
        else:
            if self.invisible:
                self.buttonObj.hide()
            else:
                self.buttonObj.show()
        self.invisibleConditions, self.readonlyConditions = utils.evaluateModifiers(self.modifiers)
        self.buttonObj.setStyleSheet(constants.BUTTON_STYLE)
