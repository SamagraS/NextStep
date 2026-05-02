param (
    [Parameter(Mandatory=$false)]
    [ValidateSet('unit', 'api', 'integration', 'all')]
    [string]$Type = 'all'
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path "venv\Scripts\pytest.exe")) {
    Write-Error "Pytest not found. Please ensure your virtual environment is activated and dependencies are installed."
    exit 1
}

$PytestCmd = "venv\Scripts\pytest.exe"

if ($Type -eq 'all') {
    Write-Host "Running all tests..."
    & $PytestCmd
} else {
    Write-Host "Running $Type tests..."
    & $PytestCmd -m $Type
}

if ($LASTEXITCODE -ne 0) {
    Write-Error "Tests failed!"
    exit $LASTEXITCODE
}
