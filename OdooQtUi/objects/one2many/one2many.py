'''
Created on 7 Feb 2017

@author: dsmerghetto
'''
import json
import os
import logging

from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets

from OdooQtUi.utils_odoo_conn import utils, utilsUi
from OdooQtUi.utils_odoo_conn import constants
from functools import partial
from OdooQtUi.objects.fieldTemplate import OdooFieldTemplate
from OdooQtUi.RPC.rpc import connectionObj
import base64


class One2many(OdooFieldTemplate):
    def __init__(self, qtParent, xmlField, fieldsDefinition, rpc, odooConnector=None):
        super(One2many, self).__init__(qtParent, xmlField, fieldsDefinition, rpc)
        self.labelQtObj = False
        self.qDoubleSpinBoxValue = False
        self.treeViewObj = False
        self.currentMessType = 'NOTE'
        self.odooConnector = odooConnector
        self.relation = self.fieldPyDefinition.get('relation', '')
        self.canCreate = json.loads(self.fieldXmlAttributes.get('can_create', 'true'))
        self.canWrite = json.loads(self.fieldXmlAttributes.get('can_write', 'true'))
        self.odooWidgetType = self.fieldXmlAttributes.get('widget', '')
        self.mainLay = QtWidgets.QVBoxLayout()
        self.evaluatedIds = {}
        self.currentValue = []
        self.messaggesLay = QtWidgets.QVBoxLayout()
        self.messaggesLay.setSpacing(15)
        if self.odooWidgetType == 'mail_followers':
            self.treeViewObj = QtWidgets.QWidget()
        elif self.odooWidgetType == 'mail_thread':
            self.treeViewObj = QtWidgets.QWidget()
        else:
            self.treeViewObj = self.odooConnector.initTreeListViewObject(odooObjectName=self.relation,
                                                                         viewName='',
                                                                         view_id=False,
                                                                         rpcObj=self.rpc,
                                                                         activeLanguage='',
                                                                         viewCheckBoxes={},
                                                                         viewFilter=False)
        self.getQtObject()

    def getMessageChatterWidget(self):
        self.setMinimumSize(100, 250)
        self.chatterWidget = QtWidgets.QWidget()
        self.chatterWidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        chatterVLayout = QtWidgets.QVBoxLayout()
        self.messaggesButton = QtWidgets.QPushButton('Show Chatter')
        self.messaggesButton.setStyleSheet(constants.BUTTON_STYLE)
        self.messaggesButton.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.messaggesButton.setMinimumSize(100, 40)
        self.messaggesButton.clicked.connect(self.showMessagges)
        chatterVLayout.addWidget(self.messaggesButton)
        # send message box
        self.sendMessageBox = QtWidgets.QWidget()
        sendMessageBoxHLayout = QtWidgets.QHBoxLayout()
        self.buttSendMessage = QtWidgets.QPushButton('Send Message')
        self.buttLogNote = QtWidgets.QPushButton('Log Note')
        self.buttSendMessage.setStyleSheet(constants.BUTTON_STYLE_MANY_2_ONE__2)
        self.buttLogNote.setStyleSheet(constants.BUTTON_STYLE_MANY_2_ONE__2)
        self.buttSendMessage.clicked.connect(self.sendMessage)
        self.buttLogNote.clicked.connect(self.logNote)
        spacerExpander = QtWidgets.QSpacerItem(40, 100, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sendMessageBoxHLayout.addWidget(self.buttSendMessage)
        sendMessageBoxHLayout.addWidget(self.buttLogNote)
        sendMessageBoxHLayout.addItem(spacerExpander)
        self.sendMessageBox.setLayout(sendMessageBoxHLayout)
        self.sendMessageBox.hide()
        chatterVLayout.addWidget(self.sendMessageBox)
        # Scroll messages
        self.messageScroll = QtWidgets.QScrollArea(self.chatterWidget)
        messageWidget = QtWidgets.QWidget(self.chatterWidget)
        self.messageVLay = QtWidgets.QVBoxLayout()
        messageWidget.setLayout(self.messageVLay)
        self.messageScroll.setWidget(messageWidget)
        self.messageScroll.setWidgetResizable(True)
        chatterVLayout.addWidget(self.messageScroll)
        verticalSpacer = QtWidgets.QSpacerItem(40, 100, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        chatterVLayout.addItem(verticalSpacer)
        self.messageScroll.hide()
        self.messageScroll.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.chatterWidget.setLayout(chatterVLayout)
        self.chatterWidget.setMinimumSize(100, 100)
        return self.chatterWidget

    def getQtObject(self):
        if self.odooWidgetType == 'mail_followers':
            self.followersButton = QtWidgets.QPushButton('Show Followers')
            self.followersButton.setStyleSheet(constants.BUTTON_STYLE)
            self.followersButton.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
            self.followersButton.clicked.connect(self.showFollowers)
            self.followersOpened = False
            self.qtHorizontalWidget.addWidget(self.followersButton)
            self.qtHorizontalWidget.addLayout(self.messaggesLay)
        elif self.odooWidgetType == 'mail_thread':
            self.qtHorizontalWidget.addWidget(self.getMessageChatterWidget())
            return
            #  old chatter
            self.messaggesButton = QtWidgets.QPushButton('Show Chatter')
            self.messaggesButton.setStyleSheet(constants.BUTTON_STYLE)
            self.messaggesButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
            self.messaggesButton.clicked.connect(self.showMessagges)
            self.messaggesButtLay = QtWidgets.QHBoxLayout()
            self.populateMessButtLay()
            self.noteLay = QtWidgets.QVBoxLayout()
            self.populateNoteLay()
            self.qtHorizontalWidget.addWidget(self.messaggesButton)
            self.qtHorizontalWidget.addLayout(self.messaggesButtLay)
            self.qtHorizontalWidget.addLayout(self.noteLay)
            self.qtHorizontalWidget.addLayout(self.messaggesLay)
        else:
            self.labelQtObj = QtWidgets.QLabel(self.fieldStringInterface)
            self.labelQtObj.setStyleSheet(constants.LABEL_STYLE)
            self.qtHorizontalWidget.addWidget(self.labelQtObj)
            self.createButt = QtWidgets.QPushButton('Create')
            self.createButt.setStyleSheet(constants.BUTTON_STYLE)
            self.qtHorizontalWidget.addWidget(self.createButt)
            self.createButt.clicked.connect(self.createAndAdd)

    def populateNoteLay(self):
        self.textEditMess = QtWidgets.QTextEdit()
        self.sendButtonMess = QtWidgets.QPushButton('Send')
        self.sendButtonMess.setStyleSheet(constants.BUTTON_STYLE_MANY_2_ONE__2)
        self.noteLay.addWidget(self.textEditMess)
        lay = QtWidgets.QHBoxLayout()
        lay.addWidget(self.sendButtonMess)
        self.noteLay.addLayout(lay)
        self.textEditMess.setStyleSheet(constants.TEXT_STYLE)
        self.sendButtonMess.clicked.connect(self.sendMessNote)
        self.showNoteLay(False)

    def sendMessNote(self):
        body = str(self.textEditMess.toPlainText())
        res = False
        if self.currentMessType == 'NOTE':
            res = self._logNote(body)
        else:
            res = self._sendMessage(body)
        self.showNoteLay(False)
        for i in reversed(list(range(self.messaggesLay.count()))):
            self.messaggesLay.itemAt(i).widget().deleteLater()
        if res:
            self.currentValue.insert(0, res)
        self.showMessagges()
        self.textEditMess.setText('')

    def showNoteLay(self, visible=False):
        self.textEditMess.setHidden(not visible)
        self.sendButtonMess.setHidden(not visible)

    def populateMessButtLay(self):
        self.buttSendMessage = QtWidgets.QPushButton('Send Message')
        self.buttLogNote = QtWidgets.QPushButton('Log Note')
        self.buttSendMessage.setStyleSheet(constants.BUTTON_STYLE_MANY_2_ONE__2)
        self.buttLogNote.setStyleSheet(constants.BUTTON_STYLE_MANY_2_ONE__2)
        self.messaggesButtLay.addWidget(self.buttSendMessage)
        self.messaggesButtLay.addWidget(self.buttLogNote)
        #self.messaggesButtLay.addSpacerItem(QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        self.buttSendMessage.clicked.connect(self.sendMessage)
        self.buttLogNote.clicked.connect(self.logNote)
        self.buttSendMessage.setHidden(True)
        self.buttLogNote.setHidden(True)

    def sendMessage(self):
        self.showNoteLay(True)
        self.currentMessType = 'MESSAGE'

    def _sendMessage(self, body=''):
        parameters = self.parentId
        kwargParameters = {}
        context = {}
        kwargParameters['body'] = body
        kwargParameters['subject'] = False
        kwargParameters['message_type'] = 'comment'
        kwargParameters['subtype'] = 'mail.mt_comment'
        kwargParameters['parent_id'] = False
        kwargParameters['attachments'] = []
        kwargParameters['content_subtype'] = 'html'
        context['thread_model'] = 'product.product'
        return connectionObj.callCustomMethod('mail.thread', 'message_post', parameters, kwargParameters, context=context)

    def logNote(self):
        self.showNoteLay(True)
        self.currentMessType = 'NOTE'

    def _logNote(self, body=''):
        parameters = self.parentId
        kwargParameters = {}
        context = {}
        kwargParameters['body'] = body
        kwargParameters['subject'] = False
        kwargParameters['message_type'] = 'comment'
        kwargParameters['subtype'] = 'mail.mt_note'
        kwargParameters['parent_id'] = False
        kwargParameters['attachments'] = []
        kwargParameters['content_subtype'] = 'html'
        context['thread_model'] = 'product.product'
        return connectionObj.callCustomMethod('mail.thread', 'message_post', parameters, kwargParameters, context=context)

    def showFollowers(self):
        self.followersButton.setHidden(True)
        if not self.followersOpened:
            lay = QtWidgets.QHBoxLayout()
            self.followButton = QtWidgets.QPushButton('UnFollowing')
            self.followButton.clicked.connect(self.followClicked)
            self.setUnfolloWingButton()
            lay.addWidget(self.followButton)
            self.buttonFollowersCount = QtWidgets.QToolButton()
            self.buttonFollowersCount.setText(str(len(self.currentValue)))
            self.toolmenu = QtWidgets.QMenu()
            res = self.populateMenu()
            for obj in res:
                currentPartnerId, _partnerName = self.getPartnerIdFromUserId()
                partnerRes = obj.get('partner_id')
                if partnerRes and partnerRes[0] == currentPartnerId:
                    self.setFollowingButton()
            self.buttonFollowersCount.setMenu(self.toolmenu)
            self.buttonFollowersCount.setPopupMode(QtWidgets.QToolButton.InstantPopup)
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
            self.buttonFollowersCount.setText(str(len(self.currentValue)))
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
            self.buttonFollowersCount.setText(str(len(self.currentValue)))
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
        currText = str(self.followButton.text())
        partnerId, _partnerName = self.getPartnerIdFromUserId()
        if partnerId:
            if currText == 'Following':
                res = connectionObj.search(self.relation,
                                           [('partner_id', '=', partnerId),
                                            ('res_id', '=', self.parentId)])
                for objId in res:
                    self.removeFollowerChannel(objId)
            else:
                self._addFollower(partnerId)

    def showMessagges(self):
        self.sendMessageBox.show()
        #self.messaggesButton.setEnabled(False)
        #self.messaggesButton.setStyleSheet(constants.BUTTON_STYLE + 'background-color: #d3d0d0;')
        messages = connectionObj.read(self.relation, [], self.currentValue)
        for messageDict in messages:
            _userId, userName = messageDict.get('author_id', [False, ''])
            bodyMessage = messageDict.get('body', '')
            write_date = messageDict.get('write_date', '')
            attachment_ids = messageDict.get('attachment_ids', [])
            labelUser = QtWidgets.QLabel(userName)
            labelDate = QtWidgets.QLabel(write_date)
            labelBody = QtWidgets.QTextEdit()
            labelBody.setFrameShape(QtWidgets.QFrame.NoFrame)
            labelBody.insertHtml(bodyMessage)
            labelBody.setReadOnly(True)
            hlayUser = QtWidgets.QHBoxLayout()
            hlayUser.addWidget(labelUser)
            hlayUser.addWidget(labelDate)
            mainVLay = QtWidgets.QVBoxLayout()
            mainVLay.addLayout(hlayUser)
            mainVLay.addWidget(labelBody)
            attachmentLay = QtWidgets.QHBoxLayout()
            if attachment_ids:
                res = connectionObj.read('ir.attachment', ['datas', 'datas_fname'], attachment_ids)
                for attachDict in res:
                    fileContent = attachDict.get('datas', '')
                    fileName = attachDict.get('datas_fname', '')
                    imageLay = QtWidgets.QVBoxLayout()
                    labelImage = utilsUi.getQtImageFromContent(fileContent, imageWidth=120, imageHeight=120)
                    imageLay.addWidget(labelImage)
                    buttonDownloadImage = QtWidgets.QPushButton('Download')
                    buttonDownloadImage.setStyleSheet(constants.BUTTON_STYLE + 'max-width: 100px;')
                    buttonDownloadImage.clicked.connect(partial(self.downloadImage, fileContent, fileName))
                    imageLay.addWidget(buttonDownloadImage)
                    attachmentLay.addLayout(imageLay)
            mainVLay.addLayout(attachmentLay)
            mainWidget = QtWidgets.QWidget()
            mainWidget.setLayout(mainVLay)
            labelUser.setStyleSheet('font-weight: bold;')
            mainWidget.setStyleSheet('background-color: #cccbcb;')
            self.messageVLay.addWidget(mainWidget)
            self.messageScroll.show()

    def downloadImage(self, content, fileName):
        fileCleanContent = base64.b64decode(content)
        cleanFname, extension = os.path.splitext(fileName)
        filePath = utilsUi.getDirectoryFileToSaveSystem(None, cleanFname, fileType='*%s' % (extension))
        if filePath:
            filePath = str(filePath)
            with open(filePath, 'wb') as writeFile:
                writeFile.write(fileCleanContent)
            utils.openByDefaultEditor(filePath)

    def createAndAdd(self):
        try:
            def acceptDial():
                dialog.accept()

            def rejectDial():
                dialog.reject()

            dialog = QtWidgets.QDialog()
            mainLay = QtWidgets.QVBoxLayout()
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
            if dialog.exec_() == QtWidgets.QDialog.Accepted:
                fieldVals = viewObjForm.getAllFieldsValues()
                objId = self.rpc.create(self.relation, fieldVals)
                if objId:
                    self.currentValue.append(objId)
                    self.setValue(self.currentValue)
        except Exception as ex:
            utils.logMessage('error', '%r' % (ex), 'createAndAdd')

    def computeFieldVal(self, val):
        outStrVal = ''
        if isinstance(val, (list, tuple)):
            _objId, outStrVal = val
        elif isinstance(val, bool):
            outStrVal = ''
        elif isinstance(val, int):
            outStrVal = ''
        elif isinstance(val, (str)):
            outStrVal = str(val)
        return outStrVal

    def setValue(self, relIds):
        self.currentValue = relIds
        if self.odooWidgetType == 'mail_followers':
            return
        elif self.odooWidgetType == 'mail_thread':
            return
        else:
            self.treeViewObj.loadIds(relIds, {}, {}, {})
            self.qDoubleSpinBoxValue = self.treeViewObj.treeObj.tableWidget
            self.qDoubleSpinBoxValue.setColumnCount(self.qDoubleSpinBoxValue.columnCount() + 1)
            fieldsToReadOrdered = self.treeViewObj.treeObj.orderedFields
            self.fieldsToReadOrdered = fieldsToReadOrdered
            self.setRemoveButtons(self.qDoubleSpinBoxValue)
            self.setupTableWidgetLay(self.qDoubleSpinBoxValue)
            if self.required:
                utilsUi.setRequiredBackground(self.qDoubleSpinBoxValue, '')
            self.mainLay.addWidget(self.treeViewObj)
            self.qtHorizontalWidget.addLayout(self.mainLay)
            self.qDoubleSpinBoxValue.setHorizontalHeaderItem(self.qDoubleSpinBoxValue.columnCount() - 1, QtWidgets.QTableWidgetItem('Remove'))
            self.qDoubleSpinBoxValue.resizeColumnsToContents()
        #self.addSpacerItem(QtWidgets.QSpacerItem(20,20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

    def setupTableWidgetLay(self, tableWidget):
        tableWidget.resizeColumnsToContents()
        tableWidget.setShowGrid(False)
        tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

    def setRemoveButtons(self, tableWidget):
        rowCount = tableWidget.rowCount()
        colCount = tableWidget.columnCount()
        for rowCount in range(0, rowCount):
            btn = QtWidgets.QPushButton('Remove')
            btn.setStyleSheet(constants.BUTTON_ADD_AN_ITEM)
            tableWidget.setCellWidget(rowCount, colCount - 1, btn)
            btn.clicked.connect(partial(self.removeItem, rowCount))

    def removeItem(self, rowIndex):
        found = False
        rowIndexes = list(self.treeViewObj.idLineRel.keys())
        for rowInd in rowIndexes:
            objId = self.treeViewObj.idLineRel[rowInd]
            if rowInd == rowIndex:
                if objId in self.currentValue:
                    self.currentValue.remove(objId)
                    utils.removeRowFromTableWidget(self.qDoubleSpinBoxValue, rowIndex)
                    self.setRemoveButtons(self.qDoubleSpinBoxValue)
                    del self.treeViewObj.idLineRel[rowInd]
                    found = True
            elif found:
                del self.treeViewObj.idLineRel[rowInd]
                self.treeViewObj.idLineRel[rowInd - 1] = objId

    def valueChanged(self):
        self.valueTemplateChanged()

    @property
    def value(self):
        return self.currentValue

    @property
    def valueInterface(self):
        return self.currentValue

    def eraseValue(self):
        self.setValue([])
