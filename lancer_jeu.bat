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

:public
echo.
echo ================================================
echo   🌍 MODE PUBLIC ^(avec tunnel Serveo^)
echo ================================================
echo.

REM Vérifier SSH
where ssh >nul 2>&1
if errorlevel 1 (
    echo ❌ SSH n'est pas installé
    echo 📦 Installez OpenSSH depuis les paramètres Windows
    echo    ^(Paramètres ^> Applications ^> Fonctionnalités facultatives^)
    pause
    exit /b 1
)

echo ✅ SSH détecté
echo.

set subdomain=smile-life

echo 🚀 Lancement du serveur ET du tunnel...
echo.
echo 📍 Votre jeu sera accessible sur :
echo    https://%subdomain%.serveo.net
echo.
echo ⚠️  Partagez cette adresse avec vos amis !
echo.
timeout /t 2 >nul

REM Lancer le serveur Flask en arrière-plan
start /b python app.py

echo ⏳ Démarrage du serveur Flask...
timeout /t 3 >nul

echo 📡 Connexion au tunnel Serveo...
echo.
echo ⚠️  Pour arrêter le serveur, fermez cette fenêtre ou appuyez sur Ctrl+C
echo.

:tunnel_loop
ssh -o ServerAliveInterval=60 -o ServerAliveCountMax=3 -R %subdomain%:80:127.0.0.1:5000 serveo.net
echo ⚠️ Connexion perdue. Reconnexion dans 5 secondes...
timeout /t 5 >nul
goto tunnel_loop

:invalid
echo Choix invalide
pause
exit /b 1

:end
endlocal