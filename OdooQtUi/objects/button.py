'''
Created on 06 feb 2017

@author: Daniel
'''
import json

from PySide2 import QtGui
from PySide2 import QtWidgets
#
from OdooQtUi.utils_odoo_conn import utils
from OdooQtUi.utils_odoo_conn import constants
from OdooQtUi.utils_odoo_conn.utilsUi import popError
from OdooQtUi.objects.fieldTemplate import OdooFieldTemplate
#

class Button(OdooFieldTemplate):
    def __init__(self,
                 qtParent,
                 xmlObject,
                 forceHidden=False,
                 model='',
                 odooConnector=False):
        super(Button, self).__init__(qtParent=qtParent,
                                     xmlField=xmlObject,
                                     fieldsDefinition={},
                                     odooConnector=odooConnector)
        self.xmlObject = xmlObject
        self.model=model
        self.buttonAttribs = self.xmlObject.attrib
        self.buttonString = self.buttonAttribs.get('string', '')
        self.buttonType = self.buttonAttribs.get('type', '')
        self.buttonName = self.buttonAttribs.get('name', '')
        self.modifiers = json.loads(self.buttonAttribs.get('modifiers', '{}'))
        self.buttonObj = self.getQtObject()
        self.layout().addWidget(self.buttonObj)
        self.invisible = utils.evaluateBoolean(self.buttonAttribs.get('invisible', False))
        self.readonly = utils.evaluateBoolean(self.buttonAttribs.get('readonly', False))
        self.buttonObj.setDisabled(self.readonly)
        self.buttonObj.clicked.connect(self.buttonClicked)
        if forceHidden:
            self.hide()
        else:
            if self.invisible:
                self.hide()
            else:
                self.show()
        self.invisibleConditions, self.readonlyConditions = utils.evaluateModifiers(self.modifiers)
        self.buttonObj.setStyleSheet(constants.BUTTON_STYLE)

    @property
    def qtObject(self):
        return self.buttonObj

    def getQtObject(self):
        self.buttonObj = QtWidgets.QPushButton(self.buttonString)
        self.buttonObj.setMaximumWidth(200)
        return self.buttonObj

    def setReadonly(self, val=False):
        self.setDisabled(val)

    def setInvisible(self, val=False):
        if val:
            self.hide()
        else:
            self.show()

    def buttonClicked(self):
        try:
            self.odooConnector.callButtonFunction(self.model, self.odooId, self.buttonType, self.buttonName)
            self.parent().loadIds(self.odooId)
        except Exception as ex:
            popError(self, ex)

        
        
        