$ErrorActionPreference = "Stop"

$File = "public\esat-question-bank\index.html"

if (!(Test-Path $File)) {
  throw "Cannot find $File"
}

$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item $File "$File.backup_esat_solution_reattempt_fix_$Stamp"

$Html = Get-Content $File -Raw -Encoding UTF8
$Changes = 0

function Replace-One($Old, $New, $Label) {
  if ($script:Html.Contains($Old)) {
    $script:Html = $script:Html.Replace($Old, $New)
    $script:Changes++
    Write-Host "Patched: $Label"
  } else {
    Write-Host "Not found or already patched: $Label"
  }
}

# 1) Do not disable wrong checked answers permanently.
Replace-One `
  'const locked = a.checked ? "disabled" : "";' `
  'const locked = (a.checked && a.isCorrect === true) ? "disabled" : "";' `
  "wrong answers remain selectable"

# 2) Allow selecting a new option after a wrong checked answer.
$OldGuard = 'if (state.answers[key].checked) return;'

$NewGuard = "if (state.answers[key].checked && state.answers[key].isCorrect === true) return;`r`n`r`n      if (state.answers[key].checked && state.answers[key].isCorrect === false) {`r`n        state.answers[key] = {`r`n          ...state.answers[key],`r`n          checked: false,`r`n          locked: false,`r`n          isCorrect: false`r`n        };`r`n      }"

Replace-One $OldGuard $NewGuard "wrong checked answer can be reattempted"

# 3) Store solution from the current question when checker response does not include it.
Replace-One `
  'solution_html: checked.solution_html || ""' `
  'solution_html: checked.solution_html || meta.solution_html || (currentQuestion && currentQuestion.solution_html) || ""' `
  "solution_html saved after checking"

# 4) Render solution using fallback from current question, including older saved attempts.
$OldRender = 'body.innerHTML = a.solution_html || "";'

$NewRender = "const solutionHtml = a.solution_html || meta.solution_html || (currentQuestion && currentQuestion.solution_html) || """";`r`n    body.innerHTML = solutionHtml || ""<p>Solution not available for this question yet.</p>"";`r`n`r`n    if (window.MathJax && window.MathJax.typesetPromise) {`r`n      setTimeout(function () {`r`n        window.MathJax.typesetPromise([body]).catch(function () {});`r`n      }, 0);`r`n    }"

Replace-One $OldRender $NewRender "solution render fallback"

Set-Content -Path $File -Value $Html -Encoding UTF8

Write-Host ""
Write-Host "ESAT solution + wrong-reattempt patch complete."
Write-Host "Changes applied: $Changes"
Write-Host "Backup created: $File.backup_esat_solution_reattempt_fix_$Stamp"

if ($Changes -lt 4) {
  Write-Host "WARNING: Fewer than 4 changes applied. Verify before build."
}
