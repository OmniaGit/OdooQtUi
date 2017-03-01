'''
Created on 9 Feb 2017

@author: dsmerghetto
'''
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *

def window():
   app = QApplication(sys.argv)
   win = QWidget()
   grid = QGridLayout()
    
   for i in range(1,8):
      for j in range(1,8):
         grid.addWidget(QPushButton("B"+str(i)+str(j)),i,j)
   grid.addWidget(QPushButton("aaa"), 5, 1)
   lll = QHBoxLayout()
   line = QLineEdit()
   butt = QPushButton('aaa')
   lll.addWidget(line)
   lll.addWidget(butt)
   grid.addLayout(lll, 5, 2)
            
   win.setLayout(grid)
   win.setGeometry(100,100,200,100)
   win.setWindowTitle("PyQt")
   win.show()
   sys.exit(app.exec_())

if __name__ == '__main__':
   window()