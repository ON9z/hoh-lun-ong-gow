@echo off
REM agent-lessons installer -- Windows cmd.exe
REM
REM This file is ASCII-only ON PURPOSE. cmd.exe re-reads a .bat by byte offset
REM while it runs; a non-ASCII byte can desynchronise the parser and make it
REM jump into garbage. Same reason there are no fancy characters below.
REM
REM Usage (from the repo root):
REM   install\install.cmd status
REM   install\install.cmd install --agent claude
REM   install\install.cmd install --agent claude --apply
REM   install\install.cmd uninstall --agent claude --apply
setlocal
REM Switch the console to UTF-8 so non-ASCII output renders (and does not crash).
chcp 65001 >nul 2>nul
set "HERE=%~dp0"

set "PY="

REM `py` (the official Windows launcher) is the most reliable.
where py >nul 2>nul && (
  py -3 -c "import sys; sys.exit(0 if sys.version_info>=(3,8) else 1)" >nul 2>nul && set "PY=py -3"
)

REM Fall back to python3 / python, but SKIP the Microsoft Store stub
REM (it exists on PATH yet only opens the Store when run).
if not defined PY (
  where python3 >nul 2>nul && (
    python3 -c "import sys" >nul 2>nul && set "PY=python3"
  )
)
if not defined PY (
  where python >nul 2>nul && (
    python -c "import sys" >nul 2>nul && set "PY=python"
  )
)

if not defined PY (
  echo [agent-lessons] No usable Python 3.8+ found.
  echo.
  echo This installer needs Python only to edit your agent config safely
  echo ^(idempotent, marked block, exact uninstall^). No network access needed.
  echo.
  echo   Install Python:  winget install Python.Python.3.12
  echo   Or:              https://www.python.org/downloads/  ^(tick "Add to PATH"^)
  exit /b 127
)

%PY% "%HERE%core.py" %*
exit /b %ERRORLEVEL%
