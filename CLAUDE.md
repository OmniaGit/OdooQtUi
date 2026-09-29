# CLAUDE.md

Guidance for Claude Code (claude.ai/code) in the OdooQtUi repository.

## OmniaSolutions: branches, versions and builds

This section is the same in every OmniaSolutions repository (OmniaConfigurator3,
client_utils, MultiCad, MultiDbClient, OdooQtUi, OdooPlmClientExtention,
CoreBom, PyComBridge, PLM_BOX): change it in all of them together.

### Branches

The development rule of every OmniaSolutions application that is not an Odoo
module:

- **`<year>` is the build branch** (`2026`). Every package, executable and
  installer is built from it, test builds included, and every definitive change
  for that year's version ends up in it.
- **`<developer>_dev_<year>` is where a developer works and tests**
  (`matteo_dev_2026`). A change is tested there and merged into `<year>` once
  it works; nothing is developed on `<year>` directly.
- A merge conflict is shown to Matteo and decided by him, never resolved by
  guess.
- Odoo modules follow the same rule with the Odoo version in place of the year:
  `<odoo_version>` (`18.0`) and `<developer>_dev_<odoo_version>`
  (`matteo_dev_18.0`).

### Versions

Every Omnia library is a versioned Python package:

- `__version__ = "YEAR.MINOR.PATCH"` in the package's `__init__.py` is the only
  place the version is written; `pyproject.toml` reads it
  (`dynamic = ["version"]`).
- The distribution is named `omnia-<name>`; the import name does not change.
- A release tags its commit `<name>-v<version>` and raises the version.
- A product pins the exact version of every package it ships, and its installer
  carries a `versions.txt` listing them.

| Repository | Import | Distribution |
|---|---|---|
| MultiCad | `multyCad`, `multyCadApplication`, `multiCadCom` | `omnia-multicad` |
| client_utils | `OmniaSolutions` | `omnia-utils` |
| MultiDbClient | `DbWrapper` | `omnia-dbwrapper` |
| OdooPlmClientExtention | `OdooPLMClientCadExt`, `cad_extensions` | `omnia-odooplm-cce` |
| OdooQtUi | `OdooQtUi` | `OdooQtUi`, published under its own name |
| PyComBridge | the installer `PyComBridge-<version>-x64.exe` | - |

### Builds

- Every package, executable and installer is built on the VirtualBox VM
  **`OdooPLM 2.12 Compile`**, and on no other machine (Python 3.12.10 per user,
  MSVC 2022, Inno Setup).
- A build starts from git, never from a working tree: the `<year>` branch
  (`2026`) is exported with `git archive` to the share and built from there, so
  every build names the commit it came from.
- The host drives the VM with `VBoxManage guestcontrol`: it writes a `.bat` to
  the share (`~/workspace_virtual_machine/share`, `\\VBoxSvr\share` in the
  guest), starts it in the background, and reads its log and status file from
  the share. A long build is never run in the foreground over guestcontrol: the
  pipe fills and Nuitka blocks.
- Code that runs inside a CAD (the PyComBridge products) is compiled with Nuitka
  `--module`, one module per package, for Python 3.12: the ABI of PyComBridge's
  interpreter.
