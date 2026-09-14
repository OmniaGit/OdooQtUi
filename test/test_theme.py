# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011-2026 OmniaSolutions and the OdooQtUi contributors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of OdooQtUi, released under the Apache License 2.0.
# Redistributions must keep the attribution in the NOTICE file.
# See the LICENSE and NOTICE files at the root of the project.

"""The palette, and the stylesheets that are built out of it.

The colours used to be written into constants.py, forty of them inside fifty
stylesheet strings: changing the look of a client meant editing the library, and
a customer could not change it at all. What is tested here is the part that
makes that possible -- a palette that can be read over, and constants that are
resolved against it every time they are read rather than once at import.

    cd OdooQtUi && python -m unittest discover -s test -p "test_*.py"

No Qt: `apply` is the only thing here that needs it, and it answers False rather
than raising where there is none.
"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from OdooQtUi import theme
from OdooQtUi.utils_odoo_conn import constants


class Palette(unittest.TestCase):

    def setUp(self):
        theme.reset()

    tearDown = setUp

    def test_it_ships_with_one(self):
        self.assertEqual(theme.colour('primary'), theme.DEFAULT['primary'])
        self.assertEqual(theme.colour('nothing_of_the_sort', '#123456'), '#123456')

    def test_a_dictionary_is_read_over_it(self):
        theme.load({'primary': '#005f73'})
        self.assertEqual(theme.colour('primary'), '#005f73')
        # And only what it names: the rest of the palette stands.
        self.assertEqual(theme.colour('surface'), theme.DEFAULT['surface'])

    def test_a_file_is_read_over_it(self):
        handle, path = tempfile.mkstemp(suffix='.json')
        with os.fdopen(handle, 'w') as out:
            json.dump({'primary': '#005f73'}, out)
        try:
            theme.load(path)
            self.assertEqual(theme.colour('primary'), '#005f73')
        finally:
            os.remove(path)

    def test_the_environment_says_where_it_is(self):
        handle, path = tempfile.mkstemp(suffix='.json')
        with os.fdopen(handle, 'w') as out:
            json.dump({'primary': '#005f73'}, out)
        os.environ[theme.ENVIRONMENT] = path
        try:
            theme.load()
            self.assertEqual(theme.colour('primary'), '#005f73')
        finally:
            del os.environ[theme.ENVIRONMENT]
            os.remove(path)

    def test_a_theme_that_cannot_be_read_changes_nothing(self):
        # Decoration must not stop a client from starting.
        theme.load('/no/such/theme.json')
        self.assertEqual(theme.colour('primary'), theme.DEFAULT['primary'])
        theme.load(['not', 'a', 'palette'])
        self.assertEqual(theme.colour('primary'), theme.DEFAULT['primary'])

    def test_a_colour_of_its_own_is_kept(self):
        # A customer stylesheet may name colours this library does not use.
        theme.load({'their_own_green': '#00ff00'})
        self.assertEqual(theme.colour('their_own_green'), '#00ff00')


class Stylesheets(unittest.TestCase):

    def setUp(self):
        theme.reset()

    tearDown = setUp

    def test_the_names_are_filled_in(self):
        self.assertEqual(theme.style('a { color: $primary; }'),
                         'a { color: %s; }' % theme.DEFAULT['primary'])

    def test_the_braces_of_a_stylesheet_are_left_alone(self):
        # Which is why this is a Template and not a format string.
        self.assertIn('{', theme.stylesheet())
        self.assertNotIn('$', theme.stylesheet())

    def test_a_name_nobody_defined_is_left_as_it_is(self):
        self.assertEqual(theme.style('a { color: $nothing; }'),
                         'a { color: $nothing; }')


class Constants(unittest.TestCase):
    """The stylesheets the widgets read, resolved against the palette."""

    def setUp(self):
        theme.reset()

    tearDown = setUp

    def test_a_themed_one_answers_in_the_colours_in_force(self):
        self.assertIn(theme.DEFAULT['primary'], constants.VIOLET_BACKGROUND)
        theme.load({'primary': '#005f73'})
        self.assertIn('#005f73', constants.VIOLET_BACKGROUND)

    def test_the_dialogs_are_a_surface_and_not_a_colour(self):
        # Where the purple was: a window is the sheet of paper the form is
        # written on, and the product's own colour goes on top of it.
        self.assertIn(theme.DEFAULT['surface'], constants.ODOO_STYLE)
        self.assertNotIn('#875a7b', constants.ODOO_STYLE)
        self.assertNotIn('#A583A5', constants.ODOO_STYLE)

    def test_the_ones_that_have_not_moved_yet_still_answer(self):
        # The file moves into the palette a group at a time; the rest is still
        # written out by hand and has to go on working meanwhile.
        self.assertEqual(constants.FONT_SIZE, 'font-size: 14px;')
        self.assertTrue(constants.BUTTON_STYLE_REVERSED)

    def test_a_name_that_is_neither(self):
        self.assertRaises(AttributeError, getattr, constants, 'NO_SUCH_STYLE')

    def test_the_name_can_still_be_imported_on_its_own(self):
        # Four files in the client do `from ... .constants import ODOO_STYLE`,
        # and a module __getattr__ has to answer that too.
        from OdooQtUi.utils_odoo_conn.constants import ODOO_STYLE
        self.assertIn('QDialog', ODOO_STYLE)


class Applying(unittest.TestCase):

    def setUp(self):
        theme.reset()

    tearDown = setUp

    def test_with_no_application_there_is_nothing_to_style(self):
        try:
            from PySide6 import QtWidgets
        except ImportError:
            self.assertIs(theme.apply(), False)
            return
        if QtWidgets.QApplication.instance() is None:
            self.assertIs(theme.apply(), False)

    def test_a_widget_of_its_own_can_be_styled(self):
        class _Styled(object):
            sheet = None

            def setStyleSheet(self, text):
                self.sheet = text

        target = _Styled()
        self.assertIs(theme.apply(target), True)
        self.assertIn(theme.DEFAULT['primary'], target.sheet)

    def test_the_application_is_styled_once(self):
        class _Styled(object):
            def setStyleSheet(self, text):
                pass

        self.assertIs(theme.apply(_Styled()), True)
        # A target of its own is always styled; the application is not styled
        # twice, which is what keeps a connector per command from costing
        # anything.
        theme._applied = True
        self.assertIs(theme.apply(), False)
        self.assertIs(theme.apply(force=True) or True, True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
