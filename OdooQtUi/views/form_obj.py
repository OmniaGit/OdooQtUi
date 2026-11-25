# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011-2026 OmniaSolutions and the OdooQtUi contributors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of OdooQtUi, released under the Apache License 2.0.
# Redistributions must keep the attribution in the NOTICE file.
# See the LICENSE and NOTICE files at the root of the project.

'''
Created on 24 Mar 2017

@author: dsmerghetto
'''
import copy
import json
import logging
import xml.etree.cElementTree as ElementTree
from functools import partial
from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

from OdooQtUi.views.templateView import TemplateView
from OdooQtUi.utils_odoo_conn import utils
from OdooQtUi.utils_odoo_conn import utilsUi
from OdooQtUi.utils_odoo_conn import constants
from OdooQtUi.objects.selection.selection import Selection
from OdooQtUi.objects.boolean.boolean import Boolean
from OdooQtUi.objects.char.char import Charachter
from OdooQtUi.objects.date.date import Date
from OdooQtUi.objects.datetimee.datetimee import Datetime
from OdooQtUi.objects.float.float import Float
from OdooQtUi.objects.integer.integer import Integer
from OdooQtUi.objects.many2many.many2many import Many2many
from OdooQtUi.objects.many2one.many2one import Many2one
from OdooQtUi.objects.one2many.one2many import One2many
from OdooQtUi.objects.binary.binary import Binary
from OdooQtUi.objects.text.text import Text
from OdooQtUi.objects import button
from OdooQtUi.widgets.page_tab_widget import PageTabWidget


#: useHeader that shows of a form's header only its statusbar.
STATUSBAR_ONLY = 'statusbar'


