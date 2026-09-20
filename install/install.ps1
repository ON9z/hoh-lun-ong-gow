# agent-lessons installer -- PowerShell 5.1+ / PowerShell 7+
#
# ASCII-only on purpose: a PowerShell/cmd file with non-ASCII text can be read
# in the wrong codepage and corrupt itself. Keep this file ASCII.
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File install\install.ps1 status
#   powershell -ExecutionPolicy Bypass -File install\install.ps1 install --agent claude
#   powershell -ExecutionPolicy Bypass -File install\install.ps1 install --agent claude --apply
#
# One-liner from a fresh clone (dry-run first, always):
#   powershell -ExecutionPolicy Bypass -File .\install\install.ps1 install --agent claude

$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path

$candidates = @('python3', 'python', 'py')
$py = $null
foreach ($c in $candidates) {
    $cmd = Get-Command $c -ErrorAction SilentlyContinue
    if (-not $cmd) { continue }
    # Reject the Microsoft Store stub: it "exists" but only opens the Store.
    $out = & $c -c "import sys; print(sys.version_info[0], sys.version_info[1])" 2>$null
    if ($LASTEXITCODE -eq 0 -and $out -match '^(\d+) (\d+)') {
        $maj = [int]$Matches[1]; $min = [int]$Matches[2]
        if ($maj -ge 3 -and $min -ge 8) { $py = $c; break }
    }
}

if (-not $py) {
    Write-Host "[agent-lessons] No usable Python 3.8+ found." -ForegroundColor Red
    Write-Host ""
    Write-Host "This installer needs Python only to edit your agent config safely"
    Write-Host "(idempotent, marked block, exact uninstall). No network access needed."
    Write-Host ""
    Write-Host "  Install Python:  winget install Python.Python.3.12"
    Write-Host "  Or:              https://www.python.org/downloads/  (tick 'Add to PATH')"
    exit 127
}

& $py (Join-Path $here 'core.py') @args
exit $LASTEXITCODE
