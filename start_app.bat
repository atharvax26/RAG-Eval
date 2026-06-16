@echo off
setlocal enabledelayedexpansion
title RAG Eval Studio — Launcher
color 0A

echo.
echo  ============================================
echo   RAG Eval Studio  ^|  Starting up...
echo  ============================================
echo.

:: ── 1. Check Node.js is installed ───────────────────────────────────────────
echo [1/4] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  ERROR: Node.js is not installed or not in PATH.
    echo  Download it from https://nodejs.org and re-run this file.
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('node --version') do echo  Node.js %%v found.
echo.

:: ── 2. Docker check (optional — skip if not installed) ──────────────────────
echo [2/4] Checking Docker (optional for UI preview)...
docker info >nul 2>&1
if errorlevel 1 (
    echo  Docker not available — running in FRONTEND-ONLY mode.
    echo  The UI will load. API calls will show errors (expected without backend).
) else (
    echo  Docker is running — starting backend services...
    docker-compose up -d db qdrant backend >nul 2>&1
    if errorlevel 1 (
        echo  Backend services could not start — continuing in frontend-only mode.
    ) else (
        echo  Backend services started (PostgreSQL + Qdrant + FastAPI).
    )
)
echo.

:: ── 3. npm install if node_modules missing ──────────────────────────────────
echo [3/4] Setting up frontend...
cd /d "%~dp0frontend"
if not exist "node_modules" (
    echo  Installing npm packages (first time only, may take 1-2 minutes)...
    call npm install
    if errorlevel 1 (
        echo.
        echo  ERROR: npm install failed.
        pause
        exit /b 1
    )
    echo  npm install complete.
) else (
    echo  Dependencies already installed.
)
echo.

:: ── 4. Start Vite dev server and open browser ───────────────────────────────
echo [4/4] Starting frontend dev server...

:: Launch the dev server in a new window and capture its PID
start "RAG Eval — Frontend Dev Server" cmd /k "cd /d "%~dp0frontend" && npm run dev"

:: Wait for port 5173 or 3000 to respond (Vite defaults to 5173)
echo  Waiting for dev server to be ready...
set RETRIES=0
set PORT=5173

:WAIT_LOOP
timeout /t 2 /nobreak >nul
curl -s --max-time 2 http://localhost:!PORT! >nul 2>&1
if not errorlevel 1 goto OPEN_BROWSER

:: Also try port 3000 (set in vite.config.ts)
curl -s --max-time 2 http://localhost:3000 >nul 2>&1
if not errorlevel 1 (
    set PORT=3000
    goto OPEN_BROWSER
)

set /a RETRIES+=1
if !RETRIES! lss 25 (
    echo  Still waiting... (!RETRIES!/25^)
    goto WAIT_LOOP
)
echo  Dev server taking longer than expected — opening browser anyway...
set PORT=3000

:OPEN_BROWSER
echo  Opening Chrome at http://localhost:!PORT! ...
echo.

:: Try chrome in PATH first, then known install locations, then default browser
where chrome >nul 2>&1 && (start "" chrome "http://localhost:!PORT!" & goto DONE)
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" (
    start "" "%ProgramFiles%\Google\Chrome\Application\chrome.exe" "http://localhost:!PORT!"
    goto DONE
)
if exist "%LocalAppData%\Google\Chrome\Application\chrome.exe" (
    start "" "%LocalAppData%\Google\Chrome\Application\chrome.exe" "http://localhost:!PORT!"
    goto DONE
)
:: Last resort: default browser
start "" "http://localhost:!PORT!"

:DONE
echo  ============================================
echo   RAG Eval Studio is running!
echo.
echo   App  :  http://localhost:!PORT!
if not "!PORT!"=="3000" echo   Also :  http://localhost:3000
echo.
echo   Close the "Frontend Dev Server" window to stop.
echo  ============================================
echo.
pause
