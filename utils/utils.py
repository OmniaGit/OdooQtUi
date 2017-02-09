'''
Created on 20/set/2015

@author: Daniel
'''
from PyQt4 import QtGui
import json
import os
import logging
import sys
import datetime
import traceback
from os.path import expanduser
import stat


try:
    import ImageMath
    import Image
    import win32gui
    import win32con
    import win32api
    import win32ui
    import win32com.client
    from win32com.client import Dispatch
except Exception, ex:
    logging.error('Windows imports cannot be loaded')
    logging.error(ex)
# C:\Users\Daniel\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup

TRY_ICON_OBJ = None
DB_INST = None


def launchTryIconMessage(title, message, level='info'):
    if level.upper() == 'INFO':
        iconMode = 1    # Info
    elif level.upper() == 'WARNING':
        iconMode = 2    # No warning
    elif level.upper() == 'ERROR':
        iconMode = 3    # No critical
    else:
        iconMode = 0    # No icon
    TRY_ICON_OBJ.showMessage(title, message, iconMode)


def startUpEnable(pathFrom, startUpflag=False):
    '''
        C:\Users\Daniel\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\MineSweeper.exe
    '''
    try:
        if not pathFrom:
            return
        objShell = win32com.client.Dispatch("WScript.Shell")
        userMenu = objShell.SpecialFolders("StartMenu")
        pathTo = os.path.join(userMenu, 'Programs\Startup', os.path.basename(str(pathFrom)))
        filename, file_extension = os.path.splitext(pathTo)
        file_extension = file_extension
        linkPath = filename + '.lnk'
        if startUpflag:
            osName = getOS()
            if osName == 'WINDOWS':
                shell = Dispatch('WScript.Shell')
                shortcut = shell.CreateShortCut(linkPath)
                shortcut.Targetpath = pathFrom
                shortcut.WorkingDirectory = os.path.dirname(pathFrom)
                shortcut.IconLocation = pathFrom
                shortcut.save()
            elif osName == 'LINUX':
                pass
                # To try on linux
                # os.symlink(pathFrom, pathTo)
        else:
            if os.path.exists(linkPath):
                os.remove(linkPath)
    except Exception, ex:
        logging.error(ex)


def getBaseVolumeName():
    volumePath = expanduser("~").split(':')[0] + ':\\'
    logging.debug('[getBaseVolumeName] volumePath: %s' % (volumePath))
    return volumePath


def getExeList():
    exeList = []
    if getOS() == 'WINDOWS':
        exeList = getExeFromPath(os.path.join(getBaseVolumeName(), 'Program Files'))
        exeList = exeList + getExeFromPath(os.path.join(getBaseVolumeName(), 'Program Files (x86)'))
    logging.info('[getExeList] exeList: %s' % (exeList))
    return exeList


def getProgramFiles():
    exeList = []
    if getOS() == 'WINDOWS':
        exeList = getExeFromPath(os.path.join(getBaseVolumeName(), 'Program Files'))
    logging.info('[getProgramFiles] exeList: %s' % (exeList))
    return exeList


def getProgramFiles86():
    exeList = []
    if getOS() == 'WINDOWS':
        exeList = getExeFromPath(os.path.join(getBaseVolumeName(), 'Program Files (x86)'))
    logging.info('[getProgramFiles86] exeList: %s' % (exeList))
    return exeList


def getPythonPathExe():
    exeList = []
    pythonExePath = sys.executable
    if os.path.exists(pythonExePath):
        pythonInstallDir = os.path.dirname(pythonExePath)
        exeList = getExeFromPath(pythonInstallDir)
    logging.info('[getPythonPathExe] exeList: %s' % (exeList))
    return exeList


