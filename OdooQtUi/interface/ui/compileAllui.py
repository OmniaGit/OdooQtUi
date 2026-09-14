# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011-2026 OmniaSolutions and the OdooQtUi contributors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of OdooQtUi, released under the Apache License 2.0.
# Redistributions must keep the attribution in the NOTICE file.
# See the LICENSE and NOTICE files at the root of the project.

'''
Created on 03/ott/2012
@author: mboscolo
'''
import os
import sys
import glob
import subprocess
import logging


def getPyFileName(uiFile):
    fromUiFileName = os.path.basename(uiFile).split('.')[0]
    fromUiFileName = "ui_" + fromUiFileName + ".cythonize_odooplm"
    return os.path.join(os.path.dirname(uiFile), fromUiFileName)


srcPath = os.path.join(os.path.dirname(__file__), "*.ui")


for fromFile in glob.glob(srcPath):
    toFile = getPyFileName(fromFile)
    if not os.path.exists(fromFile):

        logging.warning("File %s dose not exsists" % fromFile)
        continue
    if sys.platform.find('linux') > 0 or ('linux' in sys.platform) > 0:
        cmd = r'python /usr/lib/python2.7/dist-packages/PyQt4/uic/pyuic.cythonize_odooplm -o %s %s' % (toFile, fromFile)
    else:
        cmd = r'pyuic4 -o %s  %s' % (toFile, fromFile)
        #  seems that subprocess dose not finds the python side package dir
        cmd = r'C:\Python27\Lib\site-packages\PyQt4\pyuic4.bat -o %s %s' % (toFile, fromFile)
    print ("Execute", cmd)
    subprocess.call(cmd)
