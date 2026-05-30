[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Task,
    [ValidateSet("initialized", "in_progress", "blocked", "ready_for_review", "done")]
    [string]$Status = "in_progress",
    [string]$Notes = "",
    [string]$NextStep = ""
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$MemoryRoot = Join-Path $ProjectRoot ".codex-memory"
$SessionPath = Join-Path $MemoryRoot "SESSION-STATE.md"

if (-not (Test-Path -LiteralPath $MemoryRoot)) {
    throw "Missing .codex-memory. Run scripts\Initialize-CodexMemory.ps1 first."
}

$now = Get-Date -Format "yyyy-MM-ddTHH:mm:ssK"

$content = @"
# Session State

updated_at: $now
status: $Status
task: $Task

## Notes

$Notes

## Next Step

$NextStep
"@

Set-Content -LiteralPath $SessionPath -Value $content -Encoding UTF8
Write-Output "Updated $SessionPath"