def getExeFromPath(startingPath='', extension='.exe'):
    outExeList = []
    executable = stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH
    if os.path.exists(startingPath):
        for root, _dirnames, filenames in os.walk(startingPath):
            try:
                for filename in filenames:
                    fileCompletePath = str(os.path.join(root, filename))
                    st = os.stat(fileCompletePath)
                    mode = st.st_mode
                    if mode & executable:
                        outExeList.append(fileCompletePath)
            except Exception, ex:
                logging.error('Error during path generation, startingPath:%r' % (startingPath))
                logging.error(ex)
    return outExeList


def distance2(a, b):
    return (a[0] - b[0]) * (a[0] - b[0]) + (a[1] - b[1]) * (a[1] - b[1]) + (a[2] - b[2]) * (a[2] - b[2])


def makeColorTransparent(image, color, thresh2=0):
    image = image.convert("RGBA")
    red, green, blue, alpha = image.split()
    image.putalpha(ImageMath.eval("""convert(((((t - d(c, (r, g, b))) >> 31) + 1) ^ 1) * a, 'L')""",
        t=thresh2, d=distance2, c=color, r=red, g=green, b=blue, a=alpha))
    return image


def getIconPathFromExe(exePath=''):
    try:
        if os.path.exists(exePath):
            exePath = str(exePath)
            ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
            ico_y = win32api.GetSystemMetrics(win32con.SM_CYICON)
            large, small = win32gui.ExtractIconEx(exePath, 0)
            if small and large:
                win32gui.DestroyIcon(small[0])
                hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
                hbmp = win32ui.CreateBitmap()
                hbmp.CreateCompatibleBitmap(hdc, ico_x, ico_y)
                hdc = hdc.CreateCompatibleDC()
                hdc.SelectObject(hbmp)
                hdc.FillSolidRect((0, 0, ico_x, ico_x), 0xffffff)
                hdc.DrawIcon((0, 0), large[0])
                iconsDir = getIconsDirectory()
                bmpIconPath = os.path.join(iconsDir, os.path.basename(exePath).split('.')[0] + '.bmp')
                hbmp.SaveBitmapFile(hdc, bmpIconPath)
                iconPath = os.path.join(iconsDir, os.path.basename(exePath).split('.')[0] + '.png')
                makeColorTransparent(Image.open(bmpIconPath), (255, 255, 255)).save(iconPath)
                return iconPath
            else:
                logMessage('WARNING', 'Filed to generate pixmap from file "%s"' % (exePath))
        else:
            logMessage('WARNING', 'Filed to generate pixmap from file "%s"' % (exePath))
    except Exception, ex:
        logMessage('WARNING', 'Filed to generate pixmap from file "%s"' % (exePath))
        logging.error(ex)
    return ''


def getModulePath():
    currPath = getCurrentPath()
    utilsDir = os.path.dirname(currPath)
    return utilsDir


def computePath(path):
    if os.path.exists(path):
        return path
    else:
        logging.warning('[computePath] path "%s" does not exist.' % (path))
    return ''


def getImagePath(imageName):
    iconsDir = getIconsDirectory()
    return computePath(os.path.join(iconsDir, imageName))

# 
# def getNoImagePath():
#     iconsDir = getIconsDirectory()
#     return computePath(os.path.join(iconsDir, constants.ICON_NO_IMAGE))


def getIconsDirectory():
    """
        Gets icons directory path
    """
    moduleDir = os.path.dirname(os.path.realpath(__file__))
    iconsDir = os.path.join(moduleDir, 'images')       # Path used by packaged version
    if not os.path.exists(iconsDir):
        moduleDir = os.path.dirname(moduleDir)
        iconsDir = os.path.join(moduleDir, 'images')
        if not os.path.exists(iconsDir):
            moduleDir = os.path.dirname(moduleDir)
            iconsDir = os.path.join(moduleDir, 'images')
            if not os.path.exists(iconsDir):
                moduleDir = os.path.dirname(moduleDir)
                iconsDir = os.path.join(moduleDir, 'images')
                if not os.path.exists(iconsDir):
                    return 'False'
    return iconsDir


