# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011-2026 OmniaSolutions and the OdooQtUi contributors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of OdooQtUi, released under the Apache License 2.0.
# Redistributions must keep the attribution in the NOTICE file.
# See the LICENSE and NOTICE files at the root of the project.

"""The screenshots of the README, taken again from a running Odoo.

Every example of the README's quick start is opened on the real display, in a
process of its own (a theme is applied once per process), and its window is
captured with the frame the window manager draws around it:

    login          OdooQtUi/images/login.png
    form           OdooQtUi/images/res_partner.png
    list           OdooQtUi/images/product_list.png
    theme          OdooQtUi/images/res_partner_theme.png

    python tools/make_screenshots.py --db V19E_demo
    python tools/make_screenshots.py --db V19E_demo --only list theme

It needs a display (X11 or Wayland session, not offscreen) and an Odoo server
with the demo data the examples read: a res.partner to show (--partner) and
some product.product records. Nothing is written to the server.

The login dialog is opened with an application name of its own, so no stored
server, user or password of the machine shows in the picture.
"""

import argparse
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES = os.path.join(ROOT, 'OdooQtUi', 'images')

#: example name -> image file name
EXAMPLES = {
    'login': 'login.png',
    'form': 'res_partner.png',
    'list': 'product_list.png',
    'theme': 'res_partner_theme.png',
}

#: The palette of the README's "Make it yours" example.
THEME = {'primary': '#1f4e79', 'accent': '#e67e22'}

#: Time for the window manager to place and decorate a window, and for Qt to paint it.
CAPTURE_DELAY_MS = 3000


def arguments(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('--server', default='localhost')
    parser.add_argument('--port', type=int, default=8069)
    parser.add_argument('--scheme', default='http')
    parser.add_argument('--protocol', default='xmlrpc', choices=['xmlrpc', 'jsonrpc'])
    parser.add_argument('--db', required=True, help='the database the examples read')
    parser.add_argument('--user', default='admin')
    parser.add_argument('--password', default='admin')
    parser.add_argument('--partner', type=int, default=7, help='the res.partner shown in the form')
    parser.add_argument('--output', default=IMAGES, help='where the images are written')
    parser.add_argument('--only', nargs='+', choices=sorted(EXAMPLES), help='take these only')
    parser.add_argument('--example', help=argparse.SUPPRESS)    # the child process
    return parser.parse_args(argv)


def main(argv=None):
    options = arguments(argv)
    if options.example:
        return shoot(options)
    os.makedirs(options.output, exist_ok=True)
    failed = []
    for example in options.only or list(EXAMPLES):
        command = [sys.executable, os.path.abspath(__file__), '--example', example,
                   '--server', options.server, '--port', str(options.port),
                   '--scheme', options.scheme, '--protocol', options.protocol,
                   '--db', options.db, '--user', options.user, '--password', options.password,
                   '--partner', str(options.partner), '--output', options.output]
        print('%-6s -> %s' % (example, os.path.join(options.output, EXAMPLES[example])))
        if subprocess.call(command, cwd=ROOT) != 0:
            failed.append(example)
    if failed:
        print('failed: %s' % ', '.join(failed))
        return 1
    return 0


def shoot(options):
    """Open one example, capture its window, quit."""
    sys.path.insert(0, ROOT)
    from PySide6 import QtCore, QtWidgets

    app = QtWidgets.QApplication(sys.argv[:1])
    if options.example == 'theme':
        # Before the connector: it applies the palette in force when it is built.
        from OdooQtUi import theme
        theme.load(THEME)
    from OdooQtUi.connector import MainConnector

    if options.example == 'login':
        from OdooQtUi.interface.login import LoginDialComplete
        connector = MainConnector(app_name='OdooQtUi-screenshot')
        window = LoginDialComplete(app_name='OdooQtUi-screenshot', odooConnector=connector)
        # Filled in as a user would, rather than empty.
        window.lineEdit_scheme.setText(options.scheme)
        window.lineEdit_server.setText(options.server)
        window.lineEdit_port.setText(str(options.port))
        window.comboBox_conn_type.setCurrentIndex(max(0, window.comboBox_conn_type.findText(options.protocol)))
    else:
        connector = MainConnector()
        connector.loginWithUser(options.user, options.password, options.db,
                                xmlrpcServerIP=options.server, xmlrpcPort=options.port,
                                scheme=options.scheme, loginType=options.protocol)
        if not connector.userLogged:
            print('unable to log in to %s:%s database %s' % (options.server, options.port, options.db))
            return 1
        version = connector.odoo_version
        if options.example in ('form', 'theme'):
            form = connector.initFormViewObj('res.partner')
            form.loadIds([options.partner])
            suffix = ' with a custom theme' if options.example == 'theme' else ''
            window = _dialog('OdooQtUi - res.partner %s%s (Odoo %s)' % (options.partner, suffix, version),
                             form, 1000, 800, scroll=True)
        else:
            products = connector.initTreeListViewObject('product.product', viewFilter=True)
            products.loadForceEmptyIds()
            window = _dialog('OdooQtUi - product.product list with search (Odoo %s)' % version,
                             products, 1100, 650)

    window.setWindowFlags(window.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
    window.show()
    window.raise_()
    window.activateWindow()
    output = os.path.join(options.output, EXAMPLES[options.example])
    result = {}

    def capture():
        frame = window.frameGeometry()
        pixmap = window.screen().grabWindow(0, frame.x(), frame.y(), frame.width(), frame.height())
        result['saved'] = pixmap.save(output)
        app.quit()

    QtCore.QTimer.singleShot(CAPTURE_DELAY_MS, capture)
    app.exec()
    return 0 if result.get('saved') else 1


def _dialog(title, widget, width, height, scroll=False):
    from PySide6 import QtWidgets
    window = QtWidgets.QDialog()
    window.setWindowTitle(title)
    layout = QtWidgets.QVBoxLayout(window)
    if scroll:
        area = QtWidgets.QScrollArea()
        area.setWidgetResizable(True)
        area.setWidget(widget)
        widget = area
    layout.addWidget(widget)
    window.resize(width, height)
    return window


if __name__ == '__main__':
    sys.exit(main())
