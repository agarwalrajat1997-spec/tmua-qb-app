[CmdletBinding()]
param(
    [string]$InputDirectory = (Join-Path $env:USERPROFILE "Downloads"),
    [string]$ProjectRef = "pnkzxzigpkvhlmhsmzdd",
    [string]$R2Prefix = "sat/question-bank/v2/original-hard-100",
    [string]$R2PublicBaseUrl = "https://media.thrivingscholars.com"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Step([string]$Text) {
    Write-Host ""
    Write-Host ("=" * 72) -ForegroundColor DarkGray
    Write-Host $Text -ForegroundColor Cyan
    Write-Host ("=" * 72) -ForegroundColor DarkGray
}

function ConvertFrom-SecureValue([Security.SecureString]$SecureValue) {
    $Pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecureValue)
    try {
        return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($Pointer)
    }
    finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($Pointer)
    }
}

function Ensure-TextEnvironmentVariable([string]$Name, [string]$Prompt) {
    $Existing = [Environment]::GetEnvironmentVariable($Name, "Process")
    if (-not [string]::IsNullOrWhiteSpace($Existing)) {
        return $false
    }

    $Value = Read-Host $Prompt
    if ([string]::IsNullOrWhiteSpace($Value)) {
        throw "$Name is required."
    }
    [Environment]::SetEnvironmentVariable($Name, $Value.Trim(), "Process")
    return $true
}

function Ensure-SecretEnvironmentVariable([string]$Name, [string]$Prompt) {
    $Existing = [Environment]::GetEnvironmentVariable($Name, "Process")
    if (-not [string]::IsNullOrWhiteSpace($Existing)) {
        return $false
    }

    $Secure = Read-Host $Prompt -AsSecureString
    $Value = ConvertFrom-SecureValue $Secure
    if ([string]::IsNullOrWhiteSpace($Value)) {
        throw "$Name is required."
    }
    [Environment]::SetEnvironmentVariable($Name, $Value, "Process")
    return $true
}

function Invoke-Checked([string]$FilePath, [string[]]$Arguments) {
    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw ("Command failed with exit code {0}: {1}" -f $LASTEXITCODE, $FilePath)
    }
}

Write-Step "SAT Question Bank 595-question release preflight"

$RequiredFiles = @(
    "sat-hard-original-100-verified.json",
    "sat-qb-manual-batch-01-of-06-reviewed.json",
    "sat-qb-manual-batch-02-of-06-reviewed.json",
    "sat-qb-manual-batch-03-of-06-reviewed.json",
    "sat-qb-manual-batch-04-of-06-reviewed.json",
    "sat-qb-manual-batch-05-of-06-reviewed.json",
    "sat-qb-manual-batch-06-of-06-reviewed.json"
)

foreach ($Name in $RequiredFiles) {
    $Path = Join-Path $InputDirectory $Name
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "Required input file is missing: $Path"
    }
}

$PythonCommand = Get-Command "py" -ErrorAction SilentlyContinue
$PythonArguments = @("-3")
if (-not $PythonCommand) {
    $PythonCommand = Get-Command "python" -ErrorAction SilentlyContinue
    $PythonArguments = @()
}
if (-not $PythonCommand) {
    throw "Python 3 is required. Install it from python.org and rerun this script."
}

$RuntimeRoot = Join-Path $env:LOCALAPPDATA "ThrivingScholars\SAT-QB-Release"
$Venv = Join-Path $RuntimeRoot "venv"
$VenvPython = Join-Path $Venv "Scripts\python.exe"
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonScript = Join-Path $ScriptRoot "publish_sat_qb_release.py"
$Requirements = Join-Path $ScriptRoot "requirements.txt"

New-Item -ItemType Directory -Path $RuntimeRoot -Force | Out-Null
if (-not (Test-Path -LiteralPath $VenvPython -PathType Leaf)) {
    Write-Host "Creating the isolated SAT release environment..."
    Invoke-Checked $PythonCommand.Source ($PythonArguments + @("-m", "venv", $Venv))
}

Write-Host "Installing/verifying the pinned release dependency..."
Invoke-Checked $VenvPython @("-m", "pip", "install", "--disable-pip-version-check", "-r", $Requirements)
Invoke-Checked $VenvPython @("-m", "pip", "check")

$SecretsSetHere = [Collections.Generic.List[string]]::new()
try {
    if (Ensure-SecretEnvironmentVariable "SUPABASE_SERVICE_ROLE_KEY" "Supabase service-role key (input is hidden)") {
        $SecretsSetHere.Add("SUPABASE_SERVICE_ROLE_KEY")
    }
    if (Ensure-TextEnvironmentVariable "R2_ACCOUNT_ID" "Cloudflare R2 account ID") {
        $SecretsSetHere.Add("R2_ACCOUNT_ID")
    }
    if (Ensure-TextEnvironmentVariable "R2_ACCESS_KEY_ID" "Cloudflare R2 access key ID") {
        $SecretsSetHere.Add("R2_ACCESS_KEY_ID")
    }
    if (Ensure-SecretEnvironmentVariable "R2_SECRET_ACCESS_KEY" "Cloudflare R2 secret access key (input is hidden)") {
        $SecretsSetHere.Add("R2_SECRET_ACCESS_KEY")
    }
    if (Ensure-TextEnvironmentVariable "R2_BUCKET" "Cloudflare R2 bucket name") {
        $SecretsSetHere.Add("R2_BUCKET")
    }

    Write-Step "Controlled production publication gate"
    Write-Host "This will preserve 230 auto-passes, override 265 corrected qids,"
    Write-Host "append 100 new questions, upload 24 images, and publish exactly 595."
    $Confirmation = Read-Host "Type PUBLISH-595-SAT-QUESTIONS to continue"
    if ($Confirmation -cne "PUBLISH-595-SAT-QUESTIONS") {
        throw "Publication cancelled: confirmation phrase did not match."
    }

    [Environment]::SetEnvironmentVariable(
        "SAT_QB_PUBLISH_CONFIRM",
        "PUBLISH-595-SAT-QUESTIONS",
        "Process"
    )
    $SecretsSetHere.Add("SAT_QB_PUBLISH_CONFIRM")

    $Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $Receipt = Join-Path $InputDirectory "SAT-QB-595-Release-Receipt-$Timestamp.json"
    $Backup = Join-Path $InputDirectory "SAT-QB-Prepublish-Backup-$Timestamp.json"

    Write-Step "Run the verified, resumable release"
    Invoke-Checked $VenvPython @(
        $PythonScript,
        "--input-dir", $InputDirectory,
        "--project-ref", $ProjectRef,
        "--r2-prefix", $R2Prefix,
        "--r2-public-base-url", $R2PublicBaseUrl,
        "--receipt", $Receipt,
        "--backup", $Backup
    )

    Write-Step "SAT Question Bank release completed"
    Write-Host "Receipt: $Receipt" -ForegroundColor Green
    Write-Host "Pre-publish backup: $Backup" -ForegroundColor Green
    Write-Host "Upload the receipt output to ChatGPT for the final live-site check."
}
finally {
    foreach ($Name in $SecretsSetHere) {
        [Environment]::SetEnvironmentVariable($Name, $null, "Process")
    }
}
