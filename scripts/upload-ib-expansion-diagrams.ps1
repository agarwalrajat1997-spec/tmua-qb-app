param([Parameter(Mandatory=$true)][string]$ArtifactDir, [Parameter(Mandatory=$true)][string]$WranglerEntry)
$ErrorActionPreference = 'Stop'
$mathsDir = (Resolve-Path -LiteralPath $ArtifactDir).Path
$mathsStage = Get-Content -Raw -LiteralPath (Join-Path $mathsDir 'staged-manifest.json') | ConvertFrom-Json -AsHashtable
if ($mathsStage.bucket -ne 'thriving-scholars-media' -or $mathsStage.origin -ne 'https://media.thrivingscholars.com') { throw 'Unexpected Cloudflare destination' }
$mathsResultPath = Join-Path $mathsDir 'uploaded-results.json'
$mathsDone = if (Test-Path -LiteralPath $mathsResultPath) { Get-Content -Raw -LiteralPath $mathsResultPath | ConvertFrom-Json -AsHashtable } else { @{schemaVersion=1;verified=@{}} }
$mathsVerifyDir = Join-Path $mathsDir 'public-verification'
New-Item -ItemType Directory -Force -Path $mathsVerifyDir | Out-Null
$mathsNode = (Get-Command node.exe).Source
$mathsUploaded = 0; $mathsSkipped = 0; $mathsFailed = @()
function Save-MathsProgress {
 [IO.File]::WriteAllText($mathsResultPath,($mathsDone | ConvertTo-Json -Depth 30)+"`n",[Text.UTF8Encoding]::new($false))
}
function Read-MathsPublicImage($Item) {
 $mathsPublicFile = Join-Path $mathsVerifyDir ($Item.sha256+'.svg')
 $mathsResponse = Invoke-WebRequest -Uri ($mathsStage.origin+'/'+$Item.key+'?verification='+[guid]::NewGuid().ToString('N')) -UseBasicParsing -TimeoutSec 20 -OutFile $mathsPublicFile -PassThru
 if ($mathsResponse.StatusCode -ne 200 -or $mathsResponse.Headers['Content-Type'] -notmatch 'image/svg\+xml') { throw 'Unexpected public image response' }
 if ((Get-FileHash -LiteralPath $mathsPublicFile -Algorithm SHA256).Hash.ToLowerInvariant() -ne $Item.sha256) { throw 'Public image hash mismatch' }
 return @{key=$Item.key;bytes=(Get-Item -LiteralPath $mathsPublicFile).Length}
}
foreach ($mathsItem in $mathsStage.objects) {
 if ($mathsItem.sha256 -notmatch '^[a-f0-9]{64}$' -or $mathsItem.key -ne ('ib/expansion/2026-10-31/'+$mathsItem.sha256+'.svg')) { throw 'Invalid image key' }
 $mathsLocal = Join-Path $mathsDir ('assets/'+$mathsItem.sha256+'.svg')
 if ((Get-FileHash -LiteralPath $mathsLocal -Algorithm SHA256).Hash.ToLowerInvariant() -ne $mathsItem.sha256) { throw 'Local image hash mismatch' }
 if ($mathsDone.verified.Contains($mathsItem.sha256)) { $mathsSkipped++; continue }
 try { $mathsDone.verified[$mathsItem.sha256] = Read-MathsPublicImage $mathsItem; Save-MathsProgress; $mathsSkipped++; continue } catch { }
 $mathsSuccess = $false
 for ($mathsAttempt=1; $mathsAttempt -le 3; $mathsAttempt++) {
  try {
   $mathsUploadLog = & $mathsNode --dns-result-order=ipv4first $WranglerEntry r2 object put ($mathsStage.bucket+'/'+$mathsItem.key) --file $mathsLocal --remote --content-type image/svg+xml --cache-control 'public,max-age=31536000,immutable' 2>&1
   if ($LASTEXITCODE -ne 0) { throw 'Cloudflare transfer did not finish' }
   $mathsDone.verified[$mathsItem.sha256] = Read-MathsPublicImage $mathsItem
   Save-MathsProgress; $mathsUploaded++; $mathsSuccess=$true; break
  } catch { Write-Output (@{retry=$mathsAttempt;image=$mathsItem.sha256.Substring(0,16);reason=$_.Exception.Message} | ConvertTo-Json -Compress); if ($mathsAttempt -lt 3) { Start-Sleep -Seconds 2 } }
 }
 if (-not $mathsSuccess) { $mathsFailed += $mathsItem.sha256 }
 if ($mathsUploaded -gt 0 -and $mathsUploaded % 20 -eq 0) { Write-Output (@{uploaded=$mathsUploaded;skipped=$mathsSkipped;total=$mathsStage.objects.Count} | ConvertTo-Json -Compress) }
}
if ($mathsFailed.Count) { throw "$($mathsFailed.Count) images need another transfer; verified copies are retained." }
$mathsAssets = [ordered]@{}
foreach ($mathsItem in $mathsStage.objects) { $mathsAssets[$mathsItem.sha256] = $mathsDone.verified[$mathsItem.sha256] }
$mathsManifest = @{schemaVersion=1;origin=$mathsStage.origin;assets=$mathsAssets}
[IO.File]::WriteAllText((Join-Path (Get-Location) 'content/ib/expansion-diagram-manifest.json'),($mathsManifest | ConvertTo-Json -Depth 30)+"`n",[Text.UTF8Encoding]::new($false))
Write-Output (@{status='verified';uploaded=$mathsUploaded;skipped=$mathsSkipped;total=$mathsStage.objects.Count} | ConvertTo-Json -Compress)
