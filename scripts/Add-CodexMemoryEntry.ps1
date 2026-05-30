[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("learning", "decision", "error", "correction", "proactive", "handoff")]
    [string]$Type,

    [Parameter(Mandatory = $true)]
    [string]$Title,

    [Parameter(Mandatory = $true)]
    [string]$Body,

    [string]$Scope = "expedition-hq",
    [string]$Source = "manual",
    [string]$Impact = "",
    [string]$NextStep = ""
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$MemoryRoot = Join-Path $ProjectRoot ".codex-memory"

if (-not (Test-Path -LiteralPath $MemoryRoot)) {
    throw "Missing .codex-memory. Run scripts\Initialize-CodexMemory.ps1 first."
}

$folderByType = @{
    learning   = "learnings"
    decision   = "decisions"
    error      = "errors"
    correction = "corrections"
    proactive  = "proactive"
    handoff    = "handoffs"
}

function Test-UnsafeMemoryText {
    param([string]$Text)

    $patterns = @(
        "sk-[A-Za-z0-9_-]{20,}",
        "ghp_[A-Za-z0-9_]{20,}",
        "github_pat_[A-Za-z0-9_]{20,}",
        "xox[baprs]-[A-Za-z0-9-]{20,}",
        "-----BEGIN [A-Z ]*PRIVATE KEY-----",
        "(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{12,}",
        "(?i)\b(api[_-]?key|password|secret|token)\s*[:=]\s*\S+"
    )

    foreach ($pattern in $patterns) {
        if ($Text -match $pattern) {
            return $true
        }
    }

    return $false
}

$combined = @($Title, $Body, $Scope, $Source, $Impact, $NextStep) -join "`n"
if (Test-UnsafeMemoryText -Text $combined) {
    throw "Refusing to write memory entry because the text matches a common secret pattern."
}

$folder = Join-Path $MemoryRoot $folderByType[$Type]
if (-not (Test-Path -LiteralPath $folder)) {
    New-Item -ItemType Directory -Path $folder | Out-Null
}

$slug = ($Title.ToLowerInvariant() -replace "[^a-z0-9]+", "-").Trim("-")
if ([string]::IsNullOrWhiteSpace($slug)) {
    $slug = $Type
}

if ($slug.Length -gt 60) {
    $slug = $slug.Substring(0, 60).Trim("-")
}

$stamp = Get-Date -Format "yyyy-MM-ddTHH-mm-ss"
$path = Join-Path $folder "$stamp-$slug.md"
$observedAt = Get-Date -Format "yyyy-MM-ddTHH:mm:ssK"

$content = @"
# $Title

type: $Type
observed_at: $observedAt
scope: $Scope
source: $Source

## Body

$Body

## Impact

$Impact

## Next Step

$NextStep
"@

Set-Content -LiteralPath $path -Value $content -Encoding UTF8
Write-Output $path
