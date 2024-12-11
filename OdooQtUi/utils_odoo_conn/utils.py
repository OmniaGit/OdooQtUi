'''
Created on 20/set/2015

@author: Daniel
'''
import os
import sys
import json
import stat
import time
import copy
import base64
import logging
import datetime
import inspect
import subprocess
from os.path import expanduser
from datetime import timedelta
try:
    from traceback import TracebackException
except Exception as ex:
    pass

try:
    from PIL import Image
    from win32com.client import Dispatch
except Exception as ex:
    logging.error('Windows imports cannot be loaded')
    logging.error(ex)
# C:\Users\Daniel\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup

TRY_ICON_OBJ = None
DB_INST = None

getFunctionName = lambda: inspect.stack()[1][3]


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
    '''
    try:
        if not pathFrom:
            return
        osName = getOS()
        if osName != 'WINDOWS':
            logging.warning("OS not supported")
            return
        objShell = Dispatch("WScript.Shell")
        userMenu = objShell.SpecialFolders("StartMenu")
        pathTo = os.path.join(userMenu, 'Programs\Startup', os.path.basename(str(pathFrom)))
        filename, file_extension = os.path.splitext(pathTo)
        file_extension = file_extension
        linkPath = filename + '.lnk'
        if startUpflag:
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(linkPath)
            shortcut.Targetpath = pathFrom
            shortcut.WorkingDirectory = os.path.dirname(pathFrom)
            shortcut.IconLocation = pathFrom
            shortcut.save()
        else:
            if os.path.exists(linkPath):
                os.remove(linkPath)
    except Exception as ex:
        logging.error(ex)


def getBaseVolumeName():
    """
    Get the name of the base volume dist
    :return: <the name>
    """
    volumePath = expanduser("~").split(':')[0] + ':\\'
    logging.debug('[getBaseVolumeName] volumePath: %s' % (volumePath))
    return volumePath


def getExeList():
    """
    Get list of available product executable product 
    :return: [<progrm.exe>,<program2.exe>]
    """
    exeList = []
    if getOS() == 'WINDOWS':
        exeList = getExeFromPath(os.path.join(getBaseVolumeName(), 'Program Files'))
        exeList = exeList + getExeFromPath(os.path.join(getBaseVolumeName(), 'Program Files (x86)'))
    logging.info('[getExeList] exeList: %s' % (exeList))
    return exeList


def getProgramFiles():
    """
    Get program file main folder
    """
    exeList = []
    if getOS() == 'WINDOWS':
        exeList = getExeFromPath(os.path.join(getBaseVolumeName(), 'Program Files'))
    logging.info('[getProgramFiles] exeList: %s' % (exeList))
    return exeList


def getProgramFiles86():
    """
    Get program file main folder (32 Bit)
    :return: [] 
    """
    exeList = []
    if getOS() == 'WINDOWS':
        exeList = getExeFromPath(os.path.join(getBaseVolumeName(), 'Program Files (x86)'))
    logging.info('[getProgramFiles86] exeList: %s' % (exeList))
    return exeList


def getPythonPathExe():
    """
    Get the python binary path
    :return: tipically in windows C:\pythonx.x
    """
    exeList = []
    pythonExePath = sys.executable
    if os.path.exists(pythonExePath):
        pythonInstallDir = os.path.dirname(pythonExePath)
        exeList = getExeFromPath(pythonInstallDir)
    logging.info('[getPythonPathExe] exeList: %s' % (exeList))
    return exeList


def getExeFromPath(startingPath=''):
    """
    Get executable file from path
    :return: [<progrm.exe>,<program2.exe>]
    """
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
            except Exception as ex:
                logging.error('Error during path generation, startingPath:%r' % (startingPath))
                logging.error(ex)
    return outExeList


def distance2(a, b):
    return (a[0] - b[0]) * (a[0] - b[0]) + (a[1] - b[1]) * (a[1] - b[1]) + (a[2] - b[2]) * (a[2] - b[2])


def getModulePath():
    """
    Return the path of the module current module path
    :return: the path
    """
    currPath = getCurrentPath()
    utilsDir = os.path.dirname(currPath)
    return utilsDir


def getImagePath(imageName):
    """
    Get the full path of an image name looking at the pre defined icon/image repository/folder
    :imageName name of the image es. my_image.bmp
    :return: image fill path or empty string if not found
    """
    path = getIconsDirectory()
    if os.path.exists(path):
        return os.path.join(path, imageName)
    return ''


def getIconsDirectory(folder_name='images', curr_file=''):
    """
    Gets icons directory path
    :folder_name Image forlder name 
    :curr_file where to start looking first.. if empty look at __file__
    :return: image directory pth
    """
    if not curr_file:
        curr_file = __file__
    outModuleDir = os.path.dirname(os.path.realpath(curr_file))
    starting_dir = outModuleDir
    iconsDir = os.path.join(outModuleDir, folder_name)       # Path used by packaged version
    if not os.path.exists(iconsDir):
        moduleDir = os.path.dirname(outModuleDir)
        iconsDir = os.path.join(moduleDir, folder_name)
        if not os.path.exists(iconsDir):
            moduleDir = os.path.dirname(moduleDir)
            iconsDir = os.path.join(moduleDir, folder_name)
            if not os.path.exists(iconsDir):
                moduleDir = os.path.dirname(moduleDir)
                iconsDir = os.path.join(moduleDir, folder_name)
    for root, sub_dirs, _files in os.walk(starting_dir):
        for sub_dir in sub_dirs:
            if sub_dir == folder_name:
                iconsDir = os.path.join(root, sub_dir)
                break
    return iconsDir


def getCurrentPath():
    """
    Inizialize all the folder needed for the application
    """
    modulePath = os.path.dirname(__file__)
    splitLibrary = modulePath.split('library.zip')  # This is needed when we use py2exe and the file is zipped in the library.zip
    if len(splitLibrary) > 1:
        modulePath = splitLibrary[0]
    return modulePath


def setupTimeOnFile(timeStamp, toFile, deltaTime=None):
    if not deltaTime:
        deltaTime = timedelta(0)
    if timeStamp:
        try:
            aa = timeStamp.timetuple()
            bb = "%s-%s-%s %s:%s:%s" % (str(aa.tm_year),
                                        str(aa.tm_mon),
                                        str(aa.tm_mday),
                                        str(aa.tm_hour),
                                        str(aa.tm_min),
                                        str(aa.tm_sec))
        except Exception:
            bb = timeStamp
        timeStamp = datetime.datetime.strptime(bb, '%Y-%m-%d %H:%M:%S')
        os.utime(toFile,
                 (time.mktime((timeStamp - deltaTime).timetuple()),
                  time.mktime((timeStamp - deltaTime).timetuple())))

def openByDefaultEditor(path):
    if not path:
        return False
    try:
        if sys.platform.startswith('darwin'):
            subprocess.call(('open', path))
        elif os.name == 'nt':
            os.startfile(path)
        elif os.name == 'posix':
            try:
                subprocess.call(('xdg-open', path))
            except Exception as ex:
                os.system('%s %s' % (os.getenv('EDITOR'), path))
    except Exception as ex:
        logWarning('EX %r' % (ex), 'openByDefaultEditor')
        try:
            toOpen = '"%s"' % (path).encode(sys.getfilesystemencoding())
            logDebug('[openCommon] toOpen: %s' % (toOpen), 'openCommon')
            os.startfile(toOpen)
        except Exception as ex:
            logError('error during opening file with default editor %r' % (ex), 'openByDefaultEditor')
            return False
    return True


def getOS():
    """
    Get the operating system
    :return: 'LINUX' or 'WINDOWS' or 'UNKNOWN'
    """
    platform = sys.platform
    if 'linux' in platform:
        return 'LINUX'
    elif 'win' in platform or 'nt' in os.name:
        return 'WINDOWS'
    else:
        logging.warning('Os not found: %s' % (platform))
        return 'UNKNOWN'


def logDebug(message='', functionName=''):
    logMessage('DEBUG', message, functionName)


def logInfo(message='', functionName=''):
    logMessage('INFO', message, functionName)


def logWarning(message='', functionName=''):
    logMessage('WARNING', message, functionName)


def logError(message='', functionName=''):
    logMessage('ERROR', message, functionName)


def logMessage(msgType='DEBUG', message='', functionName=''):
    msg = '%s[%s] %s' % (str(datetime.datetime.now()), functionName, message)
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
    except Exception as ex:
        logMessage('error', 'Error during converting image: %r' % (ex), 'convertJpgToPng')
        return ''


def getRowsFromListWidget(listWidget):
    outList = []
    linesCount = listWidget.count()
    for index in range(0, linesCount):
        listItem = listWidget.item(index)
        cellValue = ''
        if listItem:
            cellValue = str(listItem.text())
        outList.append(cellValue)
    return outList


def evalValue(val):
    val = str(val)
    try:
        return eval(val)
    except Exception as ex:
        logging.warning(str(ex))
        return val


def removeRowFromTableWidget(tableWidget, rowIndex):
    tableWidget.model().removeRow(rowIndex)


def getRowsFromTableWidget(tableWidget, outType='list', fieldNames=[], rowsIndexesToGet=[]):
    '''
        @outType: 'list' / 'dict'
        @outType: ['field1', 'field2', ...]
    '''
    rowCount = tableWidget.rowCount()
    columnCount = tableWidget.columnCount()
    if outType == 'list':
        outList = []
        rowIndexes = rowsIndexesToGet
        if not rowIndexes:
            rowIndexes = list(range(0, rowCount))
        for rowIndex in rowIndexes:
            rowList = []
            for colIndex in range(0, columnCount):
                tableItem = tableWidget.item(rowIndex, colIndex)
                cellValue = ''
                if tableItem:
                    cellValue = evalValue(tableItem.text())
                rowList.append(cellValue)
            outList.append(rowList)
        return outList
    elif outType == 'dict' and fieldNames:
        outDict = {}
        rowIndexes = rowsIndexesToGet
        if not rowIndexes:
            rowIndexes = list(range(0, rowCount))
        for rowIndex in rowIndexes:
            for colIndex in range(0, columnCount):
                if colIndex >= len(fieldNames):
                    continue
                colName = fieldNames[colIndex]
                tableItem = tableWidget.item(rowIndex, colIndex)
                cellValue = ''
                if tableItem:
                    cellValue = evalValue(tableItem.text())
                    if rowIndex not in outDict:
                        outDict[rowIndex] = {colName: cellValue}
                    else:
                        outDict[rowIndex][colName] = cellValue
        return outDict


def getSelectedRowsFromListWidget(listWidget):
    itemsSelected = listWidget.selectedItems()
    return [str(item.text()) for item in itemsSelected]


def evaluateBoolean(val, context={}):
    if isinstance(val, bool):
        return val
    elif isinstance(val, str):
        try:
            fieldsDict = copy.copy(context)
            invisible = eval(val, fieldsDict)
            if invisible:
                return True
            return False
        except Exception as ex:
            logging.error(ex)
            return False
    elif isinstance(val, (int)):
        if val == 0:
            return False
        else:
            return True
    raise Exception(f"{val} not managed")

def evaluateModifiers(modifiers):
    if isinstance(modifiers, str):
        modifiers = json.loads(modifiers)
    invisibleConditions = modifiers.get('invisible', {})
    readonlyConditions = modifiers.get('readonly', {})
    return invisibleConditions, readonlyConditions


def evaluateContext(contextStr,
                    fieldsDict):
    """
    Avaluate the context with aval function
    This method use a saftry dictionary copi before to be called
     
    :contextStr string to evaluate es: product_id==10
    :fieldsDict dict like key,value of the fields used for the eval funtion
    :return: result of the aval function
    """
    try:
        fieldsDict = copy.copy(fieldsDict)
        return eval(contextStr, fieldsDict)
    except Exception as ex:
        logging.warn("Unable to evaluate %s" % contextStr)
        return {}


def evaluateAttrs(fieldsDict, toCompute, context={}):
    def evalSingleCondition(cond):
        if len(cond) != 3:
            logMessage('warning', 'Condition lenght != 3: %r' % (cond), 'evalSingleCondition')
            return False
        fieldName, operator, valToCompare = cond
        #
        def cleandVal(val, context={}):
            if isinstance(val, str):
                try:
                    val = eval(val)
                except Exception as ex:
                    logging.warn("Unable to eval %s" % val)
            return val
        #
        valToCompare=cleandVal(valToCompare, context)
        headerFieldName='header_'+fieldName
        fieldObj=None
        if fieldName in fieldsDict:
            fieldObj = fieldsDict.get(fieldName, None)
        elif headerFieldName in fieldsDict:
            fieldObj = fieldsDict.get(headerFieldName, None)
        if not fieldObj:
            logMessage('warning', 'No field obj found for name %r' % (fieldName), 'evalSingleCondition')
            return False
        fieldVal = fieldObj.value
        if operator == '=' or operator == '==':
            return fieldVal == valToCompare
        elif operator == '!=':
            return fieldVal != valToCompare
        elif operator == '>':
            if isinstance(fieldVal, list) and isinstance(valToCompare,(int, float)):
                fieldVal=len(fieldVal)
            return fieldVal > valToCompare
        elif operator == '<':
            if isinstance(fieldVal, list) and isinstance(valToCompare,(int, float)):
                fieldVal=len(fieldVal)
            return fieldVal < valToCompare
        elif operator == '>=':
            if isinstance(fieldVal, list) and isinstance(valToCompare,(int, float)):
                fieldVal=len(fieldVal)
            return fieldVal >= valToCompare
        elif operator == '<=':
            if isinstance(fieldVal, list) and isinstance(valToCompare,(int, float)):
                fieldVal=len(fieldVal)
            return fieldVal <= valToCompare
        elif operator == 'in':
            if not isinstance(valToCompare, (list, tuple)):
                logMessage('warning', 'valToCompare: %r is not a list for operator: %r' % (valToCompare, operator), 'evalSingleCondition')
                return False
            return fieldVal in valToCompare
        elif operator == 'not in':
            if not isinstance(valToCompare, (list, tuple)):
                logMessage('warning', 'valToCompare: %r is not a list for operator: %r' % (valToCompare, operator), 'evalSingleCondition')
                return False
            return fieldVal not in valToCompare
        elif operator == 'like':
            if not isinstance(valToCompare, str):
                logMessage('warning', 'valToCompare: %r is not a char for operator: %r' % (valToCompare, operator), 'evalSingleCondition')
                return False
            return fieldVal in valToCompare
        elif operator == 'ilike':
            if not isinstance(valToCompare, str):
                logMessage('warning', 'valToCompare: %r is not a char for operator: %r' % (valToCompare, operator), 'evalSingleCondition')
                return False
            return fieldVal.lower() in valToCompare.lower()
        return False

    if isinstance(toCompute, bool):
        return toCompute
    if len(toCompute) == 1:
        try:
            return evalSingleCondition(toCompute[0])
        except:
            pass

    conditions = []
    operators = []
    for singleCompute in toCompute:
        if isinstance(singleCompute, str):
            if singleCompute == '|':
                operators.append(singleCompute)
                continue
            elif singleCompute == '&':
                operators.append(singleCompute)
                continue
            else:
                logMessage('warning', 'Operator %r not implemented' % (singleCompute), 'evaluateAttrs')
        if not operators:
            operators.append('&')
        try:
            res = evalSingleCondition(singleCompute)
        except Exception as ex:
            pass
        conditions.append(res)

    return _evalSimple(conditions, operators)


def _evalSimple(conditions, operators):
    if len(operators) != len(conditions) - 1:
        logMessage('warning', 'Cannot eval with conditions: %r and operators: %r' % (conditions, operators), '_evalSimple')
        return False
    count = 0
    lastCond = False
    for cond in conditions:
        if count == 0:
            lastCond = cond
        else:
            oper = operators[count - 1]
            if oper == '&':
                lastCond = lastCond and cond
            elif oper == '|':
                lastCond = lastCond or cond
        count = count + 1
    return lastCond


def timeit(method):

    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        logDebug('%2.2f sec, %r' % (te - ts, method.__name__), 'timeit')
        return result

    return timed


def getUserHomeDir():
    return os.path.expanduser("~")


def getLoginFile(app_name='OdooQtUi'):
    home = getUserHomeDir()
    return os.path.join(home, '.%s_trayUserLogin' % (app_name))


def getDebugSeverity():
    home = getUserHomeDir()
    if os.path.join(home,'.odooqtuidebug'):
        return logging.DEBUG
    else:
        return logging.INFO


def writeToFile(dbName, username, userpass, serverIp, serverPort, scheme, connType, dbList=[], app_name='OdooQtUi'):
    toWriteDict = {
        'db_name': dbName,
        'user_name': username,
        'user_pass': userpass,
        'server_ip': serverIp,
        'server_port': serverPort,
        'scheme': scheme,
        'conn_type': connType,
        # 'conn_list': self.availableConnTypes,
        'db_list': dbList,
    }
    toWrite = json.dumps(toWriteDict)
    filePath = getLoginFile(app_name)
    with open(filePath, 'w') as outFile:
        outFile.write(toWrite)


def loadFromFile(app_name='OdooQtUi'):
    dbName = ''
    username = ''
    userpass = ''
    serverIp = ''
    serverPort = ''
    scheme = ''
    connType = ''
    dbList = []
    filePath = getLoginFile(app_name)
    fileDict = {}
    if os.path.exists(filePath):
        with open(filePath, 'r') as readFile:
            content = readFile.read()
            fileDict = json.loads(content)
        if fileDict:
            dbName = fileDict.get('db_name', '')
            username = fileDict.get('user_name', '')
            userpass = fileDict.get('user_pass', '')
            serverIp = fileDict.get('server_ip', '')
            serverPort = fileDict.get('server_port', '')
            scheme = fileDict.get('scheme', '')
            connType = fileDict.get('conn_type', '')
            dbList = fileDict.get('db_list', [])
    return dbName, username, userpass, serverIp, serverPort, scheme, connType, dbList


def html_traceback(exc_value):
    result = ''

    # get previous fails, so errors are appended by order of execution
    if hasattr(exc_value, '__context__') and exc_value.__context__:
        result += html_traceback(exc_value.__context__)

    # convert Exception into TracebackException
    tbe = TracebackException.from_exception(exc_value)

    # get stacktrace (cascade methods calls)
    error_lines = ""
    for frame_summary in tbe.stack:
        summary_details = """
            <hr>
            <b>'filename'</b>: %s<br> 
            <b>'method'  </b>: %s<br>
            <b>'lineno'  </b>: %s<br>
            <b>'code'    </b>: %s<br>
            """ % (frame_summary.filename,
                   frame_summary.name,
                   frame_summary.lineno,
                   frame_summary.line)
        error_lines+= "\n"
        error_lines+= summary_details

    # append error, by order of execution
    result+="""
               <hr>
               <b>'error_lines'</b>: %s<br> 
               <b>'type'       </b>: %s<br>
               <b>'message'    </b>: %s<br>""" % (error_lines,
                                                  tbe.exc_type.__name__,
                                                  str(tbe).replace("\n", "<br>"))
    return result



