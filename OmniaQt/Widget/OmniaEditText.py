
##############################################################################
#
#    OmniaSolutions, Your own solutions
#    Copyright (C) 30/ott/2012 OmniaSolutions (<http://www.omniasolutions.eu>). All Rights Reserved
#    info@omniasolutions.eu
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
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
    def __init__(self, parent=None, columName=""):
        """
            init the filter object
        """
        super(OmniaWidgetFilterSql, self).__init__(parent)
        vLayout = QtWidgets.QVBoxLayout(self)

        filterHLayout = QtWidgets.QHBoxLayout()
        self._label = QtWidgets.QLabel(self)
        self._label.setText(columName)
        self._combo = QtWidgets.QComboBox(self)
        self._combo.addItem("=")
        self._combo.addItem("Like")
        self._combo.setCurrentIndex(1)
        self._lineEdit = QtWidgets.QLineEdit(self)
        
        filterHLayout.addWidget(self._label)
        filterHLayout.addWidget(self._combo)
        filterHLayout.addWidget(self._lineEdit)
        vLayout.addItem(filterHLayout)

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

    def setColumn(self, columName):
        """
            set column name
        """
        self._label.setText(columName)

    @property
    def filter(self):
        """
            get the filter of the object
        """
        if str(self._combo.currentText()) == 'Like':
            return "%s %s '%%%s%%'" % (str(self._label.text()),
                                       str(self._combo.currentText()),
                                       str(self._lineEdit.text()))

        return "%s %s %s" % (str(self._label.text()),
                             str(self._combo.currentText()),
                             str(self._lineEdit.text()))

    @property
    def filterTuple(self):
        """
            get the filter of the object as tuple
            (filedname,condition,value)
        """
        return self._label.text(), self._combo.currentText(), self._lineEdit.text()


class OmniaMenuFilterSql(QtWidgets.QMenu):
    def __init__(self, parent=None, columName=""):
        super(OmniaMenuFilterSql, self).__init__(parent)
        self._filter = []
        self._filterTuple = []
        aw = QtWidgets.QWidgetAction(self)
        self.widgetFilterSql = OmniaWidgetFilterSql(columName="")

        self.widgetFilterSql.addEvent += self._addEvent
        self.widgetFilterSql.applyEvent += self._applyEvent
        self.widgetFilterSql.removeEvent += self._removeEvent

        aw.setDefaultWidget(self.widgetFilterSql)
        self.addAction(aw)

        self.addEvent = OmniaEvent()
        self.removeEvet = OmniaEvent()
        self.applyEvent = OmniaEvent()
        self.changed = False

    def _addEvent(self, objFilter):
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

    def setColumn(self, columName, flt):
        """
            set info from the column
        """
        self.widgetFilterSql.setColumn(columName)
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
