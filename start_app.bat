@echo off
setlocal enabledelayedexpansion
title RAG Eval Studio — Launcher
color 0A

echo.
echo  ============================================
echo   RAG Eval Studio  ^|  Starting up...
echo  ============================================
echo.

:: ── 1. Check Docker Desktop is running ──────────────────────────────────────
echo [1/5] Checking Docker...
docker info >nul 2>&1
if errorlevel 1 (
    echo  Docker Desktop is not running. Launching it now...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    echo  Waiting 30 seconds for Docker to start...
    timeout /t 30 /nobreak >nul
    docker info >nul 2>&1
    if errorlevel 1 (
        echo.
        echo  ERROR: Docker Desktop did not start in time.
        echo  Please start Docker Desktop manually and re-run this file.
        pause
        exit /b 1
    )
)
echo  Docker is running.
echo.

:: ── 2. Start backend services (postgres + qdrant + backend) via Docker ───────
echo [2/5] Starting backend services (PostgreSQL + Qdrant + FastAPI)...
docker-compose up -d db qdrant backend
if errorlevel 1 (
    echo.
    echo  ERROR: docker-compose failed. Check docker-compose.yml and try again.
    pause
    exit /b 1
)
echo  Backend services started.
echo.

:: ── 3. Frontend — npm install if node_modules is missing ────────────────────
echo [3/5] Setting up frontend...
if not exist "frontend\node_modules" (
    echo  node_modules not found — running npm install (first time only)...
    pushd frontend
    call npm install
    if errorlevel 1 (
        echo  ERROR: npm install failed. Make sure Node.js is installed.
        popd
        pause
        exit /b 1
    )
    popd
    echo  npm install complete.
) else (
    echo  node_modules found — skipping install.
)
echo.

:: ── 4. Launch frontend dev server in a new terminal window ─────────────────
echo [4/5] Launching Vite dev server on http://localhost:3000 ...
start "RAG Eval — Frontend Dev Server" cmd /k "cd /d "%~dp0frontend" && npm run dev"
echo  Frontend dev server window opened.
echo.

:: ── 5. Wait for the frontend to be ready, then open Chrome ─────────────────
echo [5/5] Waiting for frontend to be ready...
set RETRIES=0
:WAIT_LOOP
timeout /t 2 /nobreak >nul
curl -s -o nul -w "%%{http_code}" http://localhost:3000 | findstr "200" >nul 2>&1
if errorlevel 1 (
    set /a RETRIES+=1
    if !RETRIES! lss 20 (
        echo  Still waiting... (!RETRIES!/20^)
        goto WAIT_LOOP
    )
    echo  Timed out waiting for frontend — opening Chrome anyway...
)

echo  Opening Chrome...
start "" "chrome.exe" "http://localhost:3000"
if errorlevel 1 (
    :: Fallback: try the full path for Chrome
    start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" "http://localhost:3000"
    if errorlevel 1 (
        :: Last fallback: open with default browser
        start "" "http://localhost:3000"
    )
)

echo.
echo  ============================================
echo   All systems go!
echo.
echo   Frontend  : http://localhost:3000
echo   Backend   : http://localhost:8000/docs
echo   Qdrant UI : http://localhost:6333/dashboard
echo.
echo   To stop everything, run:  stop_app.bat
echo  ============================================
echo.
pause
