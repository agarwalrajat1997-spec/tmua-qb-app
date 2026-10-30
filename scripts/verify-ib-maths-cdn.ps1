param([Parameter(Mandatory=$true)][string]$ArtifactDir)
$ErrorActionPreference='Stop'
$mathsDir=(Resolve-Path -LiteralPath $ArtifactDir).Path
$mathsManifest=Get-Content -Raw content/ib/maths-diagram-manifest.json | ConvertFrom-Json -AsHashtable
if($mathsManifest.origin -ne 'https://media.thrivingscholars.com'){throw 'Unexpected media origin'}
$mathsOutput=Join-Path $mathsDir 'canonical-verification'
New-Item -ItemType Directory -Force -Path $mathsOutput | Out-Null
$mathsChecks=@();$mathsFailures=@()
foreach($mathsHash in $mathsManifest.assets.Keys){
 $mathsEntry=$mathsManifest.assets[$mathsHash]
 if($mathsHash -notmatch '^[a-f0-9]{64}$' -or $mathsEntry.key -ne ('ib/maths/2026-10-30/'+$mathsHash+'.svg')){throw 'Unexpected media key'}
 $mathsPassed=$false
 for($mathsAttempt=1;$mathsAttempt -le 3;$mathsAttempt++){
  try{
   $mathsPath=Join-Path $mathsOutput ($mathsHash+'.svg')
   $mathsResponse=Invoke-WebRequest -Uri ($mathsManifest.origin+'/'+$mathsEntry.key) -UseBasicParsing -TimeoutSec 20 -OutFile $mathsPath -PassThru
   if($mathsResponse.StatusCode -ne 200 -or $mathsResponse.Headers['Content-Type'] -notmatch 'image/svg\+xml'){throw 'Unexpected image response'}
   if((Get-FileHash -LiteralPath $mathsPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $mathsHash -or (Get-Item -LiteralPath $mathsPath).Length -ne $mathsEntry.bytes){throw 'Public image differs from the authored image'}
   $mathsChecks+=@{sha256=$mathsHash;bytes=$mathsEntry.bytes;status='passed'};$mathsPassed=$true;break
  }catch{if($mathsAttempt -lt 3){Start-Sleep -Seconds 2}}
 }
 if(-not $mathsPassed){$mathsFailures+=$mathsHash}
 if(($mathsChecks.Count+$mathsFailures.Count)%50 -eq 0){Write-Output (@{checked=$mathsChecks.Count;failures=$mathsFailures.Count;total=$mathsManifest.assets.Count}|ConvertTo-Json -Compress)}
}
$mathsReport=@{status=if($mathsFailures.Count){'failed'}else{'passed'};origin=$mathsManifest.origin;verified=$mathsChecks.Count;failures=$mathsFailures;checks=$mathsChecks}
[IO.File]::WriteAllText((Join-Path $mathsDir 'canonical-cdn-verification.json'),($mathsReport|ConvertTo-Json -Depth 20)+"`n",[Text.UTF8Encoding]::new($false))
if($mathsFailures.Count){throw "$($mathsFailures.Count) canonical image URLs did not pass verification"}
Write-Output (@{status='passed';verified=$mathsChecks.Count}|ConvertTo-Json -Compress)
