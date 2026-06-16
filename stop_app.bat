@echo off
title RAG Eval Studio — Stopping
color 0C

echo.
echo  ============================================
echo   RAG Eval Studio  ^|  Shutting down...
echo  ============================================
echo.

echo Stopping Docker services...
docker-compose down
echo.
echo Closing frontend dev server window...
taskkill /fi "WindowTitle eq RAG Eval — Frontend Dev Server" /f >nul 2>&1
echo.
echo  All services stopped.
echo.
pause
