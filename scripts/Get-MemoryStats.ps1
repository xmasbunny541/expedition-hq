[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$MemoryRoot = Join-Path $ProjectRoot ".codex-memory"

if (-not (Test-Path -LiteralPath $MemoryRoot)) {
    throw "Missing .codex-memory. Run scripts\Initialize-CodexMemory.ps1 first."
}

$folders = @("learnings", "decisions", "errors", "corrections", "proactive", "handoffs")

$allFiles = @(Get-ChildItem -LiteralPath $MemoryRoot -Recurse -File)
$latestWrite = ($allFiles | Sort-Object LastWriteTime -Descending | Select-Object -First 1).LastWriteTime

Write-Output "Memory root: $MemoryRoot"
Write-Output "Total files: $($allFiles.Count)"
Write-Output "Latest write: $latestWrite"
Write-Output ""

$rows = foreach ($folder in $folders) {
    $path = Join-Path $MemoryRoot $folder
    $files = @(Get-ChildItem -LiteralPath $path -File -Filter "*.md" -ErrorAction SilentlyContinue | Where-Object { $_.Name -ne "README.md" })
    [pscustomobject]@{
        folder = $folder
        entries = $files.Count
        latest = ($files | Sort-Object LastWriteTime -Descending | Select-Object -First 1).Name
    }
}

$rows | Format-Table -AutoSize