class TemplateFormView(TemplateView):
    nootebook_changed_signal = QtCore.Signal(int)
    form_changed = QtCore.Signal(str)

    def __init__(self,
                 viewObj,
                 odooConnector=None,
                 hideFormContent=False):
        self.globalMapping = {}
        self.aloneLabels = {}
        self.notebookTabsNotComputed = {}
        # [(invisible expression, callable taking hidden)] for the div, group
        # and page nodes whose visibility depends on the record.
        self.containerModifiers = []
        self.nootebookFieldsToCompute = {}  # {nootebookIndex: {'fieldName': fieldObj}}
        self.requiredFields = {}
        self.readonlyFields = {}
        self.invisibleFields = {}
        self.fieldDefaultVals = {}  # {'fieldName' : fieldval}
        self.skipOnChange = False
        self.readonly = False
        self.activeIds = []         # must be one
        self.hideFormContent = hideFormContent
        #
        super(TemplateFormView, self).__init__(odooConnector=odooConnector,
                                               viewObj=viewObj)
        #
        self.objectsInit = copy.deepcopy(self.fields)
        self._initViewObj()
        self.nootebook_changed_signal.connect(self.updateDataStructure)
        self.setMinimumSize(0, 0)
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        

    def _initViewObj(self):
        if self.fieldsNameTypeRel:
            self.startingFieldValues = self.fieldsNameTypeRel.get('fields', {})
            self.RenderArch()
            self.mappingInterface = self.globalMapping
            self.addToObject()
            self._setFieldModifiers()
        else:
            utils.logWarning('Unable to get fields view definition!', '_initViewObj')

    @utils.timeit
    def RenderArch(self):
        if self.arch:
            self.setStyleSheet(constants.MAIN_STYLE)
            vertical_layout = QtWidgets.QVBoxLayout()
            vertical_layout.setSpacing(0)
            self.computeRecursion(qvboxLayout=vertical_layout,
                                  xmlParent=ElementTree.XML(self.arch.encode('utf-8')))
            verticalSpacer = QtWidgets.QSpacerItem(40, 100, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            vertical_layout.addItem(verticalSpacer)
            self.setLayout(vertical_layout)
        else:
            utils.logWarning('No arch set impossible to compute structure')

    def computeRecursion(self,
                         qvboxLayout=False,
                         xmlParent=None,
                         nootebookIndex=0,
                         row_widget_limit=4):
        # TODO:    div name <div name="button_box" class="oe_button_box">
        row_widget_count = 0
        if not qvboxLayout:
            qvboxLayout = QtWidgets.QVBoxLayout()
            qvboxLayout.setSpacing(0)
            qvboxLayout.setContentsMargins(0, 0, 0, 0)
        if constants.DEBUG:
            line = QtWidgets.QLineEdit()
            line.setStyleSheet("border:2px solid blue;")
            qvboxLayout.addWidget(line)
        row_container = QtWidgets.QHBoxLayout()
        row_container.setSpacing(0)
        #
        for childXlmElement in xmlParent:
            childXmlTag = childXlmElement.tag
            xmlAttrs = childXlmElement.attrib
            if childXmlTag == 'sheet' and not self.hideFormContent:
                self.sheet_layout = self.computeRecursion(qvboxLayout=qvboxLayout,
                                                          xmlParent=childXlmElement)
            elif childXmlTag == 'header' and self.useHeader:
                mapping, layout = self.computeHeader(archHeader=childXlmElement, useHeader=self.useHeader)
                if layout:
                    if self.useHeader:
                        qvboxLayout.addLayout(layout)
                    else:
                        layout.deleteLater()
                if mapping:
                    self.globalMapping.update(mapping)
            elif childXmlTag == 'div':
                divAttrib = childXlmElement.attrib
                divClass = divAttrib.get('class', '')
                if divClass == 'oe_chatter':
                    if not self.useChatter:
                        utils.logWarning('Chatter not implemented')
                        continue
                    else:
                        self.computeChatter(qvboxLayout, childXlmElement)
                elif divClass == 'oe_button_box':
                    pass
                elif divClass == 'oe_title':
                    self.computeRecursion(qvboxLayout=self._conditionalLayout(childXlmElement, qvboxLayout),
                                          xmlParent=childXlmElement)
                elif childXlmElement.text and len(childXlmElement.text.strip()) > 0:
                    divLayout = self._conditionalLayout(childXlmElement, qvboxLayout)
                    label = QtWidgets.QLabel(childXlmElement.text)
                    label.setStyleSheet(constants.LABEL_SEPARATOR)
                    divLayout.addWidget(label)
                    self.computeRecursion(qvboxLayout=divLayout,
                                          xmlParent=childXlmElement)
                else:
                    qvboxLayout.addLayout(row_container)
                    self.computeRecursion(qvboxLayout=self._conditionalLayout(childXlmElement, qvboxLayout),
                                          xmlParent=childXlmElement)
            elif childXmlTag == 'notebook':
                qvboxLayout.addLayout(row_container)
                tabWidget = PageTabWidget(self)
                tabWidget.setStyleSheet(constants.NOOTEBOOK_STYLE)
                tabWidgetBar = tabWidget.tabBar()
                tabWidgetBar.setStyleSheet(constants.NOOTEBOOK_TABBAR_STYLE)
                nootebookIndex = 0
                for page in childXlmElement:
                    pageString = page.attrib.get('string', '')
                    invisible = page.attrib.get('invisible', False)
                    modifInvisible, modifReadonly = utils.evaluateModifiers(page.attrib.get('modifiers', {}))
                    # An expression is not a yes: "not is_company" is a
                    # non-empty string, and read as a boolean it dropped the
                    # page for every record. Only a page that is always hidden
                    # is left out; one that depends on the record is built and
                    # its tab shown or hidden by _setFieldModifiers.
                    constantInvisible = utils.isConstantModifier(invisible) and utils.evaluateExpression(invisible)
                    if constantInvisible or modifInvisible:
                        continue
                    pageWidget = QtWidgets.QWidget(tabWidget)
                    pageVboxLayout = QtWidgets.QVBoxLayout()
                    pageVboxLayout.setSpacing(0)
                    pageVboxLayout.setContentsMargins(*constants.NOTEBOOK_PAGE_MARGINS)
                    if modifReadonly:
                        pageWidget.setDisabled(True)
                    if nootebookIndex != 0:
                        self.notebookTabsNotComputed[nootebookIndex] = {'xmlPage': page, 'pageWidget': pageWidget}
                    self.computeRecursion(qvboxLayout=pageVboxLayout,
                                          xmlParent=page,
                                          nootebookIndex=nootebookIndex)
                    pageVboxLayout.addSpacerItem(QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
                    pageWidget.setLayout(pageVboxLayout)
                    tabIndex = tabWidget.addTab(pageWidget, pageString)
                    if not utils.isConstantModifier(invisible):
                        self.containerModifiers.append(
                            (invisible, partial(self._setTabHidden, tabWidget, tabIndex)))
                    nootebookIndex = nootebookIndex + 1
                qvboxLayout.addWidget(tabWidget)
                # tabWidget.currentChanged.connect(partial(self.computeNooteBookPage, tabWidget))
            elif childXmlTag == 'group':
                qvboxLayout.addLayout(row_container)
                row_container = QtWidgets.QHBoxLayout()
                row_container.setSpacing(0)
                self._computeGroup(childXlmElement, qvboxLayout)
            elif childXmlTag == 'button':
                buttonObj = button.Button(qtParent=self,
                                          xmlObject=childXlmElement,
                                          model=self.model,
                                          odooConnector=self.odooConnector)
                key = 'button_' + str(buttonObj.buttonName).replace(' ', '_')
                self.appendToglobalMapping(key, buttonObj)
                qvboxLayout.addWidget(buttonObj)
                divClass = xmlParent.attrib.get('class', '')
                if divClass == 'oe_button_box':
                    buttonObj.setHidden(True)
            elif childXmlTag == 'separator':
                childAttrs = childXlmElement.attrib
                separatorVal = childAttrs.get('string', '')
                if separatorVal:
                    labelObj = QtWidgets.QLabel(separatorVal)
                    labelObj.setStyleSheet(constants.LABEL_SEPARATOR)
                    qvboxLayout.addWidget(labelObj)
            elif childXmlTag == 'field':
                fieldQHLayout = self.computeField(childXlmElement)
                if fieldQHLayout:
                    row_container.addWidget(fieldQHLayout)
                    row_widget_count += 2
                    self.appendToglobalMapping('field_' + fieldQHLayout.fieldName, fieldQHLayout)
            elif childXmlTag == 'h1':
                self.computeRecursion(qvboxLayout=qvboxLayout,
                                      xmlParent=childXlmElement)
            elif childXmlTag == 'label':
                childAttrs = childXlmElement.attrib
                fieldRelated = childAttrs.get('for', False)
                if fieldRelated:
                    continue
                labelObj = False
                if fieldRelated:
                    labelObj = QtWidgets.QLabel()
                    self.aloneLabels[fieldRelated] = labelObj
                fieldRelated = childAttrs.get('string', False)
                if fieldRelated:
                    labelObj = QtWidgets.QLabel(fieldRelated)
                if labelObj:
                    labelObj.setStyleSheet(constants.LABEL_STYLE)
                    qvboxLayout.addWidget(labelObj)
            else:
                utils.logWarning('Tag %r not supported and not evaluated' % (childXlmElement))
            if row_widget_count >= row_widget_limit:
                row_widget_count = 0
                qvboxLayout.addLayout(row_container)
                row_container = QtWidgets.QHBoxLayout()
                row_container.setSpacing(0)
                # no more available on pyside row_container.setMargin(0)
        if constants.DEBUG:
            line = QtWidgets.QLineEdit()
            line.setStyleSheet("border:2px solid blue;")
            qvboxLayout.addWidget(line)
        if not row_container.parent():
            qvboxLayout.addLayout(row_container)
        return qvboxLayout

    # --- groups, laid out as Odoo lays them out ------------------------------
    #
    # A <group> holding only groups puts them side by side, one column each; a
    # <group> holding fields is a grid of `col` cells (2 by default), where a
    # field takes its label's cell and the ones after it -- `colspan` of them
    # in all, the label included, 2 by default, 1 with nolabel -- and starts a
    # new row when the row is full. `string` on a group is its title. The
    # labels sit in a column of their own, so they line up and the fields
    # start at the same place, which a row of label+field widgets never did.

    def _computeGroup(self, xmlGroup, parentLayout):
        layout = self._conditionalLayout(xmlGroup, parentLayout)
        title = xmlGroup.attrib.get('string')
        if title:
            titleLabel = QtWidgets.QLabel(title)
            titleLabel.setStyleSheet(constants.GROUP_TITLE_STYLE)
            layout.addWidget(titleLabel)
        children = [child for child in xmlGroup if isinstance(child.tag, str)]
        if children and all(child.tag == 'group' for child in children):
            columns = QtWidgets.QHBoxLayout()
            columns.setSpacing(constants.GROUP_COLUMN_SPACING)
            for child in children:
                column = QtWidgets.QVBoxLayout()
                column.setSpacing(0)
                column.setContentsMargins(0, 0, 0, 0)
                self._computeGroup(child, column)
                column.addStretch(1)
                columns.addLayout(column, 1)
            layout.addLayout(columns)
            return
        self._computeGroupGrid(xmlGroup, children, layout)

    def _computeGroupGrid(self, xmlGroup, children, layout):
        try:
            cols = max(1, int(xmlGroup.attrib.get('col', 2)))
        except ValueError:
            cols = 2
        grid = QtWidgets.QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(constants.GROUP_LABEL_SPACING)
        grid.setVerticalSpacing(constants.GROUP_ROW_SPACING)
        layout.addLayout(grid)
        cell = [0, 0]           # row, column

        def newRow():
            if cell[1]:
                cell[0] += 1
                cell[1] = 0

        def take(span):
            span = max(1, min(span, cols))
            if cell[1] + span > cols:
                newRow()
            at = (cell[0], cell[1])
            cell[1] += span
            if cell[1] >= cols:
                newRow()
            return at, span

        pendingLabel = None     # a <label for=...>: the next element is its field
        for child in children:
            tag = child.tag
            if tag == 'field':
                fieldObj = self.computeField(child)
                if not fieldObj:
                    continue
                self.appendToglobalMapping('field_' + fieldObj.fieldName, fieldObj)
                if self._alwaysInvisible(child):
                    layout.addWidget(fieldObj)      # hidden, and taking no cell
                    continue
                nolabel = utils.evaluateBoolean(child.attrib.get('nolabel', False)) \
                    or pendingLabel is not None
                span = self._colspan(child, 1 if nolabel else 2)
                label = self._takeFieldLabel(fieldObj, hide=nolabel)
                (row, column), span = take(span if pendingLabel is None else span + 1)
                if pendingLabel is not None:
                    grid.addWidget(pendingLabel, row, column)
                    pendingLabel = None
                    column += 1
                    span -= 1
                if label is not None and not nolabel:
                    grid.addWidget(label, row, column, QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
                    column += 1
                    span -= 1
                self._fillCell(fieldObj)
                grid.addWidget(fieldObj, row, column, 1, max(1, span))
            elif tag == 'label' and child.attrib.get('for'):
                pendingLabel = self._labelFor(child)
            elif tag == 'separator':
                newRow()
                text = child.attrib.get('string', '')
                if text:
                    separator = QtWidgets.QLabel(text)
                    separator.setStyleSheet(constants.GROUP_TITLE_STYLE)
                    grid.addWidget(separator, cell[0], 0, 1, cols)
                    cell[0] += 1
            else:
                # Anything else -- a group, a div, a notebook, a button -- is
                # laid out as before, in a cell of its own: after a <label for>
                # the one beside it, otherwise a whole row.
                holder = QtWidgets.QWidget(self)
                holderLayout = QtWidgets.QVBoxLayout(holder)
                holderLayout.setContentsMargins(0, 0, 0, 0)
                holderLayout.setSpacing(0)
                single = ElementTree.Element('single')
                single.append(child)
                if tag == 'group':
                    self._computeGroup(child, holderLayout)
                else:
                    self.computeRecursion(qvboxLayout=holderLayout, xmlParent=single)
                if pendingLabel is not None:
                    (row, column), span = take(self._colspan(child, 2))
                    grid.addWidget(pendingLabel, row, column)
                    grid.addWidget(holder, row, column + 1, 1, max(1, span - 1))
                    pendingLabel = None
                else:
                    newRow()
                    grid.addWidget(holder, cell[0], 0, 1, cols)
                    cell[0] += 1
        # the label columns as wide as their text, the field columns sharing the rest
        for column in range(cols):
            grid.setColumnStretch(column, 0 if column % 2 == 0 and cols > 1 else 1)

    @staticmethod
    def _fillCell(fieldObj):
        """The field as wide as its cell, as Odoo draws it: the stretch each
        field type puts after its input kept the input at its smallest width
        (a 120 pixel many2one beside a full-width char)."""
        fieldLayout = getattr(fieldObj, 'qtHorizontalWidget', None)
        if not isinstance(fieldLayout, QtWidgets.QLayout):
            return
        # The grid spaces its cells: the field keeps no margin of its own.
        fieldLayout.setContentsMargins(0, 0, 0, 0)
        for index in reversed(range(fieldLayout.count())):
            spacer = fieldLayout.itemAt(index).spacerItem()
            if spacer is not None and spacer.expandingDirections() & QtCore.Qt.Horizontal:
                fieldLayout.removeItem(spacer)
        # The room to the input, not to what sits beside it (the empty widget a
        # many2one keeps after its combo, its E button).
        inputs = (QtWidgets.QComboBox, QtWidgets.QLineEdit, QtWidgets.QAbstractSpinBox,
                  QtWidgets.QTextEdit, QtWidgets.QPlainTextEdit)
        for index in range(fieldLayout.count()):
            if isinstance(fieldLayout.itemAt(index).widget(), inputs):
                fieldLayout.setStretch(index, 1)
                break

    @staticmethod
    def _colspan(xmlElement, default):
        try:
            return int(xmlElement.attrib.get('colspan', default))
        except ValueError:
            return default

    @staticmethod
    def _alwaysInvisible(xmlElement):
        invisible = xmlElement.attrib.get('invisible')
        return invisible is not None and utils.isConstantModifier(invisible) \
            and bool(utils.evaluateExpression(invisible))

    def _labelFor(self, xmlLabel):
        """The text of a <label for="x"/>: its string, else the field's."""
        text = xmlLabel.attrib.get('string') or \
            self.fieldsNameTypeRel.get(xmlLabel.attrib.get('for'), {}).get('string', '')
        label = QtWidgets.QLabel(text)
        label.setStyleSheet(constants.LABEL_STYLE)
        return label

    def _takeFieldLabel(self, fieldObj, hide=False):
        """The field's own label, out of the field's layout so the grid can put
        it in the label column; with hide (nolabel), parked out of sight -- the
        field's setInvisible keeps showing and hiding it either way."""
        label = getattr(fieldObj, 'labelQtObj', None)
        if not isinstance(label, QtWidgets.QLabel):
            return None
        for layoutName in ('qtVBoxLayout', 'qtHorizontalWidget'):
            fieldLayout = getattr(fieldObj, layoutName, None)
            if isinstance(fieldLayout, QtWidgets.QLayout) and fieldLayout.indexOf(label) >= 0:
                fieldLayout.removeWidget(label)
                break
        if hide:
            label.setParent(self._labelParking())
            return None
        label.setParent(self)
        label.setHidden(fieldObj.isHidden())
        fieldObj.movedLabel = label
        return label

    def _labelParking(self):
        """A widget never shown: a label put there stays out of sight whatever
        setHidden the field's setInvisible calls on it."""
        parking = getattr(self, '_parkedLabels', None)
        if parking is None:
            parking = QtWidgets.QWidget(self)
            parking.setHidden(True)
            self._parkedLabels = parking
        return parking

    def _conditionalLayout(self, xmlElement, parentLayout):
        """The layout the children of a div or a group go into.

        Odoo 17 and later hide a whole block with `invisible` on its container
        -- "Potential duplicates", the company name of a person -- far more
        often than on the fields inside it. A layout cannot be hidden, so a
        container with an `invisible` gets a widget of its own, and the
        expression is kept to be evaluated against the record by
        _setFieldModifiers. One without it goes straight into the parent layout
        as it always did.
        """
        invisible = xmlElement.attrib.get('invisible')
        if invisible is None or (utils.isConstantModifier(invisible)
                                 and not utils.evaluateExpression(invisible)):
            return parentLayout
        container = QtWidgets.QWidget(self)
        layout = QtWidgets.QVBoxLayout(container)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        parentLayout.addWidget(container)
        if utils.isConstantModifier(invisible):
            # Always hidden: built all the same, since the fields inside still
            # hold values the other expressions read.
            container.setHidden(True)
        else:
            self.containerModifiers.append((invisible, container.setHidden))
        return layout

    def _setTabHidden(self, tabWidget, tabIndex, hidden):
        tabWidget.setTabVisible(tabIndex, not hidden)

    def _setContainerModifiers(self, values, context):
        for expression, setHidden in self.containerModifiers:
            setHidden(utils.evaluateExpression(expression, values, context))

    def computeHeader(self, archHeader, useHeader=False):
        mapping = {}

        def commonAppend(key, vals):
            if key not in mapping:
                mapping[key] = vals
            else:
                utils.logMessage('warning', 'multiple widgets with the same key: %r' % (key), 'computeHeader')

        # Two rows and not one: the buttons where Odoo puts them, and the
        # statusbar under them across the whole form. In Odoo it sits at the
        # right end of the same row; here it is the one thing in the header
        # worth the full width -- asked for on 2026-09-13 -- and a row of
        # chevrons squeezed next to three buttons reads as nothing at all.
        headerLayout = QtWidgets.QVBoxLayout()
        # No margin of its own, and set by hand: setLayoutMarginAndSpacing reads
        # a 0 as "no value given" and puts the default 6 back. Six above and six
        # below, twice over for the two layouts, is a band of empty space
        # between a title and the statusbar it belongs to -- and the band is
        # there even when the row holds nothing, which is every state whose
        # buttons the modifiers have hidden.
        headerLayout.setContentsMargins(0, 0, 0, 0)
        headerLayout.setSpacing(2)
        buttonsRow = QtWidgets.QHBoxLayout()
        buttonsRow.setContentsMargins(0, 0, 0, 0)
        buttonsRow.setSpacing(4)
        headerLayout.addLayout(buttonsRow)
        statusBars = []
        # useHeader 'statusbar': where the record is, and nothing to act on --
        # the form shows the state, the buttons stay out (an edit dialog).
        onlyStatus = useHeader == STATUSBAR_ONLY
        for xmlObj in archHeader:
            if onlyStatus and not (xmlObj.tag == 'field'
                                   and xmlObj.attrib.get('widget') == 'statusbar'):
                continue
            if xmlObj.tag == 'button':
                buttonObj = button.Button(qtParent=self,
                                          xmlObject=xmlObj,
                                          model=self.model,
                                          odooConnector=self.odooConnector)
                buttonsRow.addWidget(buttonObj)
                commonAppend('button_' + str(buttonObj.buttonString).replace(' ', '_'), buttonObj)
            elif xmlObj.tag == 'field':
                fieldObj = self.computeField(xmlObj)
                fieldQt = fieldObj
                fieldName = fieldObj.fieldName
                if not fieldQt:
                    utils.logMessage('warning', 'Qt field %r could not be loaded' % (fieldName), 'computeHeader')
                    continue
                if getattr(fieldObj, 'widget', '') == 'statusbar':
                    statusBars.append(fieldQt)
                elif isinstance(fieldQt, QtWidgets.QLayout):
                    buttonsRow.addLayout(fieldQt)
                elif isinstance(fieldQt, QtWidgets.QWidget):
                    buttonsRow.addWidget(fieldQt)
                else:
                    utils.logMessage('warning', 'Field %r could not be added to layout' % (fieldName), 'computeHeader')
                    continue
                commonAppend('field_' + str(fieldName), fieldObj)
            else:
                pass
        # The buttons stay where they were put, on the left, whatever room the
        # row is given.
        buttonsRow.addStretch(1)
        for statusBar in statusBars:
            headerLayout.addWidget(statusBar)
        return mapping, headerLayout

    def computeField(self, xmlObj, isChatterWidget=False):
        fieldAttributes = xmlObj.attrib
        fieldName = fieldAttributes.get('name', '')
        fieldDefinition = self.fieldsNameTypeRel.get(fieldName, {})
        fieldType = fieldDefinition.get('type', False)
        fieldObj = None
        if fieldType == 'selection':
            fieldObj = Selection(self, xmlObj, self.fieldsNameTypeRel, self.odooConnector, isChatterWidget)
        elif fieldType == 'char':
            fieldObj = Charachter(self, xmlObj, self.fieldsNameTypeRel, self.odooConnector, isChatterWidget)
        elif fieldType == 'integer':
            fieldObj = Integer(self, xmlObj, self.fieldsNameTypeRel, self.odooConnector, isChatterWidget)
        elif fieldType == 'float':
            fieldObj = Float(self, xmlObj, self.fieldsNameTypeRel, self.odooConnector, isChatterWidget)
        elif fieldType == 'datetime':
            fieldObj = Datetime(self, xmlObj, self.fieldsNameTypeRel, self.odooConnector, isChatterWidget)
        elif fieldType == 'many2one':
            fieldObj = Many2one(qtParent=self,
                                xmlField=xmlObj,
                                fieldsDefinition=self.fieldsNameTypeRel,
                                odooConnector=self.odooConnector,
                                isChatterWidget=isChatterWidget)
        elif fieldType == 'many2many':
            fieldObj = Many2many(qtParent=self,
                                 xmlField=xmlObj,
                                 fieldsDefinition=self.fieldsNameTypeRel,
                                 odooConnector=self.odooConnector,
                                 isChatterWidget=isChatterWidget)
        elif fieldType == 'text':
            fieldObj = Text(self, xmlObj, self.fieldsNameTypeRel, self.odooConnector, isChatterWidget)
        elif fieldType == 'date':
            fieldObj = Date(self, xmlObj, self.fieldsNameTypeRel, self.odooConnector, isChatterWidget)
        elif fieldType == 'boolean':
            fieldObj = Boolean(self, xmlObj, self.fieldsNameTypeRel, self.odooConnector, isChatterWidget)
        elif fieldType == 'one2many':
            fieldObj = One2many(qtParent=self,
                                xmlField=xmlObj,
                                fieldsDefinition=self.fieldsNameTypeRel,
                                odooConnector=self.odooConnector,
                                isChatterWidget=isChatterWidget)
        elif fieldType == 'binary':
            fieldObj = Binary(self, xmlObj, self.fieldsNameTypeRel, self.odooConnector, isChatterWidget)
        else:
            utils.logMessage('warning', 'Field %r not supported' % (fieldType), 'computeField')
        return fieldObj

    def computeNooteBookPage(self, tabObject, pageIndex=False):
#         tabObject.nootebook_changed_signal.emit(pageIndex)
#         return
        values = tabObject.get(pageIndex, {})
        if values:
            del tabObject[pageIndex]
            self.nootebook_changed_signal.emit(pageIndex)

    def computeChatter(self, divVlay, childElement):
        self.chatterLay = QtWidgets.QVBoxLayout()
        self.chatterButton = QtWidgets.QPushButton('↓↓↓   Show Chatter   ↓↓↓')
        self.chatterButton.setStyleSheet(constants.BUTTON_STYLE + constants.VIOLET_BACKGROUND)
        self.chatterButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.chatterButton.clicked.connect(self.showChatter)
        self.chatterWidgets = []
        count = 0
        for fieldObj in childElement:
            if fieldObj.tag == 'field':
                qtWidgetField = self.computeField(fieldObj, isChatterWidget=True)
                if qtWidgetField:
                    if isinstance(qtWidgetField, QtWidgets.QLayout):
                        self.chatterLay.insertLayout(0, qtWidgetField)
                        if count == 0:
                            self.chatterLay.insertSpacerItem(0, QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum))
                            count = count + 1
                    elif isinstance(qtWidgetField, QtWidgets.QWidget):
                        self.chatterLay.insertWidget(0, qtWidgetField)
                        qtWidgetField.hide()
                        self.chatterWidgets.append(qtWidgetField)
                    self.appendToglobalMapping('field_' + qtWidgetField.fieldName, qtWidgetField)
            else:
                utils.logMessage('warning', 'Unable to compute tag in chatter %r' % (fieldObj.tag), 'computeChatter')
        self.chatterLay.insertWidget(0, self.chatterButton)
        utilsUi.setLayoutMarginAndSpacing(self.chatterLay, constants.LAY_OUT_SPACING + 20)
        self.chatterLay.setSpacing(constants.LAY_OUT_SPACING)
        divVlay.addLayout(self.chatterLay)

    @utilsUi.rpcErrorBoundary
    def showChatter(self):
        for chatterWidget in self.chatterWidgets:
            chatterWidget.showChatterWidget()
        self.chatterButton.hide()

    @utilsUi.rpcErrorBoundary
    def updateDataStructure(self, pageIndex=0):
        utils.logDebug('compute Notebook fields: %r' % (pageIndex), 'updateDataStructure')
        if pageIndex > 0 and pageIndex in self.nootebookFieldsToCompute:
            dictFieldsToUpdate = self.nootebookFieldsToCompute[pageIndex]
            fieldNamesToUpdate = list(dictFieldsToUpdate.keys())
            self.loadIds(self.activeIds, {}, {}, {}, fieldNamesToUpdate, True)

    def setDefaults(self, fieldsToRead=[]):
        if not fieldsToRead:
            fieldsToRead = list(self.interfaceFieldsDict.keys())
        if fieldsToRead:
            self.fieldDefaultVals = self.odooConnector.rpc_connector.defaultGet(self.model, fieldsToRead)
            self.skipOnChange = True
            if self.fieldDefaultVals:
                for fieldName, fieldVal in list(self.fieldDefaultVals.items()):
                    self.setValueField(fieldName, fieldVal)
                    self._valueChanged(fieldName)
        else:
            logging.warning("unable to load default field from model %s " % self.model)
        self.skipOnChange = False

    def removeNootebookFields(self, fieldsToRead):
        mainDict = {}
        for fieldsDict in list(self.nootebookFieldsToCompute.values()):
            mainDict.update(fieldsDict)
        for fieldName in list(mainDict.keys()):
            if fieldName in fieldsToRead:
                fieldsToRead.remove(fieldName)
        return fieldsToRead

    @utils.timeit
    def loadIds(self,
                objIds=[],
                forceFieldValues={},
                readonlyFields={},
                invisibleFields={},
                fieldsToRead=[],
                skipRemoveNootebook=False):
        """
        refresh the user interface with the given odooid
        """
        if objIds is None or not objIds:
            objIds = []
        if isinstance(objIds, int):
            objIds = [objIds]
        self.activeIds = objIds
        if not fieldsToRead:
            fieldsToRead = list(self.interfaceFieldsDict.keys())
        if not skipRemoveNootebook:
            fieldsToRead = self.removeNootebookFields(fieldsToRead)
        if len(objIds) > 1:
            utilsUi.popWarning(None, 'You cannot load multiple ids on form or search view!')
            return False
        fromId = False
        if objIds:
            fromId = objIds[0]
            formVals = self.odooConnector.rpc_connector.read(self.model, fieldsToRead, [fromId], {'lang': self.odooConnector.activeLanguage})
            if not formVals:
                utils.logMessage('warning', 'No values found for id %r and model %r' % (fromId, self.model), 'loadIds')
                fromId = False
                self.skipOnChange = True
                self.setDefaults()
                self.skipOnChange = False
            else:
                self.skipOnChange = True
                self.formVals = formVals[0]
                for fieldName, fieldVal in list(self.formVals.items()):
                    self.setValueField(fieldName, fieldVal)
                    self.setFieldParentAttrs(fieldName)
                for button in self.buttons.__dict__.values():
                    button.odooId=fromId
                self.skipOnChange = False
        else:
            self.setDefaults(fieldsToRead)
        
        for fieldName, fieldVal in list(forceFieldValues.items()):
            self.setValueField(fieldName, fieldVal, )

        # The modifiers of the record just loaded, before what the caller
        # forces below, so that what the caller forces wins.
        self._setFieldModifiers()

        for readonlyField, fieldAttr in list(readonlyFields.items()):
            self.setReadonlyField(readonlyField, fieldAttr)
        
        for invisibleField, fieldAttr in list(invisibleFields.items()):
            self.setInvisibleField(invisibleField, fieldAttr)
        
        self._setButtonsModifiers()
        self.objectsInit = copy.copy(self.fields)
        self.form_changed.emit("Reloaded")

    def setFieldParentAttrs(self, fieldName):
        fieldObj = self.interfaceFieldsDict.get(fieldName, None)
        if not fieldObj:
            utils.logMessage('warning', 'Field %r not found in the local fields' % (fieldName), 'setValueField')
        else:
            fieldObj.setParentAttrs(self.activeIds, self.model)

    def _setFieldModifiers(self):
        fieldDict = self.interfaceFieldsDict
        # What the record holds, for the expressions Odoo 17 and later send in
        # place of the modifiers -- see utils.widgetModifier.
        values = utils.recordValues(fieldDict, getattr(self, 'formVals', {}))
        for fieldObj in list(fieldDict.values()):
            client_context = dict(self.odooConnector.rpc_connector.contextUser)
            client_context.update(utils.evaluateContext(fieldObj.context, fieldDict))
            val = utils.widgetModifier(fieldObj, 'readonly', fieldDict,
                                       values, client_context)
            if val is None:
                fieldObj.setReadonly(fieldObj.readonly)
            else:
                fieldObj.setReadonly(val)
                self.commonEval(val, self.readonlyFields, fieldObj)
            val = utils.widgetModifier(fieldObj, 'invisible', fieldDict,
                                       values, client_context)
            if val is None:
                fieldObj.setInvisible(fieldObj.invisible)
            else:
                fieldObj.setInvisible(val)
                self.commonEval(val, self.invisibleFields, fieldObj)
            # Required is a modifier like the other two from 17 onwards, and
            # this is the list the save dialog reads before letting a save go.
            val = utils.widgetModifier(fieldObj, 'required', fieldDict,
                                       values, client_context)
            if val is not None:
                fieldObj.required = val
            if fieldObj.required:
                self.requiredFields[fieldObj.fieldName] = fieldObj
            elif fieldObj.fieldName in self.requiredFields:
                del self.requiredFields[fieldObj.fieldName]
        self._setContainerModifiers(values, dict(self.odooConnector.rpc_connector.contextUser))

    def checkRequiredFieldsEvaluated(self, showMessage=False):
        fieldsToEvaluate = []
        message = 'These required fields needs to be evaluated:'
        for fieldObject in list(self.requiredFields.values()):
            if not fieldObject.value and not isinstance(fieldObject.value, (int, float)):
                fieldsToEvaluate.append(fieldObject.fieldStringInterface)
                message = message + '\n %r' % (fieldObject.fieldStringInterface)
        if showMessage and fieldsToEvaluate:
            utilsUi.popWarning(None, message)
        return fieldsToEvaluate

    def setInvisibleField(self, fieldName, val=False):
        fieldObj = self.interfaceFieldsDict.get(fieldName, None)
        if not fieldObj:
            utils.logMessage('warning', f'Field {fieldName} not found in the local fields', 'setInvisibleField')
            return
        fieldObj.setInvisible(val)
        self.commonEval(val, self.invisibleFields, fieldObj)
    
    def setReadonlyField(self, fieldName, val=False):
        fieldObj = self.interfaceFieldsDict.get(fieldName, None)
        if not fieldObj:
            utils.logMessage('warning', 'Field %r not found in the local fields' % (fieldName), 'setReadonlyField')
            return
        fieldObj.setReadonly(val)
        self.commonEval(val, self.readonlyFields, fieldObj)

    def commonEval(self, val, localDict, fieldObj):
        if val:
            localDict[fieldObj.fieldName] = fieldObj
        else:
            if fieldObj.fieldName in list(localDict.keys()):
                del localDict[fieldObj.fieldName]

    def getAllOnChange(self):
        outDict = {}
        for fieldName, fieldObject in list(self.interfaceFieldsDict.items()):
            outDict[fieldName] = fieldObject.on_change
        return outDict
    
    #: The field types the onchange of Odoo 17 and later is not sent, and is not
    #: asked about.
    ONCHANGE_LEFT_OUT = ('one2many', 'many2many', 'binary')

    def _on_change(self, fieldName):
        '''
            [
            [id],
            {all values},
            launcher field name,
            {All form on_changes},
            {context},
            ]
        '''
        if self.skipOnChange:
            return {}
        rpc = self.odooConnector.rpc_connector
        if rpc.serverVersion >= 17:
            fieldType = self.fieldsNameTypeRel.get(fieldName, {}).get('type')
            if fieldType in self.ONCHANGE_LEFT_OUT:
                # Not in the values the onchange is sent (see
                # _onchangeValuesAndSpec), and the server pops the fields that
                # changed from those values: asked about one of these it
                # answers KeyError (a project added to a product, Odoo 19,
                # 2026-11-25). Their own server onchange is not run.
                return {}
            values, fieldsSpec = self._onchangeValuesAndSpec()
            result = rpc.onchange(self.model, self.activeIds, values, [fieldName], fieldsSpec)
            result = dict(result) if isinstance(result, dict) else {}
            result['value'] = {name: utils.onchangeValueToWidget(value)
                               for name, value in (result.get('value') or {}).items()}
            return result
        allVals = self.getAllFieldsValues()
        allOnchanges = self.getAllOnChange()
        return rpc.on_change(self.model, self.activeIds, allVals, fieldName, allOnchanges, {})

    def _onchangeValuesAndSpec(self):
        """What the onchange of Odoo 17 and later is sent: values and spec.

        One2many, many2many and binary fields are left out of both. What is not
        sent the server takes from the record as it is stored, which is what
        these widgets hold until the form is saved; and they are not asked back,
        since an x2many answers in commands these widgets do not read.
        """
        values = {}
        fieldsSpec = {}
        for name, fieldObj in list(self.interfaceFieldsDict.items()):
            fieldName = name[7:] if name.startswith('header_') else name
            fieldType = self.fieldsNameTypeRel.get(fieldName, {}).get('type') \
                or getattr(fieldObj, 'fieldType', '')
            if fieldType in self.ONCHANGE_LEFT_OUT:
                continue
            try:
                value = utils.widgetValueToOnchange(fieldObj.value, fieldType)
            except ValueError:
                continue
            values[fieldName] = value
            if fieldType == 'many2one':
                fieldsSpec[fieldName] = {'fields': {'display_name': {}}}
            else:
                fieldsSpec[fieldName] = {}
        return values, fieldsSpec

    def addToObject(self):
        fieldIdentifier = 'field_'
        buttonIdentifier = 'button_'
        for key, obj in list(self.mappingInterface.items()):
            if key.startswith(fieldIdentifier):
                newKey = key.replace(fieldIdentifier, '')
                self.interfaceFieldsDict[newKey] = obj
                obj.value_changed_signal.connect(self._valueChanged)
                obj.translation_clicked.connect(self.translationDial)
            elif key.startswith(buttonIdentifier):
                newKey = key.replace(buttonIdentifier, '')
                self.buttons.__dict__[newKey] = obj
        return True

    def _valueChangedExt(self, fieldName):
        '''
            To allow external oveload
        '''
        pass

    @utilsUi.rpcErrorBoundary
    def _valueChanged(self, fieldName):
        fieldName = str(fieldName)
        fieldObj = self.interfaceFieldsDict.get(fieldName)
        if not fieldObj:
            utils.logMessage('warning', 'Field %r not found in interfacefieldsdict' % (fieldName), '_valueChanged')
            return
        changeResult = self._on_change(fieldObj.fieldName)
        changedValues = changeResult.get('value', {})
        # The server answers with everything the change leads to, cascade
        # included: setting those values must not send one onchange per field.
        skipOnChange, self.skipOnChange = self.skipOnChange, True
        try:
            for fieldNameFromServer, fieldValueFromServer in list(changedValues.items()):
                fieldObj1 = self.interfaceFieldsDict.get(str(fieldNameFromServer))
                if fieldObj1 is None:
                    continue
                fieldObj1.setValue(fieldValueFromServer)
                if self._isSavable(fieldObj1):
                    self.fieldsChanged[fieldObj1.fieldName] = fieldObj1
        finally:
            self.skipOnChange = skipOnChange
        # skipOnChange is up while the form writes values itself -- a record
        # being loaded, the defaults, an onchange answer. Those are not changes
        # to save: marked, a record just opened wrote back twenty fields, the
        # server's readonly ones among them.
        if not skipOnChange and self._isSavable(fieldObj):
            self.fieldsChanged[fieldName] = fieldObj
        self._setFieldModifiers()
        self._valueChangedExt(fieldName)

    def _isSavable(self, fieldObj):
        """Whether a change to the field is one to write, as the web client sees it.

        Not a field the server defines readonly, nor one a modifier makes
        readonly on this record -- unless the view says force_save.
        """
        if str(getattr(fieldObj, 'fieldXmlAttributes', {}).get('force_save', '')).lower() in ('1', 'true'):
            return True
        attributes = getattr(fieldObj, 'fieldXmlAttributes', {})
        viewDecides = (getattr(fieldObj, 'modifiers', {}) or {}).get('readonly') \
            or 'readonly' in attributes
        definition = self.fieldsNameTypeRel.get(fieldObj.fieldName, {})
        if definition.get('readonly') is True and not viewDecides:
            # A view that says readonly for the field -- `states` up to 16, an
            # expression from 17 -- has the last word, and readonlyFields holds
            # what it said for this record.
            return False
        return fieldObj.fieldName not in self.readonlyFields

    @utilsUi.rpcErrorBoundary
    def translationDial(self, fieldName):
        if not self.activeIds:
            utilsUi.popWarning(None, 'Translations are available only on already created records.')
            return
        fieldName = str(fieldName)
        fieldObj = self.interfaceFieldsDict.get(fieldName)

        def acceptTransDial():
            translationDial.accept()

        def rejectTransDial():
            translationDial.reject()

        translationDial = QtWidgets.QDialog()
        mainLay = QtWidgets.QVBoxLayout()
        tableWidget = QtWidgets.QTableWidget()
        model = self.model
        if model == 'product.product':
            model = 'product.template'
        translationName = str(model + ',' + fieldName)
        filterList = [('res_id', '=', self.activeIds[0]),
                      ('name', '=', translationName)
                      ]
        headers = ['Source value', 'Translated Value', 'Language', 'Name']
        fieldNames = ['source', 'translated', 'lang', 'name']
        values = []
        translationObj = 'ir.translation'
        res = self.odooConnector.rpc_connector.readSearch(translationObj, ['src', 'value', 'lang'], filterList)
        if not res:
            res = []
            installedLangs = self.odooConnector.rpc_connector.readSearch('res.lang', ['code', 'name'], [('active', '=', True)])
            for resDict in installedLangs:
                code = resDict.get('code', '')
                createDict = {
                    'type': 'model',
                    'value': fieldObj.value,
                    'state': 'translated',
                    'module': '',
                    'res_id': self.activeIds[0],
                    'name': translationName,
                    'src': fieldObj.value,
                    'lang': code,
                }
                transId = self.odooConnector.rpc_connector.create(translationObj, createDict)
                createDict['id'] = transId
                res.append(createDict)
        for elemDict in res:
            src = elemDict.get('src', '')
            value = elemDict.get('value', '')
            lang = elemDict.get('lang', '')
            values.append([src, value, lang, translationName])
        tableFlags = {1: QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable,
                      }
        utilsUi.commonPopulateTable(headers, values, tableWidget, tableFlags)
        mainLay.addWidget(tableWidget)
        layButtons, okButt, cancelButt = utilsUi.getButtonBox()
        okButt.clicked.connect(acceptTransDial)
        cancelButt.clicked.connect(rejectTransDial)
        mainLay.addLayout(layButtons)
        translationDial.setLayout(mainLay)
        translationDial.resize(800, 400)
        tableWidget.resizeColumnsToContents()
        tableWidget.horizontalHeader().setStretchLastSection(True)
        if translationDial.exec() == QtWidgets.QDialog.Accepted:
            rowsDict = utils.getRowsFromTableWidget(tableWidget, 'dict', fieldNames)
            for rowDict in list(rowsDict.values()):
                elemId = False
                translated = str(rowDict.get('translated', ''))
                source = str(rowDict.get('source', ''))
                lang = str(rowDict.get('lang', ''))
                for elem in res:
                    sourceRel = elem.get('src', '')
                    langRel = elem.get('lang', '')
                    if source == sourceRel and lang == langRel:
                        elemId = elem.get('id', False)
                        break
                if elemId:
                    self.odooConnector.rpc_connector.write(translationObj, {'value': translated}, [elemId])
                    if lang == self.activeLanguageCode:
                        self.setValueField(fieldName, translated)

    def appendToglobalMapping(self, key, value):
        self.globalMapping.update({key: value})

    def save(self):
        """
        save the current values
        """
        to_write = {}
        if self.activeIds:
            for k, v in self.fieldsChanged.items():
                fieldObj1 = self.interfaceFieldsDict.get(k)
                if fieldObj1.fieldType in ['one2many','many2many']:
                    to_write[k] = [(6, False, v.value)]
                else:
                    to_write[k] = v.value
            self.odooConnector.rpc_connector.write(self.model, to_write,  self.activeIds)
        else:
            for k, v in self.getAllFieldsValues().items():
                fieldObj1 = self.interfaceFieldsDict.get(k)
                if fieldObj1.fieldType in ['one2many','many2many']:
                    to_write[k] = [(6, False, v)]
                else:
                    to_write[k] = v
            self.activeIds = self.odooConnector.rpc_connector.create(self.model, to_write)
        return self.activeIds
