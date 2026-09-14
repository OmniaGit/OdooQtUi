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

### Changed
- **License changed to Apache 2.0** (previously LGPL v3, with some sources
  carrying GPL / AGPL headers). The code can be reused freely, provided the
  attribution in the `NOTICE` file is kept. Every source file now carries an
  SPDX header.
- Ported from PySide2 to **PySide6**; requires **Python 3.12+**.
- The RPC connection is reused instead of reopened on every call.
- README rewritten with working examples.

### Fixed
- Database list on the login dialog.
- `evaluateBoolean` returns a boolean instead of `None`.

### Removed
- Python 2 / PySide2 support and Odoo versions older than 19 are no longer
  officially supported.
- Obsolete `start.py` demo and the old `Test/` scripts, which used an API that
  no longer exists.
- `OmniaQt` and `OdooQtUiWeb` are no longer shipped in the PyPI package.

## [0.0.5] and earlier

PySide2 releases, see the git history.
