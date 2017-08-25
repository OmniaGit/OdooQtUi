'''
Created on 7 Feb 2017

@author: dsmerghetto
'''

from PyQt4 import QtGui, QtCore
from utils_odoo_conn import utils
from utils_odoo_conn import constants
from objects.fieldTemplate import OdooFieldTemplate


class Binary(OdooFieldTemplate):
    def __init__(self, xmlField, fieldsDefinition, rpc):
        super(Binary, self).__init__(xmlField, fieldsDefinition, rpc)
        self.labelQtObj = False
        self.widgetQtObj = False
        self.currentValue = False
        self.getQtObject()

    def getQtObject(self):
        self.labelQtObj = QtGui.QLabel(self.labelString)
        self.labelQtObj.setStyleSheet(constants.LABEL_STYLE)
        self.widgetQtObj = QtGui.QLineEdit()
        self.widgetQtObj.setToolTip(self.tooltip)
        self.widgetQtObj.editingFinished.connect(self.valueChanged)
        self.widgetQtObj.setStyleSheet(constants.CHAR_STYLE)
        self.buttonEdit = QtGui.QPushButton('Edit')
        self.buttonEdit.setStyleSheet(constants.BUTTON_STYLE_MANY_2_ONE)
        self.buttonClear = QtGui.QPushButton('Clear')
        self.buttonClear.setStyleSheet(constants.BUTTON_STYLE_MANY_2_ONE)
        if self.required:
            utils.setRequiredBackground(self.widgetQtObj, '')
        self.widgetLyQtObject.addWidget(self.widgetQtObj)
        self.widgetLyQtObject.addWidget(self.buttonEdit)
        self.widgetLyQtObject.addWidget(self.buttonClear)
        if self.translatable:
            self.connectTranslationButton()
            self.widgetLyQtObject.addWidget(self.translateButton)

    def valueChanged(self, val):
        print 'To implement valueChanged changed for binary'
        self.valueTemplateChanged()

    def setValue(self, newVal):
        pass
        print 'To implement setValue changed for binary'
#         newVal = eval(unicode(newVal))
#         self.widgetQtObj.setChecked(newVal)
#         self.currentValue = newVal

    def setReadonly(self, val=False):
        super(Binary, self).setReadonly(val)
        self.widgetQtObj.setEnabled(not val)
        if val:
            self.widgetQtObj.setStyleSheet(constants.READONLY_STYLE)
            self.buttonClear.setDisabled(True)
            self.buttonEdit.setDisabled(True)
        else:
            self.buttonClear.setDisabled(False)
            self.buttonEdit.setDisabled(False)
            if self.required:
                utils.setRequiredBackground(self.widgetQtObj, '')
            else:
                self.widgetQtObj.setStyleSheet('background-color:white;')

    def setInvisible(self, val=False):
        super(Binary, self).setInvisible(val)
        self.labelQtObj.setHidden(val)
        self.widgetQtObj.setHidden(val)
        self.buttonClear.setHidden(val)
        self.buttonEdit.setHidden(val)

    @property
    def value(self):
        return self.currentValue

    @property
    def valueInterface(self):
        return self.currentValue

    def eraseValue(self):
        # To clear also datas
        self.setValue('')
        