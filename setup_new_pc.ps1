# setup_new_pc.ps1 — Автоматическая настройка проекта на новом ПК
# Запуск: .\setup_new_pc.ps1

$ErrorActionPreference = "Stop"
$BaseDir = $PSScriptRoot

Write-Host "🔍 Проверка Python..." -ForegroundColor Cyan
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python не найден! Установи Python 3.11+ с https://python.org" -ForegroundColor Red
    exit 1
}
Write-Host "✅ $pythonVersion" -ForegroundColor Green

$major, $minor = (python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')").Split('.')
if ([int]$minor -lt 11) {
    Write-Host "❌ Требуется Python 3.11+, найдено $pythonVersion" -ForegroundColor Red
    exit 1
}

Write-Host "`n📦 Создание виртуального окружения..." -ForegroundColor Cyan
if (Test-Path "$BaseDir\.venv") {
    Write-Host "⚠️  .venv уже существует, пропускаю" -ForegroundColor Yellow
} else {
    python -m venv .venv
    Write-Host "✅ .venv создан" -ForegroundColor Green
}

Write-Host "`n🔌 Активация окружения..." -ForegroundColor Cyan
& "$BaseDir\.venv\Scripts\Activate.ps1"

Write-Host "`n📥 Обновление pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip --quiet

Write-Host "`n📦 Установка chat-service..." -ForegroundColor Cyan
Set-Location "$BaseDir\chat-service"
pip install -e . --quiet
Write-Host "✅ chat-service установлен" -ForegroundColor Green

Write-Host "`n📦 Установка context-engine..." -ForegroundColor Cyan
Set-Location "$BaseDir\context-engine"
pip install -e . --quiet
Write-Host "✅ context-engine установлен" -ForegroundColor Green

Write-Host "`n📝 Создание .env файлов из примеров..." -ForegroundColor Cyan
Set-Location $BaseDir
if (-not (Test-Path "chat-service\.env")) {
    Copy-Item "chat-service\.env.example" "chat-service\.env"
    Write-Host "✅ chat-service/.env создан" -ForegroundColor Green
}
if (-not (Test-Path "context-engine\.env")) {
    Copy-Item "context-engine\.env.example" "context-engine\.env"
    Write-Host "✅ context-engine/.env создан" -ForegroundColor Green
}

Write-Host "`n Очистка кэша..." -ForegroundColor Cyan
Remove-Item -Recurse -Force "$BaseDir\chat-service\__pycache__" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "$BaseDir\context-engine\__pycache__" -ErrorAction SilentlyContinue

Write-Host "`n🎉 ГОТОВО! Проект настроен." -ForegroundColor Green
Write-Host "`n📋 Следующие шаги:" -ForegroundColor Cyan
Write-Host "  1. Запусти MinIO (Docker или minio.exe)" -ForegroundColor White
Write-Host "  2. Окно 1: cd chat-service && uvicorn app.main:app --port 8000" -ForegroundColor White
Write-Host "  3. Окно 2: cd context-engine && uvicorn context_engine.main:app --port 8002" -ForegroundColor White
Write-Host "  4. Открой http://127.0.0.1:8000/docs" -ForegroundColor White