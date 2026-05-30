[CmdletBinding()]
param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$MemoryRoot = Join-Path $ProjectRoot ".codex-memory"

$directories = @(
    $MemoryRoot,
    (Join-Path $MemoryRoot "learnings"),
    (Join-Path $MemoryRoot "decisions"),
    (Join-Path $MemoryRoot "errors"),
    (Join-Path $MemoryRoot "corrections"),
    (Join-Path $MemoryRoot "proactive"),
    (Join-Path $MemoryRoot "handoffs")
)

foreach ($directory in $directories) {
    if (-not (Test-Path -LiteralPath $directory)) {
        New-Item -ItemType Directory -Path $directory | Out-Null
    }
}

function Ensure-TextFile {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Content
    )

    if ($Force -or -not (Test-Path -LiteralPath $Path)) {
        Set-Content -LiteralPath $Path -Value $Content -Encoding UTF8
    }
}

$now = Get-Date -Format "yyyy-MM-ddTHH:mm:ssK"

Ensure-TextFile -Path (Join-Path $MemoryRoot "MEMORY.md") -Content @"
# Expedition HQ Project Memory

## Status

- Project-local Codex memory initialized at $now.

## Memory Hygiene

- Record only reusable lessons, meaningful decisions, real failure patterns, open questions, or handoff state.
- Do not store secrets, credentials, raw private transcripts, `.env` contents, private keys, tunnel URLs, auth tokens, or secret-bearing config.
"@

Ensure-TextFile -Path (Join-Path $MemoryRoot "SESSION-STATE.md") -Content @"
# Session State

updated_at: $now
status: initialized
task: Project-local Codex memory scaffold

## Current State

- `.codex-memory/` exists.
- Run `.\scripts\Get-MemoryStats.ps1` before relying on project memory.
"@

Ensure-TextFile -Path (Join-Path $MemoryRoot "README.md") -Content @"
# Expedition HQ Codex Memory

Project-local working memory for Codex collaboration on Expedition HQ.

Do not store secrets, credentials, raw private transcripts, `.env` contents, private keys, tunnel URLs, auth tokens, or secret-bearing config.
"@

Write-Output "Codex memory scaffold ready: $MemoryRoot"
