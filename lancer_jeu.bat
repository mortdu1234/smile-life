@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ================================================
echo   🎮 JEU DE CARTES SMILE - LANCEUR COMPLET
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

echo.
echo 📋 CHOIX DU MODE :
echo.
echo   [1] 🏠 Jeu LOCAL ^(même réseau WiFi uniquement^)
echo   [2] 🌍 Jeu PUBLIC ^(accessible depuis Internet avec Serveo^)
echo.
set /p choice="Votre choix (1 ou 2) : "

if "%choice%"=="1" goto local
if "%choice%"=="2" goto public
goto invalid

:local
echo.
echo ================================================
echo   🏠 MODE LOCAL
echo ================================================
echo.

REM Obtenir l'adresse IP locale
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set IP=%%a
    set IP=!IP:~1!
    goto :found_ip
)
:found_ip

echo ✅ Démarrage du serveur...
echo.
echo 📍 Accès au jeu :
echo.
echo    Sur cet ordinateur : http://localhost:5000
echo    Autres appareils : http://!IP!:5000
echo.
python app.py
goto end

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