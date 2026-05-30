[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$MemoryRoot = Join-Path $ProjectRoot ".codex-memory"

if (-not (Test-Path -LiteralPath $MemoryRoot)) {
    throw "Missing .codex-memory. Run scripts\Initialize-CodexMemory.ps1 first."
}

$patterns = @(
    "sk-[A-Za-z0-9_-]{20,}",
    "ghp_[A-Za-z0-9_]{20,}",
    "github_pat_[A-Za-z0-9_]{20,}",
    "xox[baprs]-[A-Za-z0-9-]{20,}",
    "-----BEGIN [A-Z ]*PRIVATE KEY-----",
    "(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{12,}",
    "(?i)\b(api[_-]?key|password|secret|token)\s*[:=]\s*\S+"
)

$findings = @()
foreach ($file in Get-ChildItem -LiteralPath $MemoryRoot -Recurse -File) {
    $lineNumber = 0
    foreach ($line in Get-Content -LiteralPath $file.FullName) {
        $lineNumber++
        foreach ($pattern in $patterns) {
            if ($line -match $pattern) {
                $findings += [pscustomobject]@{
                    file = $file.FullName
                    line = $lineNumber
                    pattern = $pattern
                }
            }
        }
    }
}

if ($findings.Count -gt 0) {
    $findings | Format-Table -AutoSize
    throw "Potential secret-bearing content found in .codex-memory."
}

Write-Output "Memory redaction check passed."

