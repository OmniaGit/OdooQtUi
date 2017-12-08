'''
Created on 7 Feb 2017

@author: dsmerghetto
'''
import json

from PyQt4 import QtGui, QtCore
from OdooQtUi.utils_odoo_conn import utils, utilsUi
from OdooQtUi.utils_odoo_conn import constants
from functools import partial
from OdooQtUi.objects.fieldTemplate import OdooFieldTemplate
from OdooQtUi.RPC.rpc import connectionObj
import base64


class One2many(OdooFieldTemplate):
    def __init__(self, xmlField, fieldsDefinition, rpc, odooConnector=None):
        super(One2many, self).__init__(xmlField, fieldsDefinition, rpc)
        self.labelQtObj = False
        self.widgetQtObj = False
        self.treeViewObj = False
        self.odooConnector = odooConnector
        self.relation = self.fieldPyDefinition.get('relation', '')
        self.canCreate = json.loads(self.fieldXmlAttributes.get('can_create', 'true'))
        self.canWrite = json.loads(self.fieldXmlAttributes.get('can_write', 'true'))
        self.odooWidgetType = self.fieldXmlAttributes.get('widget', '')
        self.mainLay = QtGui.QVBoxLayout()
        self.evaluatedIds = {}
        self.currentValue = []
        self.messaggesLay = QtGui.QVBoxLayout()
        if self.odooWidgetType == 'mail_followers':
            self.widgetLyQtObject = QtGui.QVBoxLayout()
            self.treeViewObj = QtGui.QWidget()
        elif self.odooWidgetType == 'mail_thread':
            self.widgetLyQtObject = QtGui.QVBoxLayout()
            self.treeViewObj = QtGui.QWidget()
        else:
            self.treeViewObj = self.odooConnector.initTreeListViewObject(odooObjectName=self.relation,
                                                                         viewName='',
                                                                         view_id=False,
                                                                         rpcObj=self.rpc,
                                                                         activeLanguage='',
                                                                         viewCheckBoxes={},
                                                                         viewFilter=False)
        self.getQtObject()

    def getQtObject(self):
        if self.odooWidgetType == 'mail_followers':
            self.followersButton = QtGui.QPushButton('Show Followers')
            self.followersButton.setStyleSheet(constants.BUTTON_STYLE)
            self.followersButton.clicked.connect(self.showFollowers)
            self.followersOpened = False
            self.widgetLyQtObject.addWidget(self.followersButton)
            self.widgetLyQtObject.addLayout(self.messaggesLay)
            self.widgetLyQtObject.addSpacerItem(QtGui.QSpacerItem(100,100, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))
        elif self.odooWidgetType == 'mail_thread':
            self.messaggesButton = QtGui.QPushButton('Show Chatter')
            self.messaggesButton.setStyleSheet(constants.BUTTON_STYLE + 'width:900%;')
            self.messaggesButton.clicked.connect(self.showMessagges)
            self.widgetLyQtObject.addWidget(self.messaggesButton)
            self.widgetLyQtObject.addLayout(self.messaggesLay)
            self.widgetLyQtObject.addSpacerItem(QtGui.QSpacerItem(20,20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))
        else:
            buttonsLay = QtGui.QHBoxLayout()
            self.labelQtObj = QtGui.QLabel(self.labelString)
            self.labelQtObj.setStyleSheet(constants.LABEL_STYLE)
            buttonsLay.addWidget(self.labelQtObj)
            self.createButt = QtGui.QPushButton('Create')
            self.createButt.setStyleSheet(constants.BUTTON_STYLE)
            buttonsLay.addWidget(self.createButt)
            self.createButt.clicked.connect(self.createAndAdd)
            buttonsLay.addSpacerItem(QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))
            self.mainLay.addLayout(buttonsLay)

    def showFollowers(self):
        self.followersButton.setHidden(True)
        if not self.followersOpened:
            lay = QtGui.QHBoxLayout()
            self.followButton = QtGui.QPushButton('UnFollowing')
            self.followButton.clicked.connect(self.followClicked)
            self.setUnfolloWingButton()
            lay.addWidget(self.followButton)
            self.buttonFollowersCount = QtGui.QToolButton()
            self.buttonFollowersCount.setText(unicode(len(self.currentValue)))
            self.toolmenu = QtGui.QMenu()
            res = self.populateMenu()
            for obj in res:
                currentPartnerId, _partnerName = self.getPartnerIdFromUserId()
                partnerRes = obj.get('partner_id')
                if partnerRes and partnerRes[0] == currentPartnerId:
                    self.setFollowingButton()
            self.buttonFollowersCount.setMenu(self.toolmenu)
            self.buttonFollowersCount.setPopupMode(QtGui.QToolButton.InstantPopup) 
            self.buttonFollowersCount.setStyleSheet(constants.BUTTON_STYLE)
            lay.addWidget(self.buttonFollowersCount)
            self.messaggesLay.addLayout(lay)
        else:
            pass

    def populateMenu(self):
        followerAction = self.toolmenu.addAction('Add Followers')
        followerAction.changed.connect(self.addFollower)
        channelAction = self.toolmenu.addAction('Add Channels')
        channelAction.changed.connect(self.addChannel)
        self.toolmenu.addSeparator()
        res = connectionObj.read(self.relation, [], self.currentValue)
        for elem in res:
            name = elem.get('display_name', '') or ''
            if not name or name == 'False':
                vals = elem.get('channel_id', ['', ''])
                if vals:
                    name = 'Channel: ' + vals[-1]
            else:
                name = 'User: ' + name
            act = self.toolmenu.addAction(name)
            act.setCheckable(True)
            act.setChecked(True)
            act.toggled.connect(partial(self.removeFollowerChannel, elem.get('id')))
        return res

    def addFollower(self):
        utils.logMessage('warning', 'Not implemented add follower', 'addFollower')
    
    def addChannel(self):
        utils.logMessage('warning', 'Not implemented add channel', 'addChannel')

    def removeFollowerChannel(self, resId):
        if resId:
            connectionObj.write(self.parentModel, {self.fieldName: [(2, resId, False)]}, self.parentId)
            self.currentValue.remove(resId)
            self.toolmenu.clear()
            self.populateMenu()
            self.buttonFollowersCount.setText(unicode(len(self.currentValue)))
            currentPartnerId, _partnerName = self.getPartnerIdFromUserId()
            if self.parentId == currentPartnerId:
                self.setFollowingButton()
            else:
                self.setUnfolloWingButton()

    def setUnfolloWingButton(self):
        self.followButton.setText('UnFollowing')
        self.followButton.setStyleSheet(constants.BUTTON_STYLE + 'background-color: red;')

    def setFollowingButton(self):
        self.followButton.setText('Following')
        self.followButton.setStyleSheet(constants.BUTTON_STYLE)
        
    def _addFollower(self, partnerId):
        if partnerId:
            values = {'res_model': self.parentModel,
                      'partner_id': partnerId,
                      'res_id': self.parentId[0]}
            resId = connectionObj.create(self.relation, values)
            connectionObj.write(self.parentModel, {self.fieldName: [(4, resId, False)]}, self.parentId)
            self.currentValue.append(resId)
            self.toolmenu.clear()
            self.populateMenu()
            self.buttonFollowersCount.setText(unicode(len(self.currentValue)))
            self.setFollowingButton()

    def getPartnerIdFromUserId(self, userId=False):
        if not userId:
            userId = connectionObj.userId
        partnerId, partnerName = False, ''
        res = connectionObj.read('res.users', ['partner_id'], userId)
        for elem in res:
            partnerId, partnerName = elem.get('partner_id', [False, ''])
        return partnerId, partnerName
        
    def followClicked(self):
        currText = unicode(self.followButton.text())
        partnerId, _partnerName = self.getPartnerIdFromUserId()
        if partnerId:
            if currText == 'Following':
                res = connectionObj.search(self.relation, [('partner_id', '=', partnerId), ('res_id', '=', self.parentId)])
                for objId in res:
                    self.removeFollowerChannel(objId)
            else:
                self._addFollower(partnerId)
        
    def showMessagges(self):
        self.messaggesButton.setEnabled(False)
        self.messaggesButton.setStyleSheet(constants.BUTTON_STYLE + 'width:900%; background-color: #d3d0d0;')
        messages = connectionObj.read(self.relation, [], self.currentValue)
        for messageDict in messages:
            _userId, userName = messageDict.get('author_id', [False, ''])
            bodyMessage = messageDict.get('body', '')
            write_date = messageDict.get('write_date', '')
            attachment_ids = messageDict.get('attachment_ids', [])
            
            labelUser = QtGui.QLabel(userName)
            labelDate = QtGui.QLabel(write_date)
            labelBody = QtGui.QTextEdit()
            labelBody.setFrameShape(QtGui.QFrame.NoFrame)
            labelBody.setText(bodyMessage)
            labelBody.setReadOnly(True)
            
            hlayUser = QtGui.QHBoxLayout()
            hlayUser.addWidget(labelUser)
            hlayUser.addWidget(labelDate)
            
            mainVLay = QtGui.QVBoxLayout()
            mainVLay.addLayout(hlayUser)
            mainVLay.addWidget(labelBody)
            
            attachmentLay = QtGui.QHBoxLayout()
            if attachment_ids:
                res = connectionObj.read('ir.attachment', ['datas'], attachment_ids)
                for attachDict in res:
                    imageLay = QtGui.QVBoxLayout()
                    labelImage = utilsUi.getQtImageFromContent(attachDict.get('datas', ''), imageWidth=120, imageHeight=120)
                    imageLay.addWidget(labelImage)
                    buttonDownloadImage = QtGui.QPushButton('Download')
                    buttonDownloadImage.setStyleSheet(constants.BUTTON_STYLE + 'max-width: 100px;')
                    buttonDownloadImage.clicked.connect(partial(self.downloadImage, attachDict.get('datas', '')))
                    imageLay.addWidget(buttonDownloadImage)
                    attachmentLay.addLayout(imageLay)
                attachmentLay.addSpacerItem(QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))
            mainVLay.addLayout(attachmentLay)
            mainWidget = QtGui.QWidget()
            mainWidget.setLayout(mainVLay)
            labelUser.setStyleSheet('font-weight: bold;')
            mainWidget.setStyleSheet('background-color: #cccbcb;')
            self.messaggesLay.addWidget(mainWidget)

    def downloadImage(self, content):
        fileCleanContent = base64.b64decode(content)
        filePath = utilsUi.getDirectoryFileToSaveSystem(None, fileType='*.png')
        if filePath:
            with open(filePath, 'w') as writeFile:
                writeFile.write(fileCleanContent)
            utils.openByDefaultEditor(filePath)
        
    def createAndAdd(self):
        try:
            def acceptDial():
                dialog.accept()
    
            def rejectDial():
                dialog.reject()
    
            dialog = QtGui.QDialog()
            mainLay = QtGui.QVBoxLayout()
            viewObjForm = self.odooConnector.initFormViewObj(self.relation, rpcObj=self.rpc)
            mainLay.addWidget(viewObjForm)
            dialog.setStyleSheet(constants.VIOLET_BACKGROUND)
            dialog.resize(1200, 600)
            dialog.move(100, 100)
            buttLay, okButt, cancelButt = utilsUi.getButtonBox('right')
            mainLay.addLayout(buttLay)
            dialog.setLayout(mainLay)
            okButt.clicked.connect(acceptDial)
            cancelButt.clicked.connect(rejectDial)
            okButt.setStyleSheet(constants.BUTTON_STYLE_OK)
            cancelButt.setStyleSheet(constants.BUTTON_STYLE_CANCEL)
            dialog.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
            utilsUi.setLayoutMarginAndSpacing(mainLay)
            if dialog.exec_() == QtGui.QDialog.Accepted:
                fieldVals = viewObjForm.getAllFieldsValues()
                objId = self.rpc.create(self.relation, fieldVals)
                if objId:
                    self.currentValue.append(objId)
                    self.setValue(self.currentValue)
        except Exception, ex:
            utils.logMessage('error', '%r' % (ex), 'createAndAdd')

    def computeFieldVal(self, val):
        outStrVal = ''
        if isinstance(val, (list, tuple)):
            _objId, outStrVal = val
        elif isinstance(val, bool):
            outStrVal = ''
        elif isinstance(val, int):
            outStrVal = ''
        elif isinstance(val, (str, unicode, QtCore.QString)):
            outStrVal = unicode(val)
        return outStrVal

    def setValue(self, relIds):
        self.currentValue = relIds
        if self.odooWidgetType == 'mail_followers':
            return 
        elif self.odooWidgetType == 'mail_thread':
            return 
        else:
            self.treeViewObj.loadIds(relIds, {}, {}, {})
            self.widgetQtObj = self.treeViewObj.treeObj.tableWidget
            self.widgetQtObj.setColumnCount(self.widgetQtObj.columnCount() + 1)
            fieldsToReadOrdered = self.treeViewObj.treeObj.orderedFields
            self.fieldsToReadOrdered = fieldsToReadOrdered
            self.setRemoveButtons(self.widgetQtObj)
            self.setupTableWidgetLay(self.widgetQtObj)
            if self.required:
                utilsUi.setRequiredBackground(self.widgetQtObj, '')
            self.mainLay.addWidget(self.treeViewObj)
            self.widgetLyQtObject.addLayout(self.mainLay)
            self.widgetQtObj.setHorizontalHeaderItem(self.widgetQtObj.columnCount() - 1, QtGui.QTableWidgetItem('Remove'))
            self.widgetQtObj.resizeColumnsToContents()
        self.widgetLyQtObject.addSpacerItem(QtGui.QSpacerItem(20,20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))

    def setupTableWidgetLay(self, tableWidget):
        tableWidget.resizeColumnsToContents()
        tableWidget.setShowGrid(False)
        tableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

    def setRemoveButtons(self, tableWidget):
        rowCount = tableWidget.rowCount()
        colCount = tableWidget.columnCount()
        for rowCount in range(0, rowCount):
            btn = QtGui.QPushButton('Remove')
            btn.setStyleSheet(constants.BUTTON_ADD_AN_ITEM)
            tableWidget.setCellWidget(rowCount, colCount - 1, btn)
            btn.clicked.connect(partial(self.removeItem, rowCount))

    def removeItem(self, rowIndex):
        found = False
        rowIndexes = self.treeViewObj.idLineRel.keys()
        for rowInd in rowIndexes:
            objId = self.treeViewObj.idLineRel[rowInd]
            if rowInd == rowIndex:
                if objId in self.currentValue:
                    self.currentValue.remove(objId)
                    utils.removeRowFromTableWidget(self.widgetQtObj, rowIndex)
                    self.setRemoveButtons(self.widgetQtObj)
                    del self.treeViewObj.idLineRel[rowInd]
                    found = True
            elif found:
                del self.treeViewObj.idLineRel[rowInd]
                self.treeViewObj.idLineRel[rowInd - 1] = objId
        print self.treeViewObj.idLineRel

    def valueChanged(self):
        self.valueTemplateChanged()

    def setReadonly(self, val=False):
        if self.widgetQtObj:
            self.widgetQtObj.setDisabled(val)
        if self.treeViewObj:
            self.treeViewObj.treeObj.tableWidget.setDisabled(val)
            self.treeViewObj.buttToLeft.setDisabled(val)
            self.treeViewObj.buttToRight.setDisabled(val)
            self.treeViewObj.treeObj.widgetContents.setDisabled(val)
        self.createButt.setDisabled(val)
        super(One2many, self).setReadonly(val)

    def setInvisible(self, val=False):
        if self.widgetQtObj:
            self.widgetQtObj.setHidden(val)
        if self.treeViewObj:
            self.treeViewObj.buttToLeft.setHidden(val)
            self.treeViewObj.buttToRight.setHidden(val)
            self.treeViewObj.treeObj.tableWidget.setHidden(val)
            self.treeViewObj.treeObj.widgetContents.setHidden(val)
        self.labelQtObj.setHidden(val)
        self.createButt.setHidden(val)
        super(One2many, self).setInvisible(val)

    @property
    def value(self):
        return self.currentValue

    @property
    def valueInterface(self):
        return self.currentValue

    def eraseValue(self):
        self.setValue([])
