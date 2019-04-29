from PySide2 import QtWidgets# Welcome On Odoo Qt Project

The project intend to get a fully qt ui version for odoo, providing form a search view to be used in non web environment, like Allocation extension.

![License Logo](https://bytebucket.org/mboscolo/odoo_qt/raw/7216755696e0cd8e0726fa86239aa8290788be93/OdooQtUi/images/lgplv3-147x51.png)


[bitbucket](https://bitbucket.org/mboscolo/odoo_qt.git)


Here's an example of some Python code to show an odoo Login Form:

![Login](https://bytebucket.org/mboscolo/odoo_qt/raw/7216755696e0cd8e0726fa86239aa8290788be93/OdooQtUi/images/Login.png)


```python
import sys
from PySide2 import QtWidgets
from OdooQtUi.connector import MainConnector

app = QtWidgets.QApplication(sys.argv)
connectorObj = MainConnector()
connectorObj.loginWithDial()    # Perform show of the login form


app.exec_()

```

Here's an example of some Python code to show an odoo Form:
![Selection_115.png](https://bitbucket.org/repo/b8adjr/images/1135319991-Selection_115.png)

```python

import sys
from PySide2 import QtWidgets
from OdooQtUi.connector import MainConnector

app = QtWidgets.QApplication(sys.argv)
connectorObj = MainConnector()
connectorObj.loginWithDial()    # Perform show of the login form

tmplViewObj = connectorObj.initFormViewObj('product.template')
tmplViewObj.loadIds([10])   # Edit Form on product.teplate with id =10

dialog = QtWidgets.QDialog()
lay = QtWidgets.QVBoxLayout()
lay.addWidget(tmplViewObj)
dialog.setLayout(lay)
dialog.exec_()
app.exec_()

```


Here's an example of some Python code to show a odoo tree view:
![Selection_118.png](https://bitbucket.org/repo/b8adjr/images/514502163-Selection_118.png)

```python
import sys
from PySide2 import QtWidgets
from OdooQtUi.connector import MainConnector

app = QtWidgets.QApplication(sys.argv)
connectorObj = MainConnector()
connectorObj.loginWithDial()    # Perform show of the login form

tmplViewObj = tryListView('product.template', viewFilter=True)

dialog = QtWidgets.QDialog()
lay = QtWidgets.QVBoxLayout()
lay.addWidget(tmplViewObj)
dialog.setLayout(lay)
dialog.exec_()
app.exec_()

```


Have fun!


[Github-flavored Markdown](https://guides.github.com/features/mastering-markdown/)
to write your content.
