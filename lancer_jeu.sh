#!/bin/bash

# Définir l'encodage UTF-8
export LANG=fr_FR.UTF-8

echo "================================================"
echo "  🎮 JEU DE CARTES SMILE - LANCEUR COMPLET"
echo "================================================"
echo ""

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python n'est pas installé"
    read -p "Appuyez sur Entrée pour quitter..."
    exit 1
fi

# Créer l'environnement virtuel si nécessaire
if [ ! -d ".venv" ]; then
    echo "📦 Installation initiale..."
    python3 -m .venv .venv
    source .venv/bin/activate
    pip install flask flask-socketio python-socketio eventlet
else
    source .venv/bin/activate
fi

echo ""
echo "📋 CHOIX DU MODE :"
echo ""
echo "  [1] 🏠 Jeu LOCAL (même réseau WiFi uniquement)"
echo "  [2] 🌍 Jeu PUBLIC (accessible depuis Internet avec Serveo)"
echo ""
read -p "Votre choix (1 ou 2) : " choice

case $choice in
    1)
        echo ""
        echo "================================================"
        echo "  🏠 MODE LOCAL"
        echo "================================================"
        echo ""
        
        # Obtenir l'adresse IP locale
        if command -v ip &> /dev/null; then
            IP=$(ip route get 1 | awk '{print $7; exit}')
        elif command -v ifconfig &> /dev/null; then
            IP=$(ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1' | head -n1)
        else
            IP="[IP non détectée]"
        fi
        
        echo "✅ Démarrage du serveur..."
        echo ""
        echo "📍 Accès au jeu :"
        echo ""
        echo "   Sur cet ordinateur : http://localhost:5000"
        echo "   Autres appareils : http://$IP:5000"
        echo ""
        python3 app.py
        ;;
        
    2)
        echo ""
        echo "================================================"
        echo "  🌍 MODE PUBLIC (avec tunnel Serveo)"
        echo "================================================"
        echo ""
        
        # Vérifier SSH
        if ! command -v ssh &> /dev/null; then
            echo "❌ SSH n'est pas installé"
            echo "📦 Installez OpenSSH avec : sudo apt install openssh-client"
            read -p "Appuyez sur Entrée pour quitter..."
            exit 1
        fi
        
        echo "✅ SSH détecté"
        echo ""
        
        # Définir le sous-domaine
        subdomain="smile-life"
        
        echo "🚀 Lancement du serveur ET du tunnel..."
        echo ""
        echo "📍 Votre jeu sera accessible sur :"
        echo "   https://$subdomain.serveo.net"
        echo ""
        echo "⚠️  Partagez cette adresse avec vos amis !"
        echo ""
        sleep 2
        
        # Lancer le serveur Flask en arrière-plan
        python3 app.py &
        SERVER_PID=$!
        
        # Attendre que le serveur démarre
        echo "⏳ Démarrage du serveur Flask..."
        sleep 3
        
        # Fonction de nettoyage
        cleanup() {
            echo ""
            echo "🛑 Arrêt du serveur..."
            kill $SERVER_PID 2>/dev/null
            exit 0
        }
        
        # Intercepter Ctrl+C
        trap cleanup INT TERM
        
        # Lancer le tunnel SSH avec reconnexion automatique
        while true; do
            echo "📡 Connexion au tunnel Serveo..."
            ssh -o ServerAliveInterval=60 -o ServerAliveCountMax=3 -R $subdomain:80:127.0.0.1:5000 serveo.net
            
            echo "⚠️ Connexion perdue. Reconnexion dans 5 secondes..."
            sleep 5
        done
        ;;
        
    *)
        echo "Choix invalide"
        read -p "Appuyez sur Entrée pour quitter..."
        exit 1
        ;;
esac