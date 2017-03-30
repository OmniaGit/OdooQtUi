'''
Created on 29 Mar 2017

@author: dsmerghetto
'''
from PyQt4 import QtGui
import sys

class getlayout(object):
    
    def __init__(self):
        return super(getlayout, self).__init__()
    
    def getLay(self):
        hlay = QtGui.QHBoxLayout()
        
        butt1 = QtGui.QPushButton('primo')
        butt2 = QtGui.QPushButton('secondo')
        butt3 = QtGui.QPushButton('terzo')
        
        hlay.addWidget(butt1)
        hlay.addWidget(butt2)
        hlay.addWidget(butt3)
        
        valy = QtGui.QVBoxLayout()
        
        butt4 = QtGui.QPushButton('quarto')
        valy.addWidget(butt4)
        hlay.addLayout(valy)
        return hlay

app = QtGui.QApplication(sys.argv)

ccc = getlayout()
dialog = QtGui.QDialog()
qtInterface1 = ccc.getLay()
dialog.setLayout(qtInterface1)

dialog.exec_()

print 'fine primo'
dialog = QtGui.QDialog()
qtInterface1 = ccc.getLay()
dialog.setLayout(qtInterface1)

dialog.exec_()

print 'fine secondo'
app.exec_()
