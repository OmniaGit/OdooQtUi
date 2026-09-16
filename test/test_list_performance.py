# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011-2026 OmniaSolutions and the OdooQtUi contributors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of OdooQtUi, released under the Apache License 2.0.
# Redistributions must keep the attribution in the NOTICE file.
# See the LICENSE and NOTICE files at the root of the project.

"""What a list costs: the calls it makes and the columns it reads.

Profiled on 2026-09-16 against a development database, and these are the three
findings turned into tests:

- a page of 40 products was 325 KB instead of 14 KB, because the list read
  `image_1920` -- a column no cell can draw, since the value arrives as base64
  and is put in the table as text;
- every call costs about a tenth of a second whatever it carries, and
  `fields_get` of product.product (116 KB, 156 ms) was asked for again at every
  window;
- the paging buttons searched the default filter, so paging after a search
  silently gave back the whole table.

    cd OdooQtUi && python -m unittest discover -s test -p "test_*.py"

No server: the RPC layer is replaced by a recorder.
"""

import os
import sys
import unittest

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from OdooQtUi.RPC.rpc import RpcConnection
from OdooQtUi.views.tree_list_obj import TemplateTreeListView


class RecordingSocket(object):
    """The transport, counting what it was asked for."""

    def __init__(self):
        self.fields_get_calls = []

    def fieldsGet(self, obj, attributesToRead=None, context={}):
        self.fields_get_calls.append((obj, attributesToRead))
        return {'name': {'type': 'char'}}


class FieldsGetCache(unittest.TestCase):

    def setUp(self):
        self.connection = RpcConnection()
        self.connection.sockInstance = RecordingSocket()

    def test_the_same_model_is_asked_for_once(self):
        first = self.connection.fieldsGet('product.product')
        second = self.connection.fieldsGet('product.product')
        self.assertIs(first, second)
        self.assertEqual(len(self.connection.sockInstance.fields_get_calls), 1)

    def test_another_model_is_another_answer(self):
        self.connection.fieldsGet('product.product')
        self.connection.fieldsGet('ir.attachment')
        self.assertEqual([obj for obj, _attributes
                          in self.connection.sockInstance.fields_get_calls],
                         ['product.product', 'ir.attachment'])

    def test_asking_for_some_attributes_is_a_different_question(self):
        self.connection.fieldsGet('product.product')
        self.connection.fieldsGet('product.product', ['string', 'type'])
        self.assertEqual(len(self.connection.sockInstance.fields_get_calls), 2)

    def test_another_language_is_another_answer(self):
        self.connection.fieldsGet('product.product')
        self.connection.contextUser['lang'] = 'it_IT'
        self.connection.fieldsGet('product.product')
        self.assertEqual(len(self.connection.sockInstance.fields_get_calls), 2)

    def test_logging_out_forgets_it(self):
        self.connection.fieldsGet('product.product')
        self.connection.clearCache()
        self.connection.fieldsGet('product.product')
        self.assertEqual(len(self.connection.sockInstance.fields_get_calls), 2)


class ColumnsRead(unittest.TestCase):
    """_fieldsToRead: the columns of the view, minus what no cell can draw."""

    def _view(self, ordered, types):
        view = TemplateTreeListView.__new__(TemplateTreeListView)
        view.labelsOrdered = ordered
        view.__dict__['fieldsNameTypeRel'] = types
        return view

    def test_a_binary_column_is_not_read(self):
        view = self._view(['image_1920', 'name', 'engineering_code'],
                          {'image_1920': {'type': 'binary'},
                           'name': {'type': 'char'},
                           'engineering_code': {'type': 'char'}})
        self.assertEqual(view._fieldsToRead(), ['name', 'engineering_code'])

    def test_an_image_column_is_not_read_either(self):
        view = self._view(['preview', 'preview_related', 'name'],
                          {'preview': {'type': 'image'},
                           'preview_related': {'type': 'image'},
                           'name': {'type': 'char'}})
        self.assertEqual(view._fieldsToRead(), ['name'])

    def test_everything_else_is_read_in_the_order_of_the_view(self):
        columns = ['name', 'engineering_revision', 'checkout_user', 'write_date']
        view = self._view(columns, {name: {'type': 'char'} for name in columns})
        self.assertEqual(view._fieldsToRead(), columns)

    def test_a_column_the_model_does_not_describe_is_still_read(self):
        # A button column, or a field the view names and fields_get does not
        # know: read it rather than drop a column silently.
        view = self._view(['name', 'mystery'], {'name': {'type': 'char'}})
        self.assertEqual(view._fieldsToRead(), ['name', 'mystery'])


