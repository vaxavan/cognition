# setup_new_pc.ps1
# Запуск: .\setup_new_pc.ps1

$ErrorActionPreference = "Stop"

# Безопасное определение папки скрипта
if ($PSScriptRoot) {
    $BaseDir = $PSScriptRoot
} else {
    $BaseDir = $PWD.Path
}

Write-Host "[1/6] Checking Python version..." -ForegroundColor Cyan
try {
    $pythonVer = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
    $minor = [int]($pythonVer.Split('.')[1])
    if ($minor -lt 11) {
        Write-Host "ERROR: Python 3.11+ required. Found: $pythonVer" -ForegroundColor Red
        exit 1
    }
    Write-Host "OK: Python $pythonVer" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python not found or not in PATH. Install Python 3.11+ from python.org" -ForegroundColor Red
    exit 1
}

Write-Host "[2/6] Creating virtual environment..." -ForegroundColor Cyan
$venvPath = Join-Path $BaseDir ".venv"
if (-not (Test-Path $venvPath)) {
    python -m venv $venvPath
    Write-Host "OK: .venv created" -ForegroundColor Green
} else {
    Write-Host "SKIP: .venv already exists" -ForegroundColor Yellow
}

Write-Host "[3/6] Activating environment..." -ForegroundColor Cyan
& "$venvPath\Scripts\Activate.ps1"

Write-Host "[4/6] Upgrading pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip --quiet

Write-Host "[5/6] Installing services..." -ForegroundColor Cyan
$services = @("chat-service", "context-engine")
foreach ($svc in $services) {
    $svcDir = Join-Path $BaseDir $svc
    if (Test-Path (Join-Path $svcDir "pyproject.toml")) {
        Write-Host "  -> Installing $svc..." -ForegroundColor DarkCyan
        Set-Location $svcDir
        pip install -e . --quiet
    } else {
        Write-Host "  -> WARNING: $svc/pyproject.toml not found, skipping" -ForegroundColor Yellow
    }
}

Write-Host "[6/6] Setting up .env files..." -ForegroundColor Cyan
Set-Location $BaseDir
$envFiles = @(
    @{Src="chat-service\.env.example"; Dst="chat-service\.env"},
    @{Src="context-engine\.env.example"; Dst="context-engine\.env"}
)
foreach ($f in $envFiles) {
    $src = Join-Path $BaseDir $f.Src
    $dst = Join-Path $BaseDir $f.Dst
    if ((Test-Path $src) -and (-not (Test-Path $dst))) {
        Copy-Item $src $dst
        Write-Host "OK: Created $dst" -ForegroundColor Green
    }
}

# Очистка кэша
Get-ChildItem -Path $BaseDir -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "`nSUCCESS: Project setup complete!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "  1. Start MinIO (Docker or minio.exe)"
Write-Host "  2. Terminal 1: cd chat-service && uvicorn app.main:app --port 8000"
Write-Host "  3. Terminal 2: cd context-engine && uvicorn context_engine.main:app --port 8002"
Write-Host "  4. Open: http://127.0.0.1:8000/docs"