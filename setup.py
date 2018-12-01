# -*- encoding: utf-8 -*-

import os
import sys
import datetime
import tempfile
import py2exe
import shutil
from distutils.core import setup
sys.argv.append("py2exe")
project_folder = os.path.dirname(os.getcwd())
sys.path.append(project_folder)
dist_dir = os.path.join(os.getcwd(), "dist")
build_dir = os.path.join(os.getcwd(), "build")
# sys.path.append(r"C:\Windows\WinSxS\x86_microsoft.vc90.crt_1fc8b3b9a1e18e3b_9.0.21022.8_none_bcb86ed6ac711f91")
# for p in sys.path:
#     print p
# ...
# ModuleFinder can't handle runtime changes to __path__, but win32com uses them
currentDir = os.path.dirname(__file__)


try:
    # py2exe 0.6.4 introduced a replacement modulefinder.
    # This means we have to add package paths there, not to the built-in
    # one.  If this new modulefinder gets integrated into Python, then
    # we might be able to revert this some day.
    # if this doesn't work, try import modulefinder
    try:
        import py2exe.mf as modulefinder
    except ImportError:
        import modulefinder
    import win32com
    for p in win32com.__path__[1:]:
        modulefinder.AddPackagePath("win32com", p)
    for extra in ["win32com.shell", "win32com.client.Variant"]: #,"win32com.mapi"
        __import__(extra)
        m = sys.modules[extra]
        for p in m.__path__[1:]:
            modulefinder.AddPackagePath(extra, p)
except ImportError:
    # no build path setup, no worries.
    pass

now=datetime.datetime.now()
dllList = ['mfc90.dll', 'msvcp90.dll', 'qtnetwork.pyd','qtxmlpatterns4.dll','qtsvg4.dll']
# origIsSystemDLL = py2exe.build_exe.isSystemDLL
# 
# def isSystemDLL(pathname):
#     if os.path.basename(pathname).lower() in dllList:
#         return 0
#     return origIsSystemDLL(pathname)
# py2exe.build_exe.isSystemDLL = isSystemDLL

def getAllFile(fromFolder):
    out = []
    for fileName in os.listdir(fromFolder):
        out.append(os.path.join(fromFolder,fileName ))
    return out

def getListOfFile(fromFolder):
    return getAllFile(os.path.join(os.path.dirname(__file__),
                                   "setupSupportFile",
                                   fromFolder))

data_files = [
              ]

packages = ['OdooQtUi']

dll_excludes = ["mswsock.dll",
                "powrprof.dll",
                'shfolder.dll',
                'credui.dll',
                'secur32.dll'
                ]

includes = [
            'xml.etree.ElementTree',
            'sip',
            'OdooQtUi']

ignores = ['PyKDE4.kdecore',
           'PyKDE4.kdeui', 
           'ElementTree',
           'elementtree.ElementTree',
           'Pyro.core',
           'pywin',
           'pywin.dialogs',
           'pywin.dialogs.list',
           'psycopg2',
           ]


excludes = ['psycopg2',
            'M2Crypto.SSL', 
            'M2Crypto.SSL.Checker', 
            'Pyro.core', 
            '_scproxy', 
            "Tkconstants",
            "Tkinter",
            "tcl",
            'numpy',
            'PySide']


class Target:
    def __init__(self, **kw):
        self.__dict__.update(kw)
        # for the version info resources (Properties -- Version)
        self.version = now.strftime('%Y.%m.%d')
        self.company_name = "Daniel Smerghetto"
        self.name = "OdooQtUi"

com_server_target = Target(
    description = "OdooQtUi",
    modules = [],
    create_exe = False,
    create_dll = True,
    )

setup(name="Application",
      # the following two parameters embed support files within exe/dll file
      options={'build': {'build_base': build_dir},
               "py2exe": {'bundle_files': 3, 
                          'ignores': ignores,
                          'excludes': excludes,
                          'includes': includes,
                          'dll_excludes': dll_excludes,
                          'dist_dir' : dist_dir,
                          'packages' : packages,
                          'compressed' : True,
                       },
    },
    zipfile=None,
    version=now.strftime('%Y.%m.%d'),
    description="OdooQtUi",
    # author, maintainer, contact go here:
    data_files=data_files,
    author="Daniel Smerghetto",
    author_email="re_dan@hotmail.it",
    com_server=[com_server_target],
   )