def getUsefulRandom():
    dataEnv = os.environ.get('APPDATA', None)
    if not dataEnv:
        dataEnv = os.environ.get('PROGRAMFILES', None)
    if not dataEnv:
        dataEnv = getModulePath()
    randomFilePath = os.path.join(dataEnv, 'randomFile.txt')
    return randomFilePath


def getUsefulPath():
    mainDir = getModulePath()
    dirPath = os.path.join(mainDir, 'usefulfiles')
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)
    return dirPath


def getUsefulPython():
    mainDir = getModulePath()
    dirPath = os.path.join(mainDir, 'usefulRunning')
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)
    return dirPath


def getCurrentPath():
    """
       Inizialize all the folder needed for the application
    """
    modulePath = os.path.dirname(__file__)
    splitLibrary = modulePath.split('library.zip')  # This is needed when we use py2exe and the file is zipped in the library.zip
    if len(splitLibrary) > 1:
        modulePath = splitLibrary[0]
    return modulePath


# def askQuestion(labelName):
#     formDial = askForm(labelName)
#     if formDial.exec_() == QtGui.QDialog.Accepted:
#         return True
#     return False


# def askForm(labelName, buttonName=False):
#     return AskFormEdit(labelName, buttonName)


# def getDirectoryFileToSaveSystem(parent):
#     confObjects = DB_INST.getRowsTable(constants.TABLE_NAME_CONFIGURATIONS, fields=['config_value'], filtersList=[('config_name', '=', 'SAVE_SCHREENSHOT_EXTENSION')])
#     filename = QtGui.QFileDialog.getSaveFileName(None, "Save file", "", str(confObjects[0].config_value))
#     logging.info('[getDirectoryFileToSaveSystem] filename: %s' % filename)
#     return filename


def getDirectoryFromSystem(parent, pathToOpen=''):
    return unicode(QtGui.QFileDialog.getExistingDirectory(parent, "Select Directory", pathToOpen))


def getFileFromSystem(desc='Open', startPath='/home/'):
    fileName = QtGui.QFileDialog.getOpenFileName(None, desc, startPath)
    if os.path.exists(fileName):
        return unicode(fileName)
    return ''


# def getSchreenshotDefaultPath():
#     for confObj in DB_INST.getRowsTable(constants.TABLE_NAME_CONFIGURATIONS, ['config_value'], [('config_name', '=', 'SCHREENSHOT_DB_PATH')]):
#         return unicode(confObj.config_value)
#     return ''


def getOS():
    platform = sys.platform
    if 'linux' in platform:
        return 'LINUX'
    elif 'win' in platform or 'nt' in os.name:
        return 'WINDOWS'
    else:
        logging.warning('Os not found: %s' % (platform))
        return 'UNKNOWN'


def launchMessage(message='', msgType='message'):
    logMessage('info', message, 'launchMessage')
    messBox = QtGui.QMessageBox()
    messBox.setText(unicode(message))
    if msgType == 'message':
        messBox.setStandardButtons(QtGui.QMessageBox.Ok)
    elif msgType == 'question':
        messBox.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
    if (messBox.exec_() == QtGui.QMessageBox.Ok):
        messBox.accept()
        return True
    else:
        return False


def logMessage(msgType='DEBUG', message='', functionName=''):
    msg = '%s[%s] %s: %s' % (unicode(datetime.datetime.now()), functionName, unicode(msgType).upper(), message)
    if msgType.upper() == 'DEBUG':
        logging.debug(msg)
    elif msgType.upper() == 'INFO':
        logging.info(msg)
    elif msgType.upper() == 'WARNING':
        logging.warning(msg)
    elif msgType.upper() == 'ERROR':
        logging.error(msg)
    else:
        logging.debug(msg)


