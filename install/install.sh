#!/usr/bin/env sh
# agent-lessons installer -- POSIX sh / bash / zsh / Git Bash
#
# Why this file exists: the real logic lives in core.py (single source).
# This wrapper only (a) finds a usable Python, (b) forwards arguments.
# It must NOT re-implement any logic -- duplicated logic drifts silently.
#
# Usage:
#   sh install/install.sh status
#   sh install/install.sh install --agent claude            # dry-run
#   sh install/install.sh install --agent claude --apply
#   sh install/install.sh uninstall --agent claude --apply
set -eu

HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

# --- pick a Python -----------------------------------------------------------
# NOTE: on Windows/Git-Bash, a bare `python` may resolve to the Microsoft Store
# stub, which opens the Store instead of running. Prefer python3, then py.
PY=""
for c in python3 python py; do
  if command -v "$c" >/dev/null 2>&1; then
    if "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' >/dev/null 2>&1; then
      PY="$c"; break
    fi
  fi
done

if [ -z "$PY" ]; then
  cat >&2 <<'EOF'
[agent-lessons] No usable Python 3.8+ found.

This installer needs Python only to edit your agent config safely
(idempotent, marked block, exact uninstall). It never needs network access.

  Windows   : install from https://www.python.org/downloads/  (tick "Add to PATH")
              or run:  winget install Python.Python.3.12
  macOS     : brew install python3
  Debian    : sudo apt install python3

Then re-run this script.
EOF
  exit 127
fi

exec "$PY" "$HERE/core.py" "$@"
