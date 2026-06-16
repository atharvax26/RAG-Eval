@echo off
title RAG Eval Studio
color 0A

echo.
echo  ============================================
echo   RAG Eval Studio  ^|  Starting...
echo  ============================================
echo.

:: Move into the project root (same folder as this bat file)
cd /d "%~dp0"

:: npm install if needed
if not exist "frontend\node_modules" (
    echo  Installing frontend dependencies, please wait...
    cd frontend
    npm install
    cd ..
    echo.
)

:: Launch Vite in a new window — no nested quotes, use a helper script
echo  Launching dev server...
start "RAG Eval - Dev Server" cmd /c "cd /d %~dp0frontend && npm run dev && pause"

:: Give Vite 6 seconds to boot
echo  Waiting for server to start...
timeout /t 6 /nobreak >nul

:: Open Chrome (try three locations)
echo  Opening browser...
if exist "%LocalAppData%\Google\Chrome\Application\chrome.exe" (
    start "" "%LocalAppData%\Google\Chrome\Application\chrome.exe" "http://localhost:3000"
    goto DONE
)
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" (
    start "" "%ProgramFiles%\Google\Chrome\Application\chrome.exe" "http://localhost:3000"
    goto DONE
)
start "" "http://localhost:3000"

:DONE
echo.
echo  App running at http://localhost:3000
echo  Close the "RAG Eval - Dev Server" window to stop.
echo.
pause