def convertJpgToPng(jpgPath, savePngPath=''):
    try:
        if not savePngPath:
            savePngPath = os.path.splitext(jpgPath)[0] + '.png'
        if os.path.exists(jpgPath):
            im = Image.open(jpgPath)
            im.save(savePngPath, 'PNG')
        else:
            logMessage('WARNING', 'Failed to convert image. Jpg %s path does not exists' % (jpgPath))
        if not os.path.exists(savePngPath):
            logMessage('WARNING', 'Failed to convert image. Png %s path does not exists' % (savePngPath))
        return savePngPath
    except Exception, ex:
        logMessage('error', 'Error during converting image: %r' % (ex), 'convertJpgToPng')
        return ''


def exceptionManagement(ex, message=''):
    traceback.print_exc(file=sys.stdout)
    traceBackMess = traceback.format_exc()
    logging.error(ex)
    logging.error(traceBackMess)
    launchMessage(message + ': %s \n %s' % (ex, traceBackMess))


# def setTheme(obj):
#     for elemObj in obj.__dict__.values():
#         setSingleTheme(elemObj)
#     obj.setStyleSheet(constants.BACKGROUND_BASE)
#     iconsDir = getIconsDirectory()
#     mainJpgPath = computePath(os.path.join(iconsDir, constants.ICON_MAIN))
#     icon = QtGui.QIcon(mainJpgPath)
#     obj.setWindowIcon(icon)
# 
# 
# def setThemeInfo(objList):
#     for elemObj in objList:
#         elemObj.setStyleSheet(constants.STYLE_BUTTON_GREEN)
#         if isinstance(elemObj, QtGui.QPushButton):
#             elemObj.setFlat(constants.BUTTONS_FLAT)
# 
# 
# def setSingleTheme(elemObj):
#     if isinstance(elemObj, (QtGui.QPushButton, QtGui.QDialogButtonBox)):
#         elemObj.setStyleSheet(constants.STYLE_BUTTON_GREEN)
#         if isinstance(elemObj, QtGui.QPushButton):
#             elemObj.setFlat(constants.BUTTONS_FLAT)
#     if isinstance(elemObj, (QtGui.QTabWidget)):
#         elemObj.setStyleSheet(constants.BACKGROUND_TABWIDGET)
#     elif isinstance(elemObj, (QtGui.QTextEdit, QtGui.QTextBlock, QtGui.QTreeView, QtGui.QLineEdit, QtGui.QTableView, QtGui.QTableWidget, QtGui.QListView, QtGui.QListWidget, QtGui.QComboBox, QtGui.QSpinBox, QtGui.QDoubleSpinBox)):
#         elemObj.setStyleSheet(constants.BACKGROUND_TABLES)
#     elif isinstance(elemObj, (QtGui.QStatusBar, QtGui.QMenuBar)):
#         elemObj.setStyleSheet('color: rgb(76, 255, 0); font-weight: 900; font: bold 14px;')
#     elif isinstance(elemObj, (QtGui.QMenu)):
#         elemObj.setStyleSheet(constants.BACKGROUND_MENU)
# 
# 
# def translate(strToTranslate=''):
#     try:
#         DB_INST.connection.cursor()
#         if DB_INST and strToTranslate:
#             activeLang = DB_INST.getRowsTable(constants.TABLE_NAME_CONFIGURATIONS, [], [('config_name', '=', 'ACTIVE_LANGUAGE')])
#             for langObj in activeLang:
#                 languageCode = langObj.config_value.split(' - ')[0]
#                 if '\n' in strToTranslate:
#                     strToTranslate = strToTranslate.replace('\n', ' ')
#                 transObj = DB_INST.getRowsTable(constants.TABLE_LANGUAGES, [], [('language_code', '=', languageCode),
#                                                                       ('source', '=', strToTranslate)
#                                                                       ])
#                 if not transObj:
#                     return strToTranslate
#                 else:
#                     return unicode(transObj[0].translated)
#             return strToTranslate
#         return strToTranslate
#     except Exception, ex:
#         logMessage('warning', ex, 'translate')
#         return strToTranslate


def getRowsFromListWidget(listWidget):
    outList = []
    linesCount = listWidget.count()
    for index in range(0, linesCount):
        listItem = listWidget.item(index)
        cellValue = ''
        if listItem:
            cellValue = unicode(listItem.text())
        outList.append(cellValue)
    return outList


