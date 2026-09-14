# Changelog

All notable changes to this project are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project uses [Semantic Versioning](https://semver.org/).

## [0.1.0] — Unreleased

First release of the PySide6 / Odoo 19 generation of the library.

### Added
- Odoo 19 support: `list` view type and expression-based `invisible` /
  `readonly` / `required` modifiers.
- JSON-RPC connection (`jsonrpc`, `secure-jsonrpc`) alongside XML-RPC.
- Theming: one palette for the whole application, set with `theme.load()`
  from a dict or a JSON file, or through the `ODOOQTUI_THEME` environment variable.
- `StatusBar` widget (`OdooQtUi.widgets.status_bar`), the Odoo form header
  statusbar drawn as chevrons.
- Offline test suite under `test/` (no Odoo server needed).
- `pyproject.toml` packaging with complete metadata.
- `OdooQtUi.RPC.errors`: `OdooRpcError`, `OdooServerError`,
  `OdooConnectionError`; `utilsUi.showRpcError` and the `rpcErrorBoundary`
  decorator for Qt slots.
- Many2one fields search the server as the user types (`name_search` with the
  field's domain and context, 8 proposals).
- `tools/make_screenshots.py` takes the README screenshots again.
- GitHub Actions: tests and build on every push, PyPI release on a version tag.

### Changed
- **License changed to Apache 2.0** (previously LGPL v3, with some sources
  carrying GPL / AGPL headers). The code can be reused freely, provided the
  attribution in the `NOTICE` file is kept. Every source file now carries an
  SPDX header.
- **A failed RPC call raises `OdooRpcError`** instead of opening a dialog
  from the RPC layer and returning `None`. Code that tested the result for
  `None` must catch the exception; Qt slots can use `rpcErrorBoundary`.
  `forceHideInterface`, `forceRaise_error`, `setXmlRpcError` and `raise_error`
  are still accepted and change nothing.
- `fieldsChanged` holds only what the user edited and what an onchange
  answered, never readonly fields: a record just loaded has nothing to save.
- Ported from PySide2 to **PySide6**; requires **Python 3.12+**.
- The RPC connection is reused instead of reopened on every call.
- README rewritten with working examples.

### Fixed
- Database list on the login dialog.
- `evaluateBoolean` returns a boolean instead of `None`.
- The context of a view node is evaluated over the record's values, and never
  written into the session context: a res.partner form of Odoo 19 no longer
  fails with "cannot marshal".
- `invisible` on `div`, `group` and `page` is honoured and follows the record;
  pages with a condition were never built.
- onchange uses the signature of Odoo 17 and later (unchanged up to 16).
- Float and integer fields no longer clip values to 99.99 / 99.
- List views: `column_invisible` and `optional="hide"` hide columns,
  `invisible` hides a single cell (Odoo 17 and later).
- `utils.py` defined the whole module twice.

### Removed
- Python 2 / PySide2 support and Odoo versions older than 19 are no longer
  officially supported.
- Obsolete `start.py` demo and the old `Test/` scripts, which used an API that
  no longer exists.
- `OmniaQt` and `OdooQtUiWeb` are no longer shipped in the PyPI package.

## [0.0.5] and earlier

PySide2 releases, see the git history.
