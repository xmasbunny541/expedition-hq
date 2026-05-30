[CmdletBinding()]
param(
    [int]$Recent = 5
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$MemoryRoot = Join-Path $ProjectRoot ".codex-memory"

if (-not (Test-Path -LiteralPath $MemoryRoot)) {
    throw "Missing .codex-memory. Run scripts\Initialize-CodexMemory.ps1 first."
}

Write-Output "# MEMORY.md"
Get-Content -LiteralPath (Join-Path $MemoryRoot "MEMORY.md")

Write-Output ""
Write-Output "# SESSION-STATE.md"
Get-Content -LiteralPath (Join-Path $MemoryRoot "SESSION-STATE.md")

Write-Output ""
Write-Output "# Recent Entries"
Get-ChildItem -LiteralPath $MemoryRoot -Recurse -File -Filter "*.md" |
    Where-Object { $_.Name -notin @("README.md", "MEMORY.md", "SESSION-STATE.md") } |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First $Recent FullName, LastWriteTime

