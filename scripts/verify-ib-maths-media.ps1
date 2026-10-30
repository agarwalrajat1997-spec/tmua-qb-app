param([Parameter(Mandatory=$true)][string]$Url, [Parameter(Mandatory=$true)][string]$OutputPath)
$ErrorActionPreference = 'Stop'
if ($Url -notmatch '^https://media\.thrivingscholars\.com/ib/maths/2026-10-30/[a-f0-9]{64}\.svg$') { throw 'Unexpected Maths media address' }
$mathsMediaResponse = Invoke-WebRequest -Uri ($Url+'?verification='+[guid]::NewGuid().ToString('N')) -UseBasicParsing -TimeoutSec 20 -OutFile $OutputPath -PassThru
if ($mathsMediaResponse.StatusCode -ne 200 -or $mathsMediaResponse.Headers['Content-Type'] -notmatch 'image/svg\+xml') { throw 'Unexpected Maths media response' }
