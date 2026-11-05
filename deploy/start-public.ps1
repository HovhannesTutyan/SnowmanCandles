<#
.SYNOPSIS
  Publishes the candle shop from this PC through a free Cloudflare quick tunnel.

.DESCRIPTION
  1. Builds the React app (frontend/dist).
  2. Applies database migrations and collects static files.
  3. Starts Django in production mode (DEBUG off) with Waitress on 127.0.0.1:8080 —
     reachable only from this PC, so the tunnel is the only way in.
  4. Opens a Cloudflare quick tunnel and prints the public https://….trycloudflare.com link.

  Press Ctrl+C to stop: the tunnel and the server both shut down.
  The link changes every time this script starts.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File deploy\start-public.ps1
#>
param(
    [int]$Port = 8080,
    [switch]$SkipBuild
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $root 'backend'
$frontend = Join-Path $root 'frontend'
$python = Join-Path $backend '.venv\Scripts\python.exe'

$cloudflared = (Get-Command cloudflared -ErrorAction SilentlyContinue).Source
if (-not $cloudflared) {
    $cloudflared = @(
        "$env:ProgramFiles\cloudflared\cloudflared.exe",
        "${env:ProgramFiles(x86)}\cloudflared\cloudflared.exe"
    ) | Where-Object { Test-Path $_ } | Select-Object -First 1
}
if (-not $cloudflared) {
    throw 'cloudflared not found. Install it with: winget install --id Cloudflare.cloudflared -e'
}
if (-not (Test-Path $python)) {
    throw "Python virtual environment not found at $python (see backend/README.md)."
}

# Production settings for this session only (backend/.env keeps the development values).
$env:DEBUG = 'False'
$env:ALLOWED_HOSTS = 'localhost,127.0.0.1,.trycloudflare.com'
$env:CSRF_TRUSTED_ORIGINS = 'https://*.trycloudflare.com'
$env:BEHIND_PROXY = 'True'
$env:SERVE_MEDIA = 'True'

if (-not $SkipBuild) {
    Write-Host '==> Building the frontend' -ForegroundColor Cyan
    Push-Location $frontend
    try {
        npm run build
        if ($LASTEXITCODE -ne 0) { throw 'Frontend build failed.' }
    } finally { Pop-Location }
}

Write-Host '==> Preparing Django (migrations, static files)' -ForegroundColor Cyan
Push-Location $backend
try {
    & $python manage.py migrate --noinput
    if ($LASTEXITCODE -ne 0) { throw 'Migrations failed.' }
    & $python manage.py collectstatic --noinput | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'collectstatic failed.' }
} finally { Pop-Location }

Write-Host "==> Starting the server on http://127.0.0.1:$Port" -ForegroundColor Cyan
$server = Start-Process -FilePath $python `
    -ArgumentList '-m', 'waitress', "--listen=127.0.0.1:$Port", '--threads=8',
        # The tunnel connects from this PC and says the visitor used https; trust that,
        # so links and image URLs are https too.
        '--trusted-proxy=127.0.0.1', '--trusted-proxy-headers=x-forwarded-proto',
        'config.wsgi:application' `
    -WorkingDirectory $backend -PassThru -NoNewWindow

try {
    Start-Sleep -Seconds 2
    if ($server.HasExited) { throw 'The server stopped right away; see the messages above.' }

    Write-Host '==> Opening the public tunnel (look for the https://…trycloudflare.com link below)' -ForegroundColor Cyan
    Write-Host '    Press Ctrl+C to stop sharing.' -ForegroundColor Yellow
    & $cloudflared tunnel --no-autoupdate --url "http://127.0.0.1:$Port"
} finally {
    if (-not $server.HasExited) {
        Stop-Process -Id $server.Id -Force
        Write-Host '==> Server stopped.' -ForegroundColor Cyan
    }
}
