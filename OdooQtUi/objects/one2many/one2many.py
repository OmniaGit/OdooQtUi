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
import base64
from pickle import TRUE


class One2many(OdooFieldTemplate):
    def __init__(self,
                 qtParent,
                 xmlField,
                 fieldsDefinition,
                 odooConnector=None,
                 isChatterWidget=False,
                 parent_view_type=''):
        super(One2many, self).__init__(qtParent, xmlField, fieldsDefinition, odooConnector)
        self.isChatterWidget = isChatterWidget
        self.labelQtObj = False
        self.widgetQtObj = False
        self.treeViewObj = False
        self.label_name_values = False
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
        #if self.odooWidgetType == 'mail_followers':
        if self.relation=='mail.follower' and self.isChatterWidget:
            self.treeViewObj = QtWidgets.QWidget()
            self.treeViewObj.treeObj = None
        elif self.odooWidgetType == 'mail_thread':
            self.treeViewObj = QtWidgets.QWidget()
            self.treeViewObj.treeObj = None
        elif self.odooWidgetType == 'mail_activity':
            self.treeViewObj = QtWidgets.QWidget()
            self.treeViewObj.treeObj = None
        elif parent_view_type != 'tree':
            self.treeViewObj = self.odooConnector.initTreeListViewObject(odooObjectName=self.relation,
                                                                         viewName='',
                                                                         view_id=False,
                                                                         viewCheckBoxes={},
                                                                         viewFilter=False)
        self.getQtObject(parent_view_type)

    def getMessageChatterWidget(self):
        label = QtWidgets.QLabel('-----------------  Chat  -----------------')
        label.setStyleSheet(constants.BUTTON_STYLE + constants.VIOLET_BACKGROUND)
        label.setAlignment(QtCore.Qt.AlignCenter)
        mainWidget = QtWidgets.QWidget()

        sendMessageBoxHLayout = QtWidgets.QHBoxLayout()
        self.buttSendMessage = QtWidgets.QPushButton('Send Message')
        self.buttLogNote = QtWidgets.QPushButton('Log Note')
        self.buttSendMessage.setFlat(True)
        self.buttLogNote.setFlat(True)
        self.buttSendMessage.setStyleSheet(constants.BUTTON_STYLE_LINK)
        self.buttLogNote.setStyleSheet(constants.BUTTON_STYLE_LINK)
        self.buttSendMessage.clicked.connect(self.sendMessage)
        self.buttLogNote.clicked.connect(self.logNote)
        sendMessageBoxHLayout.addWidget(self.buttSendMessage)
        sendMessageBoxHLayout.addWidget(self.buttLogNote)

        mainWidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.mainMessageVLay = QtWidgets.QVBoxLayout(mainWidget)
        scrollArea = QtWidgets.QScrollArea()
        scrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        scrollArea.setFrameShadow(QtWidgets.QFrame.Sunken)
        scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        scrollArea.setWidgetResizable(True)
        scrollArea.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        scrollAreaWidgetContents = QtWidgets.QWidget()
        self.messageVLay = QtWidgets.QVBoxLayout(scrollAreaWidgetContents)
        scrollArea.setWidget(scrollAreaWidgetContents)
        self.mainMessageVLay.addWidget(label)
        self.mainMessageVLay.addLayout(sendMessageBoxHLayout)
        self.mainMessageVLay.addWidget(scrollArea)
        mainWidget.setLayout(self.mainMessageVLay)
        mainWidget.setMinimumHeight(300)
        self.populateNoteLay()
        return mainWidget

    def getMailActivityWidget(self):
        label = QtWidgets.QLabel('-----------------  Planned Activities  -----------------')
        label.setStyleSheet(constants.BUTTON_STYLE + constants.VIOLET_BACKGROUND)
        label.setAlignment(QtCore.Qt.AlignCenter)
        mainWidget = QtWidgets.QWidget()
        mainWidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        mainLay = QtWidgets.QVBoxLayout(mainWidget)
        scrollArea = QtWidgets.QScrollArea()
        scrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        scrollArea.setFrameShadow(QtWidgets.QFrame.Sunken)
        scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        scrollArea.setWidgetResizable(True)
        scrollArea.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        scrollAreaWidgetContents = QtWidgets.QWidget()
        self.activityVLayout = QtWidgets.QVBoxLayout(scrollAreaWidgetContents)
        scrollArea.setWidget(scrollAreaWidgetContents)
        mainLay.addWidget(label)
        mainLay.addWidget(scrollArea)
        mainWidget.setLayout(mainLay)
        mainWidget.setMinimumHeight(300)
        return mainWidget

    def showActivities(self):
        messages = self.odooConnector.rpc_connector.read(self.relation, [], self.currentValue)
        for messageDict in messages:
            _activity_id, activity_name = messageDict.get('activity_type_id', [False, ''])
            _user_id, user_name = messageDict.get('user_id', [False, ''])
            state = messageDict.get('state', '')
            note = messageDict.get('note', '')
            summary = messageDict.get('summary', '')
            icon = messageDict.get('icon', '')
            date_deadline = messageDict.get('date_deadline', '')
            
            contentHLay = QtWidgets.QHBoxLayout()
            if icon == 'fa-envelope':
                icon_path = utilsUi.getIconPath('mail.png')
            elif icon == 'fa-phone':
                icon_path = utilsUi.getIconPath('phone.png')
            elif icon == 'fa-users':
                icon_path = utilsUi.getIconPath('meeting.png')
            elif icon == 'fa-tasks':
                icon_path = utilsUi.getIconPath('todo.png')
            if icon_path:
                with open(icon_path, 'rb') as file_obj:
                    labelImage = utilsUi.getQtImageFromContent(file_obj.read(), imageWidth=20, imageHeight=20, b64decode=False)
                    contentHLay.addWidget(labelImage)

            labelBody = QtWidgets.QTextEdit()
            labelBody.setFrameShape(QtWidgets.QFrame.NoFrame)
            labelBody.insertHtml(note)
            labelBody.setReadOnly(True)
            # labelBody.setFixedHeight(labelBody.document().size().toSize().height() + 3)
            
            msg = '%s: %s "%s" for %s            Date %s' % (state.capitalize(), activity_name, summary, user_name, date_deadline)
            labelUser = QtWidgets.QLabel(msg)
            labelUser.setAlignment(QtCore.Qt.AlignLeft)
            contentHLay.addWidget(labelUser)
            verticalSpacer = QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            contentHLay.addSpacerItem(verticalSpacer)
            
            mainVLay = QtWidgets.QVBoxLayout()
            mainVLay.addLayout(contentHLay)
            mainVLay.addWidget(labelBody)

            mainWidget = QtWidgets.QWidget()
            mainWidget.setLayout(mainVLay)
            labelUser.setStyleSheet('font-weight: bold;')
            mainWidget.setStyleSheet('background-color: #efefef;')
            mainWidget.setMinimumHeight(100)
            self.activityVLayout.addWidget(mainWidget)

    def showChatterWidget(self):
        self.show()
        #if self.odooWidgetType == 'mail_thread':
        if True:
            self.showMessagges()
        elif self.odooWidgetType == 'mail_followers':
            self.showFollowers()
        elif self.odooWidgetType == 'mail_activity':
            self.showActivities()
        
    def getQtObject(self, parent_view_type):
        self.createButt = None
        if self.odooWidgetType == 'mail_followers':
            self.qtHorizontalWidget.addLayout(self.messaggesLay)
        elif self.odooWidgetType == 'mail_thread':
            self.qtHorizontalWidget.addWidget(self.getMessageChatterWidget())
        elif self.odooWidgetType == 'mail_activity':
            self.qtHorizontalWidget.addWidget(self.getMailActivityWidget())
        elif parent_view_type != 'tree':
            self.labelQtObj = QtWidgets.QLabel(self.fieldStringInterface)
            self.labelQtObj.setStyleSheet(constants.LABEL_STYLE)
            self.qtHorizontalWidget.addWidget(self.labelQtObj)
            self.createButt = QtWidgets.QPushButton('Create')
            self.createButt.setStyleSheet(constants.BUTTON_STYLE)
            self.qtHorizontalWidget.addWidget(self.createButt)
            self.createButt.clicked.connect(self.createAndAdd)
        else:
            self.label_name_values = QtWidgets.QLabel('')
            self.qtHorizontalWidget.addWidget(self.label_name_values)

    def populateNoteLay(self):
        self.textEditMess = QtWidgets.QTextEdit()
        self.sendButtonMess = QtWidgets.QPushButton('Send')
        self.sendButtonMess.setStyleSheet(constants.BUTTON_STYLE_MANY_2_ONE__2)
        self.mainMessageVLay.addWidget(self.textEditMess)
        lay = QtWidgets.QHBoxLayout()
        lay.addWidget(self.sendButtonMess)
        self.mainMessageVLay.addLayout(lay)
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
        for i in reversed(list(range(self.messageVLay.count()))):
            self.messageVLay.itemAt(i).widget().deleteLater()
        if res:
            self.currentValue.insert(0, res)
        self.showMessagges()
        self.textEditMess.setText('')

    def showNoteLay(self, visible=False):
        self.textEditMess.setHidden(not visible)
        self.sendButtonMess.setHidden(not visible)

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
        return self.odooConnector.rpc_connector.callCustomMethod('mail.thread', 'message_post', parameters, kwargParameters, context=context)

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
        return self.odooConnector.rpc_connector.callCustomMethod('mail.thread', 'message_post', parameters, kwargParameters, context=context)

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


    def populateMenu(self):
        followerAction = self.toolmenu.addAction('Add Followers')
        followerAction.changed.connect(self.addFollower)
        channelAction = self.toolmenu.addAction('Add Channels')
        channelAction.changed.connect(self.addChannel)
        self.toolmenu.addSeparator()
        res = self.odooConnector.rpc_connector.read(self.relation, [], self.currentValue)
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
            self.odooConnector.rpc_connector.write(self.parentModel, {self.fieldName: [(2, resId, False)]}, self.parentId)
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
            resId = self.odooConnector.rpc_connector.create(self.relation, values)
            self.odooConnector.rpc_connector.write(self.parentModel, {self.fieldName: [(4, resId, False)]}, self.parentId)
            self.currentValue.append(resId)
            self.toolmenu.clear()
            self.populateMenu()
            self.buttonFollowersCount.setText(str(len(self.currentValue)))
            self.setFollowingButton()

    def getPartnerIdFromUserId(self, userId=False):
        if not userId:
            userId = self.odooConnector.rpc_connector.userId
        partnerId, partnerName = False, ''
        res = self.odooConnector.rpc_connector.read('res.users', ['partner_id'], userId)
        for elem in res:
            partnerId, partnerName = elem.get('partner_id', [False, ''])
        return partnerId, partnerName

    def followClicked(self):
        currText = str(self.followButton.text())
        partnerId, _partnerName = self.getPartnerIdFromUserId()
        if partnerId:
            if currText == 'Following':
                res = self.odooConnector.rpc_connector.search(self.relation,
                                           [('partner_id', '=', partnerId),
                                            ('res_id', '=', self.parentId)])
                for objId in res:
                    self.removeFollowerChannel(objId)
            else:
                self._addFollower(partnerId)

    def showMessagges(self):
        messages = self.odooConnector.rpc_connector.read(self.relation, [], self.currentValue)
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
            labelBody.setFixedHeight(labelBody.document().size().toSize().height() + 3)
            hlayUser = QtWidgets.QHBoxLayout()
            hlayUser.addWidget(labelUser)
            hlayUser.addWidget(labelDate)
            mainVLay = QtWidgets.QVBoxLayout()
            mainVLay.addLayout(hlayUser)
            mainVLay.addWidget(labelBody)
            attachmentLay = QtWidgets.QHBoxLayout()
            if attachment_ids:
                res = self.odooConnector.rpc_connector.read('ir.attachment', ['datas', 'datas_fname'], attachment_ids)
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
            mainWidget.setStyleSheet('background-color: #efefef;')
            self.messageVLay.addWidget(mainWidget)

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

    def setValue(self, relIds, viewType='form'):
        self.currentValue = relIds
        if self.odooWidgetType == 'mail_followers':
            return
        elif self.odooWidgetType == 'mail_thread':
            return
        elif self.odooWidgetType == 'mail_activity':
            return
        elif self.label_name_values:
            self.loaded_ids = relIds
            str_to_display = ''
            for box_vals in self.odooConnector.rpc_connector.read(self.relation, ['display_name'], relIds):
                str_to_display += '%s | ' % (box_vals.get('display_name', ''))
            if str_to_display.endswith(' | '):
                str_to_display = str_to_display[:-2]
            self.label_name_values.setText(str_to_display)
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
            self.qtHorizontalWidget.addLayout(self.mainLay)
            self.widgetQtObj.setHorizontalHeaderItem(self.widgetQtObj.columnCount() - 1, QtWidgets.QTableWidgetItem('Remove'))
            self.widgetQtObj.resizeColumnsToContents()
        #self.addSpacerItem(QtWidgets.QSpacerItem(10,10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

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
                    utils.removeRowFromTableWidget(self.widgetQtObj, rowIndex)
                    self.setRemoveButtons(self.widgetQtObj)
                    del self.treeViewObj.idLineRel[rowInd]
                    found = True
            elif found:
                del self.treeViewObj.idLineRel[rowInd]
                self.treeViewObj.idLineRel[rowInd - 1] = objId

    def valueChanged(self):
        self.valueTemplateChanged()

    def setReadonly(self, val=False):
        try:
            if self.widgetQtObj:
                self.widgetQtObj.setDisabled(val)
            if self.treeViewObj:
                self.treeViewObj.treeObj.tableWidget.setDisabled(val)
                self.treeViewObj.buttToLeft.setDisabled(val)
                self.treeViewObj.buttToRight.setDisabled(val)
                if  self.treeViewObj.treeObj.widgetContents:
                    self.treeViewObj.treeObj.widgetContents.setDisabled(val)
            if self.createButt:
                self.createButt.setDisabled(val)
            super(One2many, self).setReadonly(val)
        except Exception as ex:
            utils.logError(ex, 'setReadonly')

    def setInvisible(self, val=False):
        try:
            if self.isChatterWidget:
                return
            if self.widgetQtObj:
                self.widgetQtObj.setHidden(val)
            if self.treeViewObj:
                self.treeViewObj.buttToLeft.setHidden(val)
                self.treeViewObj.buttToRight.setHidden(val)
                self.treeViewObj.treeObj.tableWidget.setHidden(val)
                if  self.treeViewObj.treeObj.widgetContents:
                    self.treeViewObj.treeObj.widgetContents.setHidden(val)
            if self.label_name_values:
                self.label_name_values.setHidden(val)
            self.labelQtObj.setHidden(val)
            self.createButt.setHidden(val)
            if self.labelQtObj:
                self.labelQtObj.setHidden(val)
            if self.createButt:
                self.createButt.setHidden(val)
            super(One2many, self).setInvisible(val)
        except Exception as ex:
            utils.logError(ex, 'setInvisible')

    @property
    def value(self):
        return self.currentValue

    @property
    def valueInterface(self):
        if self.label_name_values:
            return self.label_name_values.text()
        return self.currentValue

    def eraseValue(self):
        self.setValue([])
