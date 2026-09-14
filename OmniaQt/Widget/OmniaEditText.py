# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011-2026 OmniaSolutions and the OdooQtUi contributors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of OdooQtUi, released under the Apache License 2.0.
# Redistributions must keep the attribution in the NOTICE file.
# See the LICENSE and NOTICE files at the root of the project.

'''
Created on 30/ott/2012
@author: mboscolo
'''
from PySide6 import QtWidgets
from PySide6 import QtCore 

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

from OmniaQt.util import OmniaEvent


class OmniaLightEditText(QtWidgets.QMenu):
    def __init__(self, parent=None):
        super(OmniaLightEditText, self).__init__(parent)
        aw = QtWidgets.QWidgetAction(self)
        self.qLineEdit = QtWidgets.QLineEdit()
        aw.setDefaultWidget(self.qLineEdit)
        self.addAction(aw)

    def keyPressEvent(self, key):
        if Qt.Key_Escape == key.key():
            self.close()
        elif Qt.Key_Return == key.key():
            self.close()
        super(OmniaLightEditText, self).keyPressEvent(key)

    @property
    def text(self):
        return str(self.qLineEdit.text())

    @text.setter
    def text(self, value):
        self.qLineEdit.setText(str(value))


class OmniaWidgetFilterSql(QtWidgets.QWidget):
    def __init__(self, 
                 parent=None, 
                 columName="",
                 force_type="str"
                 ):
        """
            init the filter object
        """
        super(OmniaWidgetFilterSql, self).__init__(parent)
        vLayout = QtWidgets.QVBoxLayout(self)
        filterHLayout = QtWidgets.QHBoxLayout()#
        self._force_type=force_type
        #
        self._label = QtWidgets.QLabel(self)
        self._label.setText(columName)
        self._combo = QtWidgets.QComboBox(self)
        self._combo.addItem("=")
        self._combo.addItem("Like")
        self._combo.setCurrentIndex(1)
        self._lineEdit = QtWidgets.QLineEdit(self)
        #
        filterHLayout.addWidget(self._label)
        filterHLayout.addWidget(self._combo)
        filterHLayout.addWidget(self._lineEdit)
        vLayout.addItem(filterHLayout)
        #
        buttonHLayOut = QtWidgets.QHBoxLayout()

        self._addButton = QtWidgets.QPushButton(self)
        self._addButton.setText("Add")
        self._removeButton = QtWidgets.QPushButton(self)
        self._removeButton.setText("Remove")
        self._applyButton = QtWidgets.QPushButton(self)
        self._applyButton.setText("Apply")

        buttonHLayOut.addWidget(self._addButton)
        buttonHLayOut.addWidget(self._removeButton)
        buttonHLayOut.addWidget(self._applyButton)
        #
        self._lineEdit.returnPressed.connect(self.applyButtonClick)

        vLayout.addItem(buttonHLayOut)

        self._addButton.clicked.connect(self.addButtonClick)
        self._removeButton.clicked.connect(self.removeButtonClick)
        self._applyButton.clicked.connect(self.applyButtonClick)

        self.addEvent = OmniaEvent()
        self.removeEvent = OmniaEvent()
        self.applyEvent = OmniaEvent()

        self.columnValue = None

    def addButtonClick(self):
        """
            add button click
        """
        self.addEvent(self)

    def removeButtonClick(self):
        """

        """
        self.removeEvent(self)

    def applyButtonClick(self):
        self.applyEvent(self)

    def setColumnValue(self, value):
        self.columnValue = value

    def setColumn(self, 
                  columName,
                  force_type='str'):
        """
            set column name
        """
        self._force_type=force_type
        self._label.setText(columName)

    @property
    def filter(self):
        """
            get the filter of the object
        """
        if self._combo.currentText() == 'Like':
            return f"{self._label.text()} {self._combo.currentText()} '%{self._lineEdit.text()}%'"
        # if self._force_type=="str":
        #     return f"{self._label.text()} {self._combo.currentText()} '{self._lineEdit.text()}'"
        return f"{self._label.text()} {self._combo.currentText()} {self._lineEdit.text()}"

    @property
    def filterTuple(self):
        """
            get the filter of the object as tuple
            (filedname,condition,value)
        """
        return self._label.text(), self._combo.currentText(), self._lineEdit.text()


class OmniaMenuFilterSql(QtWidgets.QMenu):
    def __init__(self, 
                 parent=None, 
                 columName="",
                 force_type='str'
                 ):
        super(OmniaMenuFilterSql, self).__init__(parent)
        self._filter = []
        self._filterTuple = []
        aw = QtWidgets.QWidgetAction(self)
        self.widgetFilterSql = OmniaWidgetFilterSql(columName=columName,
                                                    force_type=force_type)

        self.widgetFilterSql.addEvent += self._addEvent
        self.widgetFilterSql.applyEvent += self._applyEvent
        self.widgetFilterSql.removeEvent += self._removeEvent

        aw.setDefaultWidget(self.widgetFilterSql)
        self.addAction(aw)

        self.addEvent = OmniaEvent()
        self.removeEvet = OmniaEvent()
        self.applyEvent = OmniaEvent()
        self.changed = False

    def _addEvent(self, 
                  objFilter):
        self.changed = True
        self._filter.append(objFilter.filter)
        self._filterTuple.append(objFilter.filterTuple)

    def _applyEvent(self, objFilter):
        self._addEvent(objFilter)
        self.close()

    def _removeEvent(self, objFilter):
        self.reset()
        self.changed = True
        self.close()

    def reset(self):
        """
            reset the value in the filter
        """
        self._filter = []
        self._filterTuple = []
        self.widgetFilterSql._lineEdit.setText("")
        self.changed = False

    def setColumn(self, 
                  columName, 
                  flt,
                  force_type="str"):
        """
            set info from the column
        """
        self.widgetFilterSql.setColumn(columName,
                                       force_type)
        self.widgetFilterSql.setColumnValue(flt)

    def keyPressEvent(self, key):
        if QtCore.Qt.Key_Escape == key.key():
            self.close()
        elif QtCore.Qt.Key_Return == key.key():
            self.close()
        super(OmniaMenuFilterSql, self).keyPressEvent(key)

    @property
    def filter(self):
        return self._filter

    @property
    def filterTuple(self):
        return self._filterTuple

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    app.setStyle('plastique')
    dialog = OmniaMenuFilterSql()
    sys.exit(app.exec())
