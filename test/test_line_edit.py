# import sys
# from PyQt4.QtCore import Qt
# from PyQt4.QtGui import QApplication, QLineEdit
# 
# class LineEdit(QLineEdit):
# 
#     completion_items = [
#         u"hello",
#         u"world"
#         ]
# 
#     def __init__(self, parent = None):
#     
#         QLineEdit.__init__(self, parent)
#     
#     def keyPressEvent(self, event):
#     
#         if event.key() == Qt.Key_Tab:
#             for item in self.completion_items:
#                 if item.startswith(self.text()):
#                     self.setText(item)
#                     break
#             
#             event.accept()
#         else:
#             QLineEdit.keyPressEvent(self, event)
# 
# 
# if __name__ == "__main__":
# 
#     app = QApplication(sys.argv)
#     window = LineEdit()
#     window.show()
#     sys.exit(app.exec_())



# import sys
# from PyQt4.QtCore import Qt
# from PyQt4.QtGui import QApplication, QCompleter, QLineEdit, QStringListModel
# 
# def get_data(model):
#     model.setStringList(["completion", "data", "goes", "here"])
# 
# if __name__ == "__main__":
# 
#     app = QApplication(sys.argv)
#     edit = QLineEdit()
#     completer = QCompleter()
#     edit.setCompleter(completer)
# 
#     model = QStringListModel()
#     completer.setModel(model)
#     get_data(model)
# 
#     edit.show()
#     sys.exit(app.exec_())





from PyQt4.QtCore import *
from PyQt4.QtGui import *

from PyQt4 import QtGui,QtCore

import sys

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)


class MyGui(QDialog): 

    def __init__(self, parent=None): 

        super(MyGui,self).__init__(parent)

        model = QtGui.QStringListModel()
        wordList = ['John Doe','Jane Doe','Albert Einstein', 'Alfred E Newman']
        model.setStringList(wordList)

        layout = QtGui.QVBoxLayout(self)
        self.line = QtGui.QLineEdit(self)
        layout.addWidget(self.line)

        self.combobox = QComboBox(parent)
        layout.addWidget(self.combobox)
        self.combobox.addItems(wordList)
        self.combobox.setEditable(True)

        self.setLayout(layout)

        complete = CustomQCompleter2(self)
        complete.setModel(model)
        complete.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        complete.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        complete.setWrapAround(False)

        self.line.setCompleter(complete)
        self.combobox.setCompleter(complete)
        self.combobox.setEditText('')

        self.setGeometry(200, 100, 400, 300)


class CustomQCompleter2(QCompleter):
    def __init__(self, parent=None):
        super(CustomQCompleter2, self).__init__(parent)
        self.local_completion_prefix = ""
        self.source_model = None

    def setModel(self, model):
        self.source_model = model
        super(CustomQCompleter2, self).setModel(self.source_model)

    def updateModel(self):
        local_completion_prefix = self.local_completion_prefix
        class InnerProxyModel(QSortFilterProxyModel):
            def filterAcceptsRow(self, sourceRow, sourceParent):
                index0 = self.sourceModel().index(sourceRow, 0, sourceParent)
                searchStr = local_completion_prefix.lower()
                modelStr = self.sourceModel().data(index0,Qt.DisplayRole).toString().toLower()
                print searchStr,' in ',modelStr, searchStr in modelStr
                return searchStr in modelStr


        proxy_model = InnerProxyModel()

        proxy_model.setSourceModel(self.source_model)

        super(CustomQCompleter2, self).setModel(proxy_model)
        print 'match :',proxy_model.rowCount()
        cr=QRect(QPoint(1, 1), QSize(1, 1))
        self.complete(cr)


    def splitPath(self, path):
        self.local_completion_prefix = str(path)
        self.updateModel()
        return ""

if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    gui = MyGui()
    gui.show()
    sys.exit(app.exec_())
