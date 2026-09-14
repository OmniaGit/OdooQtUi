# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011-2026 OmniaSolutions and the OdooQtUi contributors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of OdooQtUi, released under the Apache License 2.0.
# Redistributions must keep the attribution in the NOTICE file.
# See the LICENSE and NOTICE files at the root of the project.

'''
Created on 06 feb 2017

@author: Daniel
'''
import json

from PySide6 import QtGui
from PySide6 import QtWidgets
#
from OdooQtUi.RPC.errors import OdooRpcError
from OdooQtUi.utils_odoo_conn import utilsUi
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
        # Odoo 17 and later put an expression here -- `invisible="state !=
        # 'draft'"` -- and stop sending `modifiers` altogether. Kept as it came
        # and evaluated when there is a record to evaluate it against: read now,
        # against nothing, it raises and answers "not hidden", which is why a
        # workflow showed every button in every state.
        self.invisibleExpression = self.buttonAttribs.get('invisible', False)
        self.readonlyExpression = self.buttonAttribs.get('readonly', False)
        self.invisible = utils.evaluateExpression(self.invisibleExpression) \
            if utils.isConstantModifier(self.invisibleExpression) else True
        self.readonly = utils.evaluateExpression(self.readonlyExpression) \
            if utils.isConstantModifier(self.readonlyExpression) else False
        self.buttonObj.setDisabled(self.readonly)
        self.buttonObj.clicked.connect(self.buttonClicked)
        # One whose visibility depends on the record starts hidden and is shown
        # when the record has been read. Showing it first and taking it away is
        # how a user comes to click something that was never theirs to click.
        if forceHidden or self.invisible:
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

    @utilsUi.rpcErrorBoundary
    def buttonClicked(self):
        try:
            self.odooConnector.callButtonFunction(self.model, self.odooId, self.buttonType, self.buttonName)
            self.parent().loadIds(self.odooId)
        except OdooRpcError:
            raise           # told by rpcErrorBoundary, with what Odoo said
        except Exception as ex:
            popError(self, ex)

        
        
        