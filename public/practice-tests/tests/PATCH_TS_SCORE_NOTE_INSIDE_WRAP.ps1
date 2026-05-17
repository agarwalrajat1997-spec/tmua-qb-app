# PATCH_TS_SCORE_NOTE_INSIDE_WRAP.ps1

$ErrorActionPreference = "Stop"

$targetDir = "C:\Users\agarw\tmua-qb-app\public\practice-tests\tests"

if (!(Test-Path $targetDir)) {
  throw "Target folder not found: $targetDir"
}

Set-Location $targetDir

# only patch the actual test html files
$files = Get-ChildItem -Path $targetDir -File -Filter "*.html" |
  Where-Object {
    $_.Name -ne "index.html" -and
    $_.Name -notmatch '\.bak_'
  }

Write-Host ""
Write-Host "Target folder: $targetDir" -ForegroundColor Cyan
Write-Host "Files to patch: $($files.Count)" -ForegroundColor Cyan
$files | ForEach-Object { Write-Host " - $($_.Name)" }

if ($files.Count -eq 0) {
  throw "No HTML files found to patch."
}

# backup folder inside tests
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupRoot = Join-Path $targetDir "_backup_ts_score_note_$stamp"
New-Item -ItemType Directory -Path $backupRoot | Out-Null

$patched = 0
$skipped = 0

foreach ($file in $files) {
  $path = $file.FullName
  $content = Get-Content $path -Raw
  $original = $content

  # patch injectOnce() so note goes INSIDE .ts-score9-wrap
  $content = [regex]::Replace(
    $content,
    'function\s+injectOnce\s*\(\)\s*\{\s*try\s*\{.*?\}\s*catch\s*\(e\)\s*\{\s*\}\s*\}',
@'
function injectOnce(){
    try {
      if (document.getElementById("tsScoreNoteInjected")) return;

      var anchor = document.querySelector(".ts-score9-wrap"); // your TMUA /9 UI block
      if (!anchor) return;

      // prevent duplicates inside the same score box
      var existing = anchor.querySelector(".ts-score-note");
      if (existing) return;

      var note = makeNoteEl();
      note.id = "tsScoreNoteInjected";

      // insert INSIDE the TMUA score block so it shares the same dialogue box
      anchor.appendChild(note);
    } catch(e){
      console.error("ts-score-note injection failed", e);
    }
  }
'@,
    [System.Text.RegularExpressions.RegexOptions]::Singleline
  )

  # patch only the .ts-score-note CSS block
  $content = [regex]::Replace(
    $content,
    '\.ts-score-note\s*\{.*?\}',
@'
.ts-score-note{
    margin: 8px 0 0 0;
    width: 100%;
    max-width: none;
    padding: 7px 10px;
    border: 1px dashed rgba(148,163,184,0.38);
    border-radius: 12px;
    background: rgba(255,255,255,0.35);
    box-shadow: none;
    box-sizing: border-box;
  }
'@,
    [System.Text.RegularExpressions.RegexOptions]::Singleline
  )

  if ($content -ne $original) {
    Copy-Item $path (Join-Path $backupRoot $file.Name) -Force
    Set-Content -Path $path -Value $content -Encoding UTF8
    Write-Host "Patched: $($file.Name)" -ForegroundColor Green
    $patched++
  }
  else {
    Write-Host "Skipped: $($file.Name)" -ForegroundColor Yellow
    $skipped++
  }
}

Write-Host ""
Write-Host "Done." -ForegroundColor Cyan
Write-Host "Patched: $patched"
Write-Host "Skipped: $skipped"
Write-Host "Backup folder: $backupRoot"