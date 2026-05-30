[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Title,
    [Parameter(Mandatory = $true)][string]$Body,
    [string]$Scope = "expedition-hq",
    [string]$Source = "manual",
    [string]$Impact = "",
    [string]$NextStep = ""
)

& (Join-Path $PSScriptRoot "Add-CodexMemoryEntry.ps1") -Type learning @PSBoundParameters

