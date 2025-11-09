@echo off
chcp 65001 >nul
color 0A

echo ========================================
echo   Lancement Flask + Cloudflare Tunnel
echo ========================================
echo.

REM Vérifier si app.py existe
if not exist "app.py" (
    echo [ERREUR] Le fichier app.py n'existe pas dans ce dossier
    pause
    exit /b 1
)

REM Menu de choix
:menu
echo Choisissez le mode de lancement :
echo.
echo [1] Mode PRIVE (localhost uniquement)
echo [2] Mode PUBLIC (accessible depuis Internet via Cloudflare)
echo [Q] Quitter
echo.
set /p choice="Votre choix (1/2/Q) : "

if /i "%choice%"=="Q" exit /b 0
if "%choice%"=="1" goto private
if "%choice%"=="2" goto public
echo Choix invalide, veuillez reessayer.
echo.
goto menu

:private
cls
echo ========================================
echo   MODE PRIVE - Localhost uniquement
echo ========================================
echo.
echo Lancement de l'application Flask...
echo.
start "Flask Application" cmd /k "title Flask Application (PRIVE) && color 0E && echo ======================================== && echo    APPLICATION FLASK - MODE PRIVE && echo ======================================== && echo. && echo URL locale : http://127.0.0.1:5000 && echo. && python app.py"
echo.
echo ========================================
echo Application lancee en mode PRIVE
echo URL : http://127.0.0.1:5000
echo ========================================
echo.
echo Appuyez sur une touche pour quitter...
pause >nul
exit /b 0

:public
cls
echo ========================================
echo   MODE PUBLIC - Cloudflare Tunnel
echo ========================================
echo.

REM Vérifier si cloudflared existe
where cloudflared >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] cloudflared n'est pas installe ou pas dans le PATH
    echo Telechargez-le depuis: https://github.com/cloudflare/cloudflared/releases
    echo.
    pause
    exit /b 1
)

echo [1/2] Demarrage de l'application Flask dans un terminal separe...
echo.

REM Lancer Flask dans une nouvelle fenêtre
start "Flask Application" cmd /k "title Flask Application (PUBLIC) && color 0E && echo ======================================== && echo    APPLICATION FLASK - MODE PUBLIC && echo ======================================== && echo. && python app.py"

REM Attendre que Flask démarre
timeout /t 4 /nobreak >nul

echo [2/2] Creation du tunnel Cloudflare...
echo.
echo ========================================
echo   VOTRE URL PUBLIQUE APPARAITRA ICI :
echo ========================================
echo.

cloudflared tunnel --url http://localhost:5000

echo.
echo ========================================
echo Tunnel ferme.
echo FERMEZ MANUELLEMENT la fenetre Flask si necessaire.
echo.
echo Appuyez sur une touche pour quitter...
pause >nul