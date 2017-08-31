'''
Created on 26 ago 2017

@author: daniel
'''
from PyQt4 import QtGui
from PyQt4 import QtCore
import base64
import sys
app = QtGui.QApplication(sys.argv)


def packFile(filePath):
    """
        get a base64 stream of a file
    """
    content = None
    try:
        with open(filePath, "rb") as filedata:
            content = base64.encodestring("".join(filedata.readlines()))
    except Exception, ex:
        raise Exception("PackFile : broken stream on file : %r." % (filePath))
    return content

qdiall = QtGui.QDialog()

lay = QtGui.QVBoxLayout()
imageWidth = 400
imageHeight = 400
newVal = packFile(r'C:\Users\daniel\Desktop\815C.jpg')


widgetQtObj = QtGui.QLabel()
pm = QtGui.QPixmap()
pm.loadFromData(base64.b64decode(newVal))

pm = pm.scaled(imageWidth,
                                 imageHeight,
                                 aspectRatioMode=QtCore.Qt.IgnoreAspectRatio,
                                 transformMode=QtCore.Qt.FastTransformation)
widgetQtObj.setPixmap(pm)


# pixmap = QtGui.QPixmap('')
# newVal = packFile(r'C:\Users\daniel\Desktop\815C.jpg')
# #image = QtGui.QImage()
# byteArray = QtCore.QByteArray()
# byteArray.fromBase64(newVal)
# pixmap.loadFromData(byteArray)
# #pixmap.fromImage(image)
# pixmap = pixmap.scaled(imageWidth,
#                                  imageHeight,
#                                  aspectRatioMode=QtCore.Qt.IgnoreAspectRatio,
#                                  transformMode=QtCore.Qt.FastTransformation)
# widgetQtObj.setPixmap(pixmap)
# widgetQtObj.resize(imageWidth, imageHeight)
#             

lay.addWidget(widgetQtObj)

qdiall.setLayout(lay)
qdiall.exec_()

app.exec_()