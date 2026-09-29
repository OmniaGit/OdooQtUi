# CLAUDE.md

Guidance for Claude Code (claude.ai/code) in the OdooQtUi repository.

## OmniaSolutions: branches, versions and builds

This section is the same in every OmniaSolutions repository (OmniaConfigurator3,
client_utils, MultiCad, MultiDbClient, OdooQtUi, OdooPlmClientExtention,
CoreBom, PyComBridge, PLM_BOX): change it in all of them together.

### Branches

- **`matteo_dev_2026` is development** (in OmniaConfigurator3: `python3`). Work,
  commits and **test builds** happen here.
- **`2026` is production.** Releases are built only from `2026`, after the dev
  branch is merged into it. Nothing is committed on `2026` directly.
- The other dev branches (`dev_jayraj_2026`, `2026_dev_multierp`, ...) are
  merged into `2026` at release time. A conflict is shown to Matteo and decided
  by him, never resolved by guess.

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
- A build starts from git, never from a working tree: the chosen branch
  (`matteo_dev_2026` for a test, `2026` for a release) is exported with
  `git archive` to the share and built from there, so every build names the
  commit it came from.
- The host drives the VM with `VBoxManage guestcontrol`: it writes a `.bat` to
  the share (`~/workspace_virtual_machine/share`, `\\VBoxSvr\share` in the
  guest), starts it in the background, and reads its log and status file from
  the share. A long build is never run in the foreground over guestcontrol: the
  pipe fills and Nuitka blocks.
- Code that runs inside a CAD (the PyComBridge products) is compiled with Nuitka
  `--module`, one module per package, for Python 3.12: the ABI of PyComBridge's
  interpreter.
