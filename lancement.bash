#!/bin/bash

# Script de lancement du Jeu de Cartes Smile - Mode Multijoueur
# Pour Linux Mint

echo "=================================================="
echo "  🎮 Jeu de Cartes Smile - Lancement Multijoueur"
echo "=================================================="
echo ""

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé."
    echo "📦 Installation de Python 3..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
fi

echo "✅ Python 3 détecté : $(python3 --version)"

# Vérifier si l'environnement virtuel existe
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv
    
    echo "📦 Installation des dépendances..."
    source venv/bin/activate
    pip install flask flask-socketio python-socketio eventlet
    echo "✅ Dépendances installées"
else
    echo "✅ Environnement virtuel détecté"
    source venv/bin/activate
fi

# Vérifier si Flask-SocketIO est installé
if ! python3 -c "import flask_socketio" &> /dev/null; then
    echo "📦 Installation de Flask-SocketIO..."
    pip install flask-socketio python-socketio eventlet
fi

# Vérifier si les fichiers nécessaires existent
if [ ! -f "app.py" ]; then
    echo ""
    echo "❌ Erreur : Le fichier app.py est manquant !"
    echo "📝 Veuillez créer le fichier app.py avec le code du serveur."
    exit 1
fi

if [ ! -d "templates" ] || [ ! -f "templates/index.html" ]; then
    echo ""
    echo "❌ Erreur : Le fichier templates/index.html est manquant !"
    echo "📝 Veuillez créer le dossier templates et le fichier index.html."
    exit 1
fi

# Obtenir l'adresse IP locale
IP=$(hostname -I | awk '{print $1}')

echo ""
echo "=================================================="
echo "  🚀 Démarrage du serveur multijoueur..."
echo "=================================================="
echo ""
echo "📍 Le jeu sera accessible à :"
echo ""
echo "   🏠 Sur cet ordinateur :"
echo "      http://localhost:5000"
echo ""
echo "   🌐 Autres appareils (même réseau) :"
echo "      http://$IP:5000"
echo ""
echo "📝 Instructions :"
echo "   1. L'hôte crée une partie et obtient un CODE"
echo "   2. Les autres joueurs rejoignent avec ce CODE"
echo "   3. L'hôte démarre la partie quand tout le monde est prêt"
echo ""
echo "⏹️  Pour arrêter le serveur, appuyez sur Ctrl+C"
echo ""
echo "=================================================="
echo ""

# Lancer le serveur Flask avec SocketIO
python3 app.py