# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011-2026 OmniaSolutions and the OdooQtUi contributors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of OdooQtUi, released under the Apache License 2.0.
# Redistributions must keep the attribution in the NOTICE file.
# See the LICENSE and NOTICE files at the root of the project.

"""One palette, and every window takes its colours from it.

The colours used to be written into `constants.py`, forty of them, inside fifty
stylesheet strings -- so changing the look of the client meant editing the
library, and a customer could not change it at all. Here they are named once:

    primary        what the product is recognised by, and what a header carries
    primary_dark   the same, pressed or hovered
    on_primary     what is legible on top of it
    background     behind a window
    surface        a dialog, a form, a field
    text / muted   what is written on a surface, and what is written faintly
    border         the line around a box
    field_border   the line under an editable field
    required       a field the server will refuse without
    danger / ok    a refusal and an agreement
    accent         the one thing on a form that should catch the eye
    selection      the row the user is on

Three ways to change them, in the order they are read:

    theme.load({'primary': '#005f73'})          a dictionary, from code
    theme.load('C:/.../theme.json')             a file, per installation
    set ODOOQTUI_THEME=C:/.../theme.json        the same file, per machine

and `theme.apply()` puts the result on the running application. `MainConnector`
calls it once when it is built, so an application that uses this library is
styled without doing anything; one that wants its own colours calls `load()`
before it, and one that wants none of it passes `auto=False` there.

Nothing here imports the rest of the library: constants reads the palette, not
the other way round.
"""

import json
import logging
import os
from string import Template

logger = logging.getLogger("odooqtui.theme")

#: Where a machine points at its own palette without a line of code.
ENVIRONMENT = 'ODOOQTUI_THEME'

#: OmniaSolutions, read off the official logo
#: (logo_omnia_definitivo_2018_10_18.png): the red of the O, the darker
#: red of its shadow, and the black of `Solutions`.
DEFAULT = {
    'primary': '#ff0505',
    'primary_dark': '#7f1718',
    'on_primary': '#ffffff',
    'background': '#f4f4f5',
    'surface': '#ffffff',
    'text': '#111827',
    'muted': '#6b7280',
    'border': '#d1d5db',
    'field_border': '#cfcfcf',
    'required': '#d2d2ff',
    'danger': '#94313d',
    'ok': '#2e7d32',
    'accent': '#00a09d',
    'selection': '#ddedf0',
}

#: What the application gets when nobody has styled a widget by hand. Short on
#: purpose: every widget that sets its own stylesheet wins over this one, so a
#: long sheet here would be mostly a lie about what is on the screen.
STYLESHEET = """
QWidget { color: $text; }
QDialog, QMainWindow { background-color: $background; }
QToolTip { background-color: $surface; color: $text; border: 1px solid $border; }
QTreeView, QTableWidget, QListWidget { alternate-background-color: $selection;
                                       selection-background-color: $primary;
                                       selection-color: $on_primary; }
QHeaderView::section { background-color: $background; color: $text;
                       border: none; border-bottom: 1px solid $border;
                       padding: 4px; }
QProgressBar { text-align: center; border: 1px solid $border; border-radius: 5px;
               background-color: $surface; }
QProgressBar::chunk { background-color: $primary; }
QScrollBar::handle:horizontal, QScrollBar::handle:vertical { background-color: $muted; }
"""

_palette = dict(DEFAULT)
_applied = False


def palette():
    """The colours as they stand."""
    return dict(_palette)


def colour(name, default=''):
    """One colour by name, and what to use when the palette has no such name."""
    return _palette.get(name) or default


#: The other spelling, so a caller can use either.
color = colour


def load(source=None):
    """Read a palette over the one in force.

    :source a dictionary, or the path of a json file holding one. None reads
            the path in the environment, which is how a machine is restyled
            without touching the installation.
    :return the palette as it now stands.

    What it cannot read it leaves alone and says so: a theme is decoration, and
    a broken one must not stop a client from starting.
    """
    global _palette
    source = source if source is not None else os.environ.get(ENVIRONMENT)
    if not source:
        return palette()
    values = source
    if not isinstance(values, dict):
        try:
            with open(source, 'r') as handle:
                values = json.load(handle)
        except Exception as error:
            logger.warning("the theme %r could not be read: %s", source, error)
            return palette()
    if not isinstance(values, dict):
        logger.warning("the theme %r is not a set of names and colours", source)
        return palette()
    unknown = [name for name in values if name not in DEFAULT]
    if unknown:
        # Kept, not refused: a customer stylesheet may name colours of its own.
        logger.info("the theme names colours this library does not use: %s",
                    ", ".join(sorted(unknown)))
    _palette.update((str(name), str(value)) for name, value in values.items()
                    if value)
    return palette()


def style(template):
    """A stylesheet with its $names filled in.

    `string.Template` and not `%` or `format`: a stylesheet is full of braces
    and percent signs, and both of those would have to be escaped everywhere
    they are meant literally.
    """
    return Template(template).safe_substitute(_palette)


def stylesheet():
    """The application wide sheet, in the colours in force."""
    return style(STYLESHEET)


def apply(target=None, force=False):
    """Put the sheet on the application, or on one widget.

    :target a QApplication or a QWidget. None is the running application.
    :force  apply it again even if it has been applied already -- which is what
            a change of palette at run time needs.
    :return whether anything was styled.
    """
    global _applied
    if _applied and target is None and not force:
        return False
    if target is None:
        try:
            from PySide6 import QtWidgets
        except ImportError as error:
            logger.warning("no Qt to style: %s", error)
            return False
        target = QtWidgets.QApplication.instance()
    if target is None:
        return False
    target.setStyleSheet(stylesheet())
    _applied = True
    return True


def reset():
    """Back to the colours this library ships with. For the tests."""
    global _palette, _applied
    _palette = dict(DEFAULT)
    _applied = False
