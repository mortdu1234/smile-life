@echo off
chcp 65001 >nul
title Lanceur Jeu Smile

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
if not exist "venv" (
    echo 📦 Installation initiale...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install flask flask-socketio python-socketio eventlet
)

echo.
echo 📋 CHOIX DU MODE :
echo.
echo   [1] 🏠 Jeu LOCAL (même réseau WiFi uniquement)
echo   [2] 🌍 Jeu PUBLIC (accessible depuis Internet avec Serveo)
echo.
set /p choice="Votre choix (1 ou 2) : "

if "%choice%"=="1" goto local
if "%choice%"=="2" goto public
echo Choix invalide
pause
exit /b 1

:local
echo.
echo ================================================
echo   🏠 MODE LOCAL
echo ================================================
echo.
call venv\Scripts\activate.bat

for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do set IP=%%a
set IP=%IP:~1%

echo ✅ Démarrage du serveur...
echo.
echo 📍 Accès au jeu :
echo.
echo    Sur cet ordinateur : http://localhost:5000
echo    Autres appareils : http://%IP%:5000
echo.
python app.py
pause
exit /b 0

:public
echo.
echo ================================================
echo   🌍 MODE PUBLIC (avec tunnel Serveo)
echo ================================================
echo.

REM Vérifier SSH
where ssh >nul 2>&1
if errorlevel 1 (
    echo ❌ SSH n'est pas installé
    echo 📦 Installez OpenSSH depuis les paramètres Windows
    echo    Paramètres → Applications → Fonctionnalités facultatives → OpenSSH Client
    pause
    exit /b 1
)

echo ✅ SSH détecté
echo.

REM Demander le sous-domaine
REM echo 📝 Choisissez un nom pour votre serveur
REM set /p subdomain="Nom du serveur (ex: mon-jeu) : "
REM if "%subdomain%"=="" set subdomain=smile-life
set subdomain=smile-life
echo.
echo 🚀 Lancement du serveur ET du tunnel...
echo.
echo 📍 Votre jeu sera accessible sur :
echo    https://%subdomain%.serveo.net
echo.
echo ⚠️  Partagez cette adresse avec vos amis !
echo.
timeout /t 2

REM Lancer le serveur Flask en arrière-plan
start /b cmd /c "python app.py"

REM Attendre que le serveur démarre
echo ⏳ Démarrage du serveur Flask...
timeout /t 2

REM Lancer le tunnel SSH
:tunnel_loop
echo 📡 Connexion au tunnel Serveo...
ssh -o ServerAliveInterval=60 -o ServerAliveCountMax=3 -R %subdomain%:80:127.0.0.1:5000 serveo.net

echo ⚠️ Connexion perdue. Reconnexion...
timeout /t 5 /nobreak
goto tunnel_loop