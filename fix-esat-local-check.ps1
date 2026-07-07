$ErrorActionPreference = "Stop"

$File = "public\esat-question-bank\index.html"

if (!(Test-Path $File)) {
  throw "Cannot find $File"
}

$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item $File "$File.backup_esat_local_check_fix_$Stamp"

$Html = Get-Content $File -Raw -Encoding UTF8

$Pattern = 'state\.answers\[key\]\s*=\s*\{\s*\.\.\.a,\s*checked:\s*true,\s*locked:\s*true,\s*isCorrect:\s*checked\.is_correct\s*===\s*true,\s*answer:\s*checked\.answer,\s*solution_html:\s*checked\.solution_html\s*\|\|\s*meta\.solution_html\s*\|\|\s*\(currentQuestion\s*&&\s*currentQuestion\.solution_html\)\s*\|\|\s*""\s*\};'

$ReplacementLines = @(
'      const selectedLabel = String(a.selected || "").trim();',
'      const correctLabel = String(',
'        checked.answer ||',
'        checked.correct_answer ||',
'        checked.correctAnswer ||',
'        meta.answer ||',
'        (currentQuestion && currentQuestion.answer) ||',
'        ""',
'      ).trim();',
'',
'      const locallyCorrect =',
'        selectedLabel.toUpperCase() === correctLabel.toUpperCase();',
'',
'      state.answers[key] = {',
'        ...a,',
'        checked: true,',
'        locked: locallyCorrect,',
'        isCorrect: locallyCorrect,',
'        answer: correctLabel,',
'        solution_html:',
'          checked.solution_html ||',
'          checked.explanation_html ||',
'          meta.solution_html ||',
'          (currentQuestion && currentQuestion.solution_html) ||',
'          ""',
'      };'
)

$Replacement = [string]::Join("`r`n", $ReplacementLines)

$NewHtml = [regex]::Replace($Html, $Pattern, $Replacement, 1)

if ($NewHtml -eq $Html) {
  Write-Host "Could not find old check block. It may already be patched or slightly different."
  Write-Host "Run this and paste output:"
  Write-Host 'Select-String -Path "public\esat-question-bank\index.html" -Pattern "state.answers\[key\] = \{|isCorrect: checked|answer: checked|solution_html:" -Context 4,10'
  throw "Patch not applied."
}

Set-Content -Path $File -Value $NewHtml -Encoding UTF8

Write-Host "ESAT local correctness check patch applied."
Write-Host "Backup created: $File.backup_esat_local_check_fix_$Stamp"
