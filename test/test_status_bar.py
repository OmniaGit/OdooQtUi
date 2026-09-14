# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011-2026 OmniaSolutions and the OdooQtUi contributors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of OdooQtUi, released under the Apache License 2.0.
# Redistributions must keep the attribution in the NOTICE file.
# See the LICENSE and NOTICE files at the root of the project.

"""The statusbar widget: what it lays out, and what it colours.

The painting itself is not tested -- a screenshot is the only honest test of
that -- but everything the painting is made of is: where each chevron begins
and ends, which one is the current state, which of them are behind it, and what
a click lands on. Those are the parts that can be wrong in a way that looks
right on the developer's screen and wrong on a wider dialog.

    cd OdooQtUi && python -m unittest discover -s test -p "test_*.py"

Qt without a screen: the platform is forced to offscreen below, so this runs on
a machine with no display and inside a test runner.
"""

import os
import subprocess
import sys
import unittest

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Asked in a process of its own, and not in a try: a Qt that cannot find a
# platform plugin does not raise, it prints and calls qFatal -- so a machine
# with a broken or headless Qt did not fail this file, it killed the whole run
# before the tests that need no Qt at all had a chance.
_PROBE = subprocess.call(
    [sys.executable, '-c',
     'import os;os.environ.setdefault("QT_QPA_PLATFORM","offscreen");'
     'from PySide6 import QtWidgets;QtWidgets.QApplication([])'],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
if _PROBE:
    raise unittest.SkipTest("no Qt that can open a window here")

from PySide6 import QtWidgets

from OdooQtUi.widgets import status_bar
from OdooQtUi.widgets.status_bar import StatusBar

APPLICATION = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

STATES = [('draft', 'Draft'), ('confirmed', 'Confirmed'),
          ('released', 'Released'), ('obsoleted', 'Obsoleted')]


class States(unittest.TestCase):

    def test_pairs_are_kept_as_they_come(self):
        bar = StatusBar(states=STATES)
        self.assertEqual(bar.states, STATES)

    def test_bare_values_get_a_label_of_their_own(self):
        # What a view that carries statusbar_visible and nothing else gives us.
        bar = StatusBar(states=['draft', 'in_progress'])
        self.assertEqual(bar.states, [('draft', 'Draft'),
                                      ('in_progress', 'In Progress')])

    def test_an_empty_state_is_not_a_state(self):
        # ''.split(',') answers [''], which is how the old row of labels came to
        # draw one empty box.
        self.assertEqual(StatusBar(states=['', None, 'draft']).states,
                         [('draft', 'Draft')])

    def test_the_current_one_is_the_one_it_was_given(self):
        bar = StatusBar(states=STATES, current='released')
        self.assertEqual(bar.current, 'released')
        bar.setCurrent('draft')
        self.assertEqual(bar.current, 'draft')


class Bounds(unittest.TestCase):
    """The chevrons fill the width they are given, to the last pixel."""

    def setUp(self):
        self.bar = StatusBar(states=STATES, current='confirmed')

    def test_they_start_at_the_left_margin_and_end_at_the_right_one(self):
        for width in (240, 800, 1013, 1920):
            bounds = self.bar._bounds(width)
            self.assertEqual(bounds[0][0], 0, width)
            self.assertEqual(bounds[-1][1], width, width)

    def test_no_pixel_is_lost_between_two_of_them(self):
        # Rounding each one on its own would leave a gap that grows with the
        # number of states, and the last chevron short of the margin.
        for width in (241, 799, 1013):
            bounds = self.bar._bounds(width)
            for before, after in zip(bounds, bounds[1:]):
                self.assertEqual(before[1], after[0], width)

    def test_nothing_to_lay_out(self):
        self.assertEqual(StatusBar()._bounds(800), [])
        self.assertEqual(self.bar._bounds(0), [])

    def test_the_chevron_points_the_way(self):
        points = self.bar._chevron(200, 28)
        self.assertEqual(len(points), 3)
        self.assertEqual([point.x() for point in points],
                         [200, 200 + status_bar.ARROW, 200])
        self.assertEqual(points[1].y(), 14)

    def test_the_box_of_a_middle_state_is_bounded_by_two_chevrons(self):
        # Its left edge is the separator in front of it and its right edge the
        # point into the state after: that is what makes the row read as one
        # arrow rather than as four labels.
        box = self.bar._currentPath(1, 200, 400, 28).boundingRect()
        self.assertEqual(box.left(), 200)
        self.assertEqual(box.right(), 400 + status_bar.ARROW)

    def test_the_first_and_the_last_stop_at_the_margins(self):
        first = self.bar._currentPath(0, 0, 200, 28).boundingRect()
        self.assertEqual(first.left(), 0)
        last = self.bar._currentPath(len(STATES) - 1, 600, 800, 28).boundingRect()
        self.assertEqual(last.right(), 800)


class Colours(unittest.TestCase):
    """Where the record is, where it has been, and where it may go."""

    def setUp(self):
        self.bar = StatusBar(states=STATES, current='released')

    def _ink(self, value):
        return self.bar._textColour(self.bar._indexOf(value), value).name()

    def test_the_current_state_is_the_one_that_stands_out(self):
        self.assertEqual(self._ink('released'), status_bar.CURRENT_TEXT)
        self.assertEqual(self.bar._accent().name(), status_bar.CURRENT_COLOUR)

    def test_what_is_behind_and_what_is_ahead_are_told_apart(self):
        self.assertEqual(self._ink('draft'), status_bar.DONE_TEXT)
        self.assertEqual(self._ink('confirmed'), status_bar.DONE_TEXT)
        self.assertEqual(self._ink('obsoleted'), status_bar.TODO_TEXT)

    def test_a_state_nobody_is_in(self):
        # Everything is ahead when the record is in none of them.
        bar = StatusBar(states=STATES, current='')
        self.assertEqual(bar._textColour(0, 'draft').name(), status_bar.TODO_TEXT)

    def test_the_view_may_colour_a_state_itself(self):
        # statusbar_colors, which Odoo writes as bootstrap names.
        self.bar.setColours({'released': 'green'})
        self.assertEqual(self.bar._accent().name(),
                         status_bar.NAMED_COLOURS['green'])

    def test_a_colour_it_does_not_know(self):
        self.bar.setColours({'released': 'chartreuse'})
        self.assertEqual(self.bar._accent().name(), status_bar.CURRENT_COLOUR)


class Clicks(unittest.TestCase):

    def setUp(self):
        self.bar = StatusBar(states=STATES, current='draft')
        self.bar.resize(800, status_bar.HEIGHT)

    def test_a_point_belongs_to_the_chevron_it_is_in(self):
        self.assertEqual(self.bar._at(10), 'draft')
        self.assertEqual(self.bar._at(210), 'confirmed')
        self.assertEqual(self.bar._at(799), 'obsoleted')

    def test_past_the_end_is_the_last_one(self):
        # The point of the last chevron is drawn beyond its own width.
        self.assertEqual(self.bar._at(5000), 'obsoleted')


if __name__ == '__main__':
    unittest.main(verbosity=2)