def getRowsFromTableWidget(tableWidget, outType='list', headers=[]):
    rowCount = tableWidget.rowCount()
    columnCount = tableWidget.columnCount()
    if outType == 'list':
        outList = []
        for rowIndex in range(0, rowCount):
            rowList = []
            for colIndex in range(0, columnCount):
                tableItem = tableWidget.item(rowIndex, colIndex)
                cellValue = ''
                if tableItem:
                    cellValue = unicode(tableItem.text())
                rowList.append(cellValue)
            outList.append(rowList)
        return outList
    elif outType == 'dict' and headers:
        outDict = {}
        for rowIndex in range(0, rowCount):
            for colIndex in range(0, columnCount):
                colName = headers[colIndex]
                tableItem = tableWidget.item(rowIndex, colIndex)
                cellValue = ''
                if tableItem:
                    cellValue = unicode(tableItem.text())
                    if rowIndex not in outDict:
                        outDict[rowIndex] = {colName: cellValue}
                    else:
                        outDict[rowIndex][colName] = cellValue
        return outDict


def getSelectedRowsFromListWidget(listWidget):
    itemsSelected = listWidget.selectedItems()
    return [unicode(item.text()) for item in itemsSelected]


# def getSelectedRowsFromTableWidget(tableWidget, headers=False, onlyOne=False):
#     if not headers:
#         headers = []
#         for colIndex in range(0, tableWidget.columnCount()):
#             headers.append(unicode(tableWidget.horizontalHeaderItem(colIndex).text()))
#     outDict = {}
#     selectedItems = tableWidget.selectedItems()
#     if onlyOne and len(selectedItems) != 2:
#         launchMessage(translate('Too much rows selected!'), 'warning')
#         return {}
#     for itemIndex in selectedItems:
#         colIndex = itemIndex.column()
#         rowIndex = itemIndex.row()
#         colName = headers[colIndex]
#         itemText = unicode(itemIndex.text())
#         if rowIndex not in outDict:
#             outDict[rowIndex] = {colName: itemText}
#         else:
#             outDict[rowIndex][colName] = itemText
#     return outDict


def commonPopulateTable(headers, values, tableWidget, flags={}):
    '''
        @flags: {'colIndex': flags}
    '''
    outDict = {}
    colCount = len(headers)
    colIndexList = range(0, colCount)
    tableWidget.setColumnCount(colCount)
    tableWidget.setHorizontalHeaderLabels(headers)
    rowPosition = 0
    for menuObj in values:
        tableWidget.setRowCount(rowPosition + 1)
        rowDict = {}
        for colIndex in colIndexList:
            colName = headers[colIndex]
            colVal = menuObj.__dict__.get(colName, '')
            rowDict[colName] = colVal
            twItem = QtGui.QTableWidgetItem(colVal)
            if colIndex in flags:
                twItem.setFlags(flags[colIndex])
            tableWidget.setItem(rowPosition, colIndex, twItem)
        outDict[rowPosition] = rowDict
        rowPosition = rowPosition + 1
    return outDict

def evaluateBoolean(val):
    if isinstance(val, bool):
        return val
    elif isinstance(val, (unicode, str)):
        invisible = eval(val)
        if invisible:
            return True
        return False

def evaluateModifiers(modifiers):
    if isinstance(modifiers, (unicode, str)):
        modifiers = json.loads(modifiers)
    invisibleConditions = modifiers.get('invisible', {})
    readonlyConditions = modifiers.get('readonly', {})
    return invisibleConditions, readonlyConditions

def setRequiredBackground(widgetQtObj):
    widgetQtObj.setStyleSheet('Background-color: rgb(210,210,255)')
    
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    # aaa = getExeFromPath('/home/daniel/eclipse/committers-neon/eclipse/')
    aaa = getExeFromPath('C:\Program Files (x86)')
    app.exec_()
