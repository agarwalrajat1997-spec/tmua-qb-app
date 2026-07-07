$ErrorActionPreference = "Stop"

$File = "public\tmua-question-bank\index.html"

if (!(Test-Path $File)) {
  throw "Cannot find $File"
}

$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item $File "$File.backup_safe_mojibake_fix_$Stamp"

$Html = Get-Content $File -Raw -Encoding UTF8

function U([int]$CodePoint) {
  return [char]::ConvertFromUtf32($CodePoint)
}

$emDash   = U 0x2014
$enDash   = U 0x2013
$bullet   = U 0x2022
$middot   = U 0x00B7
$flag     = U 0x2691
$bug      = U 0x1F41E
$star     = U 0x2605
$emptyStar = U 0x2606

# Header / top labels
$Html = [regex]::Replace(
  $Html,
  '<div class="subbrand">\([^<]*Thriving Scholars\)</div>',
  '<div class="subbrand">(Practice + Review ' + $emDash + ' Thriving Scholars)</div>'
)

$Html = [regex]::Replace(
  $Html,
  '<div id="saveIndicator" class="save-indicator" style="display:\s*none;">[^<]*</div>',
  '<div id="saveIndicator" class="save-indicator" style="display: none;">Saved</div>'
)

# Flag button initial HTML
$Html = [regex]::Replace(
  $Html,
  '(<button id="btnFlag" class="btn light" onclick="ACTIONS\.toggleFlag\(\)">)[\s\S]*?(</button>)',
  '${1}Flag for Review${2}'
)

# Floating bug button
$BugButton = @"
<button
  type="button"
  id="bugFloatingBtn"
  class="bug-floating-btn"
  title="Report a problem in this question"
  aria-label="Report a problem in this question"
  onclick="BUG_REPORT.open()"
>$bug</button>
"@

$Html = [regex]::Replace(
  $Html,
  '<button\s+type="button"\s+id="bugFloatingBtn"[\s\S]*?</button>',
  $BugButton
)

# Footer buttons
$Html = [regex]::Replace(
  $Html,
  '(<button type="button" class="btn light" id="tsWorkspaceBtn"[\s\S]*?>)[\s\S]*?(</button>)',
  '${1}TMUA Workspace${2}'
)

$Html = [regex]::Replace(
  $Html,
  '<button onclick="NAV\.prev\(\)">[\s\S]*?</button>',
  '<button onclick="NAV.prev()">Previous</button>'
)

$Html = [regex]::Replace(
  $Html,
  '<button onclick="NAV\.next\(\)">[\s\S]*?</button>',
  '<button onclick="NAV.next()">Next</button>'
)

# Small UI text
$Html = [regex]::Replace(
  $Html,
  '<div class="small">Tip: pick[\s\S]*?drills\.</div>',
  '<div class="small">Tip: pick 2' + $enDash + '3 levels for focused drills.</div>'
)

$Html = [regex]::Replace(
  $Html,
  '<div class="small">Only counts questions you have checked[\s\S]*?</div>',
  '<div class="small">Only counts questions you have checked after pressing Check.</div>'
)

$Html = [regex]::Replace(
  $Html,
  '(<textarea id="backupText"[^>]*placeholder=")[^"]*(")',
  '${1}Click Generate Export${2}'
)

# Stars
$Html = [regex]::Replace(
  $Html,
  'return\s+"[^"]*"\.repeat\(d\)\s*\+\s*"[^"]*"\.repeat\(5-d\);',
  'return "' + $star + '".repeat(d) + "' + $emptyStar + '".repeat(5-d);'
)

# Dynamic flag text
$Html = [regex]::Replace(
  $Html,
  'flagBtn\.textContent\s*=\s*"[^"]*Flagged";',
  'flagBtn.textContent = "Flagged";'
)

$Html = [regex]::Replace(
  $Html,
  'flagBtn\.textContent\s*=\s*"[^"]*Flag for Review";',
  'flagBtn.textContent = "Flag for Review";'
)

# Dynamic status/topic text
$Html = [regex]::Replace(
  $Html,
  'status\.textContent\s*=\s*"Checked[^"]*Correct";',
  'status.textContent = "Checked ' + $bullet + ' Correct";'
)

$Html = [regex]::Replace(
  $Html,
  'status\.textContent\s*=\s*"Checked[^"]*Incorrect";',
  'status.textContent = "Checked ' + $bullet + ' Incorrect";'
)

$Html = [regex]::Replace(
  $Html,
  'setText\("metaTopic", \(meta\.topic \|\| ""\) \+ \(meta\.subtopic \? "[^"]*" \+ meta\.subtopic : ""\)\);',
  'setText("metaTopic", (meta.topic || "") + (meta.subtopic ? " ' + $bullet + ' " + meta.subtopic : ""));'
)

# Navigator title and icons
$Html = [regex]::Replace(
  $Html,
  'btn\.title\s*=\s*"Question "\s*\+\s*n\s*\+\s*"[^"]*"\s*\+\s*chapterLabel\s*\+\s*\(q\.subtopic \? "[^"]*" \+ q\.subtopic : ""\);',
  'btn.title = "Question " + n + " ' + $middot + ' " + chapterLabel + (q.subtopic ? " ' + $middot + ' " + q.subtopic : "");'
)

$Html = [regex]::Replace(
  $Html,
  'icons\.innerHTML\s*=\s*a\.flagged\s*\?\s*"[^"]*"\s*:\s*"";',
  'icons.innerHTML = a.flagged ? "' + $flag + '" : "";'
)

# Bug report email subject and modal label
$Html = [regex]::Replace(
  $Html,
  'email_subject:\s*"TMUA bug report[^"]*"\s*\+\s*qTitle,',
  'email_subject: "TMUA bug report ' + $emDash + ' " + qTitle,'
)

$Html = [regex]::Replace(
  $Html,
  'label\.textContent\s*=\s*payload\.question_label\s*\+\s*"[^"]*"\s*\+\s*payload\.paper\s*\+\s*"[^"]*"\s*\+\s*payload\.topic;',
  'label.textContent = payload.question_label + " ' + $middot + ' " + payload.paper + " ' + $middot + ' " + payload.topic;'
)

Set-Content -Path $File -Value $Html -Encoding UTF8

$After = Get-Content $File -Raw -Encoding UTF8

$BadChars = @(
  [char]0x00E2,
  [char]0x00F0,
  [char]0x00C3,
  [char]0x00C2,
  [char]0xFFFD
)

$BadCount = 0
foreach ($Ch in $BadChars) {
  $BadCount += ([regex]::Matches($After, [regex]::Escape([string]$Ch))).Count
}

Write-Host "Safe TMUA mojibake fix complete."
Write-Host "Remaining bad-character count: $BadCount"
Write-Host "Backup created: $File.backup_safe_mojibake_fix_$Stamp"
