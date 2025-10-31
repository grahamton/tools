# PromptKit Business Runner (PowerShell)
# Usage: run from repo root: .\promptkit-run.ps1

Write-Host "PromptKit Business Runner" -ForegroundColor Cyan
Write-Host "This will generate a single Iterate Card (Diagnosis -> Fix -> Validation)." -ForegroundColor Gray
Write-Host ""

$seed = (Read-Host "Seed (one sentence: what the assistant does and for whom)").Trim()
if (-not $seed) { Write-Error "Seed is required."; exit 1 }

$friction = (Read-Host "Friction (one sentence: biggest failure right now)").Trim()
if (-not $friction) { Write-Error "Friction is required."; exit 1 }

Write-Host ""
Write-Host "Optional: pick a pattern (press Enter to auto-detect):" -ForegroundColor Gray
Write-Host "  1) constraint-ledger   (keep a running list of constraints)"
Write-Host "  2) contrastive-clarify (one either/or to pin meaning)"
Write-Host "  3) exemplar-propose    (two tiny concrete options)"
Write-Host "  4) override-hook       (quick staff commands)"
$choice = Read-Host "Choice (1-4 or blank)"

$pattern = $null
switch ($choice) {
  "1" { $pattern = "constraint-ledger" }
  "2" { $pattern = "contrastive-clarify" }
  "3" { $pattern = "exemplar-propose" }
  "4" { $pattern = "override-hook" }
  default { $pattern = $null }
}

function Use-InstalledCli {
  return [bool](Get-Command promptkit -ErrorAction SilentlyContinue)
}

function Test-Python {
  return [bool](Get-Command python -ErrorAction SilentlyContinue)
}

function Test-PythonModule([string]$Name) {
  if (-not (Test-Python)) { return $false }
  & python -c "import $Name" 2>$null
  return ($LASTEXITCODE -eq 0)
}

function Run-Iterate([string]$Seed,[string]$Friction,[string]$Pattern) {
  if (Use-InstalledCli) {
    $argsList = @("iterate","--seed", $Seed, "--friction", $Friction, "--ascii")
    if ($Pattern) { $argsList += @("--pattern", $Pattern) }
    & promptkit @argsList
    return $LASTEXITCODE
  }

  if (-not (Test-Python)) {
    Write-Error "Python not found. Please install Python 3.9+ or install the CLI with: python -m pip install -e ."
    return 1
  }
  if (-not (Test-PythonModule "typer")) {
    Write-Error "Missing dependency: 'typer'. Install either the package (python -m pip install -e .) or just Typer (python -m pip install typer)."
    return 1
  }
  $repoSrc = Join-Path $PSScriptRoot "src"
  $env:PYTHONPATH = $repoSrc
  $pyArgs = @("-m", "promptkit.cli", "iterate", "--seed", $Seed, "--friction", $Friction, "--ascii")
  if ($Pattern) { $pyArgs += @("--pattern", $Pattern) }
  & python @pyArgs
  return $LASTEXITCODE
}

Write-Host ""; Write-Host "Generating Iterate Card..." -ForegroundColor Yellow
$code = Run-Iterate -Seed $seed -Friction $friction -Pattern $pattern
if ($code -ne 0) { exit $code }

Write-Host ""; Write-Host "Done." -ForegroundColor Green
