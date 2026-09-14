# OdooQtUi

**Native Qt desktop applications on top of Odoo — without rewriting a single view.**

[![PyPI](https://img.shields.io/pypi/v/OdooQtUi.svg)](https://pypi.org/project/OdooQtUi/)
[![Python](https://img.shields.io/pypi/pyversions/OdooQtUi.svg)](https://pypi.org/project/OdooQtUi/)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/OmniaGit/OdooQtUi/blob/main/LICENSE)

OdooQtUi reads the **form, list and search views straight from your Odoo
server** and renders them as real PySide6 widgets. Fields, notebooks, header
buttons, `invisible`/`readonly`/`required` conditions, onchanges and the
chatter all come from the server — you just drop the widget into your window.

Change a view in Odoo, and your desktop app follows. No XML to duplicate, no
forms to hand-draw.

```python
form = connector.initFormViewObj('res.partner')
form.loadIds([7])          # a live, editable Odoo form in your Qt window
```

<p align="center">
  <img src="https://raw.githubusercontent.com/OmniaGit/OdooQtUi/main/OdooQtUi/images/res_partner.png" alt="The res.partner form of Odoo 19 rendered by OdooQtUi" width="720">
  <br>
  <em>The code above, run against Odoo 19: the partner form as the server defines it, notebook and one2many lists included.</em>
</p>

---

## Why OdooQtUi?

The Odoo web client is great in a browser. Some applications don't live in a
browser:

- **Desktop integrations** — a CAD, a machine, a scale, a label printer, a
  local file system: talk to them from Python *and* show Odoo data in the same
  window.
- **Plugins inside other software** — embed an Odoo form in any Qt-based host
  application.
- **Kiosks and shop-floor stations** — a focused, native UI that exposes only
  what the operator needs.
- **Your own UX, Odoo's business logic** — build a custom window, and still let
  the server decide which fields exist, which are required and which buttons are
  allowed.

It is not a toy: OdooQtUi is the UI layer of
[OdooPLM](https://odooplm.omniasolutions.website), the PLM client that connects
SolidWorks, Inventor, FreeCAD and other CADs to Odoo, used in production.

## Features

| | |
|---|---|
| **Views** | Form (groups, notebooks, header, button box, chatter) · List with pagination · Search with filters · Tree |
| **Fields** | `char` · `text` · `integer` · `float` · `boolean` · `date` · `datetime` · `selection` · `binary` · `many2one` · `many2many` · `one2many` |
| **Behaviour** | `invisible` / `readonly` / `required` conditions · onchange · header buttons calling server methods · statusbar · create and save |
| **Connection** | XML‑RPC and JSON‑RPC, over HTTP or HTTPS · ready-made login dialog · optional stored credentials |
| **Look & feel** | One palette for the whole app, set from code, a JSON file or an environment variable |
| **Low level** | A thin RPC client (`search`, `read`, `write`, `create`, `delete`, any model method) you can use on its own |

## Installation

```bash
pip install OdooQtUi
```

Requires Python 3.12+ and PySide6 (installed automatically). You need access to
an Odoo server — if you don't have one, the
[official Docker image](https://hub.docker.com/_/odoo) starts one in a minute.

## Quick start

### 1. Log in

```python
import sys
from PySide6 import QtWidgets
from OdooQtUi.connector import MainConnector

app = QtWidgets.QApplication(sys.argv)

connector = MainConnector()
if not connector.loginWithDial():      # shows the Odoo login dialog
    sys.exit("Login cancelled")
```

<p align="center">
  <img src="https://raw.githubusercontent.com/OmniaGit/OdooQtUi/main/OdooQtUi/images/login.png" alt="The OdooQtUi login dialog" width="360">
</p>

Prefer no dialog? Log in from code, over XML‑RPC or JSON‑RPC:

```python
connector.loginWithUser('admin', 'admin', 'my_database',
                        xmlrpcServerIP='localhost', xmlrpcPort=8069,
                        scheme='http', loginType='jsonrpc')
assert connector.userLogged
```

### 2. Show an Odoo form

```python
form = connector.initFormViewObj('res.partner', useHeader=True, useChatter=True)
form.loadIds([7])                      # load the record with id 7

window = QtWidgets.QDialog()
QtWidgets.QVBoxLayout(window).addWidget(form)
window.resize(1000, 700)
window.exec()

form.save()                            # write the changes back to Odoo
```

`form.loadIds([])` opens an empty form filled with the server defaults, and
`save()` then creates the record.

### 3. Show a list with a search bar

```python
products = connector.initTreeListViewObject('product.product', viewFilter=True)
products.loadForceEmptyIds()           # first page of records

window = QtWidgets.QDialog()
QtWidgets.QVBoxLayout(window).addWidget(products)
window.exec()

print(products.getSelectedIds())
```

<p align="center">
  <img src="https://raw.githubusercontent.com/OmniaGit/OdooQtUi/main/OdooQtUi/images/product_list.png" alt="product.product list with the search bar, Odoo 19" width="720">
</p>

Double-click a row to open its form. Pass `deafult_filter=[('sale_ok', '=', True)]`
to restrict what the list shows.

Need a specific view? Every `init…` method accepts `viewName='…'` or `view_id=…`.

### 4. Talk to Odoo directly

The same connection gives you the plain RPC calls:

```python
rpc = connector.rpc_connector
ids = rpc.search('res.partner', [('is_company', '=', True)], limit=10)
for partner in rpc.read('res.partner', ['name', 'email'], ids):
    print(partner['name'], partner['email'])

rpc.write('res.partner', {'phone': '+39 041 000000'}, ids[:1])
rpc.callCustomMethod('sale.order', 'action_confirm', [[42]])
```

### 5. Make it yours

Load a palette **before** creating the connector:

```python
from OdooQtUi import theme

theme.load({'primary': '#1f4e79', 'accent': '#e67e22'})
# or theme.load('my_theme.json'), or set ODOOQTUI_THEME=/path/to/my_theme.json
connector = MainConnector()
```

<p align="center">
  <img src="https://raw.githubusercontent.com/OmniaGit/OdooQtUi/main/OdooQtUi/images/res_partner_theme.png" alt="The res.partner form with the palette above" width="720">
  <br>
  <em>The same partner form with the palette above: the accent on the buttons, the primary colour on the tabs.</em>
</p>

The available colour names are listed in
[`OdooQtUi/theme.py`](OdooQtUi/theme.py).

## Odoo compatibility

| Odoo | Status |
|---|---|
| 19 | Supported |

Older Odoo versions are not officially supported by this release.

## How it works

```
Odoo server ──fields_view_get──▶ view arch (XML) + field definitions
                                        │
                                        ▼
                             OdooQtUi parsers (views/)
                                        │
                                        ▼
                  one Qt widget per field type (objects/<type>/)
                                        │
                  read / write / onchange / buttons over RPC (RPC/)
```

- `OdooQtUi/connector.py` — `MainConnector`, the entry point: login and view factories.
- `OdooQtUi/views/` — form, list, search and tree views, built from the arch.
- `OdooQtUi/objects/` — one small widget per Odoo field type.
- `OdooQtUi/RPC/` — XML‑RPC and JSON‑RPC clients behind a single `RpcConnection`.
- `OdooQtUi/theme.py`, `OdooQtUi/widgets/` — palette and reusable widgets such as `StatusBar`.

## Contributing

Contributions are very welcome — and the codebase is friendly to newcomers:
every Odoo field type is a small, self-contained widget under
`OdooQtUi/objects/`, so adding support for a missing one (`monetary`, `html`,
`many2many_tags`, radio buttons…) is a perfect first pull request.

```bash
git clone https://github.com/OmniaGit/OdooQtUi.git
cd OdooQtUi
pip install -e .
python -m unittest discover -s test -p "test_*.py"   # no Odoo server needed
```

Found a bug or have an idea? [Open an issue](https://github.com/OmniaGit/OdooQtUi/issues).
Code, comments and commit messages are written in English.

## License

[Apache License 2.0](LICENSE) — use, modify and redistribute OdooQtUi freely,
in open source and proprietary applications alike.

The one requirement is attribution: any redistribution or derivative work must
keep the [NOTICE](NOTICE) file, or reproduce its credits in its documentation or
"About" box, naming OdooQtUi and its authors.

Copyright 2011-2026 [OmniaSolutions](https://omniasolutions.website) and the
OdooQtUi contributors — Daniel Smerghetto, Matteo Boscolo, Jayraj Thakkar.