class ImageColumns(unittest.TestCase):
    """Which columns are pictures, and which field is read to draw them."""

    class _Element(object):
        def __init__(self, tag, **attrib):
            self.tag = tag
            self.attrib = attrib

    def _view(self, ordered, types, elements, modelFields=None):
        """A list view with its arch, and the model behind it.

        The two are not the same thing, and the difference is the point of
        _imageFieldFor: a list that shows image_1920 does not mention image_128,
        which the model has all the same.
        """
        # `model` and `fieldsNameTypeRel` are properties reading the view
        # definition, so the stand-in overrides them in a subclass.
        fields = types if modelFields is None else modelFields

        class _View(TemplateTreeListView):
            model = 'a.model'
            fieldsNameTypeRel = types

        view = _View.__new__(_View)
        view.labelsOrdered = ordered
        view.treeObj = type('tree', (), {'widgets_to_add_in_line': elements})()
        connection = type('rpc', (), {'fieldsGet': staticmethod(lambda model: fields)})()
        view.odooConnector = type('connector', (), {'rpc_connector': connection})()
        return view

    def test_a_field_asked_for_as_an_image_is_a_picture_column(self):
        view = self._view(['image_1920', 'name'],
                          {'image_1920': {'type': 'image'}, 'name': {'type': 'char'}},
                          {0: self._Element('field', widget='image'),
                           1: self._Element('field')},
                          modelFields={'image_1920': {'type': 'image'},
                                       'image_128': {'type': 'image'},
                                       'name': {'type': 'char'}})
        # image_128 and not image_1920: the cell is 60 pixels, and the big one is
        # four times the bytes for no more pixels on screen.
        self.assertEqual(view._imageColumns(), {0: 'image_128'})

    def test_without_the_widget_it_is_not_drawn(self):
        view = self._view(['datas', 'name'],
                          {'datas': {'type': 'binary'}, 'name': {'type': 'char'}},
                          {0: self._Element('field'), 1: self._Element('field')})
        self.assertEqual(view._imageColumns(), {})

    def test_a_button_column_is_never_a_picture(self):
        view = self._view(['toggle_check_out'], {},
                          {0: self._Element('button', widget='image')})
        self.assertEqual(view._imageColumns(), {})

    def test_a_model_without_the_small_sizes_keeps_its_own_field(self):
        # ir.attachment's preview has no siblings: it is read as it is.
        view = self._view(['preview'], {'preview': {'type': 'image'}},
                          {0: self._Element('field', widget='image')})
        self.assertEqual(view._imageColumns(), {0: 'preview'})


class Paging(unittest.TestCase):
    """pagingFilter: what the < and > buttons search for."""

    def _view(self, default_filter):
        view = TemplateTreeListView.__new__(TemplateTreeListView)
        view.deafult_filter = default_filter
        view.currentFilter = None
        return view

    def test_without_a_search_the_default_filter_pages(self):
        view = self._view([('is_plm', '=', True)])
        self.assertEqual(view.pagingFilter(), [('is_plm', '=', True)])

    def test_after_a_search_the_user_domain_pages(self):
        view = self._view([('is_plm', '=', True)])
        view.currentFilter = [('engineering_code', 'ilike', 'ABC'),
                              ('is_plm', '=', True)]
        self.assertEqual(view.pagingFilter(), view.currentFilter)

    def test_an_empty_search_is_a_search(self):
        # [] means "everything", and it is not the same as never having
        # searched: a user who clears the box expects the whole table back.
        view = self._view([('is_plm', '=', True)])
        view.currentFilter = []
        self.assertEqual(view.pagingFilter(), [])


if __name__ == '__main__':
    unittest.main()
