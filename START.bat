@echo off
title DesignMentor AI - Startup
color 0A

echo.
echo =====================================================
echo   DesignMentor AI v2.1 - Starting Up
echo =====================================================
echo.

:: Start Backend
echo [1/2] Starting FastAPI Backend on port 8000...
start "DesignMentor Backend" cmd /k "cd /d "d:\DesignMentor AI - Intelligent System Design Interview Coach" && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

:: Wait 3 seconds for backend to start
timeout /t 3 /nobreak > nul

:: Start Frontend
echo [2/2] Starting Next.js Frontend on port 3000...
start "DesignMentor Frontend" cmd /k "cd /d "d:\DesignMentor AI - Intelligent System Design Interview Coach\frontend-next" && node "C:\Program Files\nodejs\node_modules\npm\bin\npm-cli.js" run dev"

:: Wait for frontend to start
timeout /t 5 /nobreak > nul

echo.
echo =====================================================
echo   Both servers starting up...
echo.
echo   Main App  : http://localhost:3000
echo   Legacy UI : http://localhost:8000
echo   API Docs  : http://localhost:8000/docs
echo =====================================================
echo.

:: Open browser
start http://localhost:3000

echo   Browser opened. Press any key to close this window.
pause > nul
