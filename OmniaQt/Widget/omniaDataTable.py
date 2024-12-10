from __future__ import print_function
from builtins import str
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
from PySide6 import QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

from OmniaQt.Model.omniaModel import OmniaModel
from OmniaQt.Widget.OmniaEditText import OmniaMenuFilterSql
from OmniaQt.util import OmniaEvent


class OmniaHorizontalHeader(QtWidgets.QHeaderView):
    def __init__(self, parent=None):
        super(OmniaHorizontalHeader, self).__init__(QtCore.Qt.Horizontal, parent=parent)
        self.setSectionsClickable(True)
        self._columnsFilter = {}
        self.filterUpdate = OmniaEvent()

    def contextMenuEvent(self, qContextMenuEvent):
        qPoint = qContextMenuEvent.globalPos()
        contexMenu = OmniaMenuFilterSql(parent=self)
        col = self.logicalIndexAt(qContextMenuEvent.pos())
        headerName = self.model().headerData(col, QtCore.Qt.Horizontal, 111)
        contexMenu.setColumn(headerName, self._columnsFilter.get(col, []))
        contexMenu.exec_(qPoint)
        if contexMenu.changed:
            if(len(contexMenu.filter)) > 0:
                self._columnsFilter[col] = contexMenu
            else:
                if col in self._columnsFilter:
                    del self._columnsFilter[col]
            self.filterUpdate(self)

    def drawFliter(self, painter, x, y, h, w):
        """
            draw filter
        """
        p = self.palette()
        origPen = painter.pen()
        newPen = QtGui.QPen()

        newPen.setColor(p.window().color().darker(150))
        newPen.setWidth(1.8)

        gradient = QtGui.QLinearGradient(0, 0, 0, h * 2)
        gradient.setColorAt(0.0, p.window().color().darker(200))
        gradient.setColorAt(1.0, p.highlight().color().darker(200))

        painter.setBrush(QtGui.QBrush(gradient))
        painter.setPen(newPen)

        poligonPoints = [QtCore.QPointF(x, y),
                         QtCore.QPointF(x + w, y),
                         QtCore.QPointF(x + w * (0.98), y + (h * 0.15)),
                         QtCore.QPointF(x + w - (w * 0.35), y + h * 0.3),
                         QtCore.QPointF(x + w - (w * 0.35), h),
                         QtCore.QPointF(x + (w * 0.35), h * (0.95)),
                         QtCore.QPointF(x + (w * 0.35), y + h * 0.3),
                         QtCore.QPointF(x + (w * 0.02), y + (h * 0.15)),
                         QtCore.QPointF(x, y)]
        p = QtGui.QPolygonF(poligonPoints)
        painter.drawPolygon(p)
        painter.setPen(origPen)

    def paintSection(self, painter, rect, logicalIndex):
        p = self.palette()
        x = rect.x()
        y = rect.y()
        h = rect.height()
        w = rect.width()
        r = QtCore.QRect(x, y, w - 2, h)
        gradient = QtGui.QLinearGradient(0, 0, 0, h * 2)
        gradient.setColorAt(0.0, p.window().color())
        gradient.setColorAt(1.0, p.highlight().color())
        path = QtGui.QPainterPath()
        path.addRoundedRect(r, 2, 2)
        painter.setBrush(QtGui.QBrush(gradient))
        painter.fillPath(path, QtGui.QBrush(gradient))
        headerValue = self.model().headerData(logicalIndex, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
        rt = QtCore.QRect(x + 30, y + 2, w - 36, h - 4)
        painter.drawText(rt, 0, headerValue)
        if logicalIndex in self._columnsFilter:
            self.drawFliter(painter, x + 4, y + 10, 25, 18)


class OmniaTableView(QtWidgets.QTableView):
    def __init__(self, parent=None):
        super(OmniaTableView, self).__init__(parent)
        self.setSortingEnabled(True)
        self.setHorizontalHeader(OmniaHorizontalHeader())
        self.horizontalHeader().filterUpdate = self.filetrChange
        self.computeFilter = OmniaEvent()
        self.computeFilterObj = OmniaEvent()
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

    def filetrChange(self, objeFilters):
        filterDict = objeFilters._columnsFilter

        def convertToOr(filterList):
            out = ''
            for f in filterList:
                if len(f) > 0:
                    if out == '':
                        out = f
                    else:
                        out = out + ' or ' + f
            return out
        outFilter = ''
        for columnList in list(filterDict.values()):
            rowFilter = convertToOr(columnList.filter)
            if len(str(rowFilter).strip()) > 0:
                if len(outFilter) == 0:
                    outFilter = rowFilter
                else:
                    outFilter = outFilter + ' and ' + rowFilter
        self.computeFilter(outFilter)
        self.computeFilterObj(objeFilters)

    def populateModel(self):
        self.model = OmniaModel(self.data, self.header)
        self.proxyModel = QtCore.QSortFilterProxyModel()
        self.proxyModel.setSourceModel(self.model)
        self.proxyModel.setSortCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.setModel(self.proxyModel)
        self.horizontalHeader().setStretchLastSection(True)


class OmniaDataTable(QtWidgets.QWidget):
    def __init__(self, parent=None, header=[], data=[]):
        super(OmniaDataTable, self).__init__(parent)
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.tableObj = OmniaTableView(self)
        self.tableObj.setObjectName(_fromUtf8('tableObj'))
        self.tableObj.header = header
        self.tableObj.data = data
        self.tableObj.populateModel()
        self.verticalLayout.addWidget(self.tableObj)
        self.confirmEvent = OmniaEvent()
        self.tableObj.doubleClicked.connect(self._confirmEvent)

    def changed(self):
        """
            mark changed
        """
        self._changed = True

    def _confirmEvent(self):
        """
            Confirm event made on double click on the view
        """
        self.confirmEvent(self.firstSelectedRow)

    @property
    def firstSelectedRow(self):
        for index in self.tableObj.selectedIndexes():
            return self.tableObj.proxyModel.mapToSource(index).row()
        return -1

    @property
    def selectedRows(self):
        """
            return a rows selected
        """
        out = []
        columnSelected = []
        for index in self.tableObj.selectedIndexes():
            row = index.row()
            if row not in columnSelected:
                columnSelected.append(row)
        for row in columnSelected:
            out.append(self.tableObj.model.getRowData(row))
        return out

    @property
    def selectedRow(self):
        for index in self.tableObj.selectedIndexes():
            row = index.row()
            return self.tableObj.model.getRowData(row)
        return None

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    app.setStyle('plastique')
    dialog = QDialog()
    verticalLayout = QtWidgets.QVBoxLayout(dialog)
    header = ['name', 'description', 'wherever']
    data = [['pippo', 'pluto', 'rrrr'],
            ['pppp', 'aaaaaa', 'fff']]

    def cc(elementSelected):
        print("element selected", elementSelected)
    w = OmniaDataTable(dialog, header=header, data=data)
    w.confirmEvent += cc
    verticalLayout.addWidget(w)
    dialog.exec_()
    print("sr", w.selectedRow)
    sys.exit(app.exec_())
