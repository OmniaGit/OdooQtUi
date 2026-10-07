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
  installer that reaches a customer is built from it, and every definitive
  change for that year's version ends up in it. Test builds are the exception:
  see Builds.
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
- **There are two kinds of build** (decided 2026-10-06):
  - **Test build:** every repository is built from the branch that holds its
    latest commits, `<developer>_dev_<year>` or `<year>` alike, so the newest
    work of everybody is in it. Nothing is merged and nothing is pushed; a test
    build never reaches a customer.
  - **Production build:** the dev branches are merged into `<year>` first,
    `<year>` is pushed, and the build starts from it. Other people use the same
    tools, so which dev branches go in is not known in advance: the operator
    chooses them, repository by repository.
- A build starts from git, never from a working tree: the chosen commits are
  exported with `git archive` to the share and built from there, so every
  build names the commits it came from (`versions.txt`).
- CoreBom and OdooPLM do both with `CoreBom/Setup/build.sh test|prod`; its use
  is in `CoreBom/Setup/README.md`.
- The host drives the VM with `VBoxManage guestcontrol`: it writes a `.bat` to
  the share (`~/workspace_virtual_machine/share`, `\\VBoxSvr\share` in the
  guest), starts it in the background, and reads its log and status file from
  the share. A long build is never run in the foreground over guestcontrol: the
  pipe fills and Nuitka blocks.
- Code that runs inside a CAD (the PyComBridge products) is compiled with Nuitka
  `--module`, one module per package, for Python 3.12: the ABI of PyComBridge's
  interpreter.
