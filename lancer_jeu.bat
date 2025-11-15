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

@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ================================================
echo   🎮 JEU DE CARTES SMILE - MODE PUBLIC
echo   (avec Cloudflare Tunnel)
echo ================================================
echo.

REM Vérifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé
    pause
    exit /b 1
)

REM Créer l'environnement virtuel si nécessaire
if not exist ".venv" (
    echo 📦 Installation initiale...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    pip install flask flask-socketio python-socketio eventlet
) else (
    call .venv\Scripts\activate.bat
)

REM Vérifier si cloudflared est installé
where cloudflared >nul 2>&1
if errorlevel 1 (
    echo ❌ cloudflared n'est pas installé
    echo.
    echo 📦 Pour installer cloudflared :
    echo    1. Allez sur https://github.com/cloudflare/cloudflared/releases
    echo    2. Téléchargez cloudflared-windows-amd64.exe
    echo    3. Renommez-le en cloudflared.exe
    echo    4. Placez-le dans ce dossier ou dans votre PATH
    echo.
    pause
    exit /b 1
)

echo ✅ cloudflared détecté
echo.

REM Lancer le serveur Flask en arrière-plan
start /b python app.py

echo ⏳ Démarrage du serveur Flask...
timeout /t 3 >nul

echo.
echo 🚀 Lancement du tunnel Cloudflare...
echo.
echo ⚠️  IMPORTANT : L'URL sera affichée ci-dessous
echo    Cherchez une ligne comme :
echo    https://xxxx-xxxx-xxxx.trycloudflare.com
echo.
echo ⚠️  Partagez cette adresse HTTPS avec vos amis !
echo.
echo ⚠️  Pour arrêter, fermez cette fenêtre ou appuyez sur Ctrl+C
echo.

cloudflared tunnel --url http://localhost:5000

echo.
echo ⚠️  Le tunnel s'est arrêté
pause
endlocal