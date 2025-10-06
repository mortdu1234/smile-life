#!/bin/bash

# Script d'installation automatique du Jeu de Cartes Smile
# Pour Linux Mint

echo "=================================================="
echo "  🎮 Installation du Jeu de Cartes Smile"
echo "=================================================="
echo ""

# Créer le dossier du projet
PROJECT_DIR="$HOME/smile-game-python"

if [ -d "$PROJECT_DIR" ]; then
    echo "⚠️  Le dossier $PROJECT_DIR existe déjà."
    read -p "Voulez-vous le supprimer et recommencer ? (o/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Oo]$ ]]; then
        rm -rf "$PROJECT_DIR"
        echo "✅ Dossier supprimé"
    else
        echo "❌ Installation annulée"
        exit 1
    fi
fi

echo "📁 Création du dossier du projet : $PROJECT_DIR"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Créer la structure
echo "📁 Création de la structure des dossiers..."
mkdir -p templates static

# Vérifier et installer Python
echo ""
echo "🔍 Vérification de Python..."
if ! command -v python3 &> /dev/null; then
    echo "📦 Installation de Python 3..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
fi
echo "✅ Python 3 : $(python3 --version)"

# Créer l'environnement virtuel
echo ""
echo "📦 Création de l'environnement virtuel..."
python3 -m venv venv
source venv/bin/activate

# Installer Flask
echo "📦 Installation de Flask..."
pip install flask

echo ""
echo "=================================================="
echo "  ✅ Installation terminée !"
echo "=================================================="
echo ""
echo "📝 Prochaines étapes :"
echo ""
echo "1. Créez le fichier app.py avec le code du serveur Flask"
echo "   Emplacement : $PROJECT_DIR/app.py"
echo ""
echo "2. Créez le fichier templates/index.html avec le code HTML"
echo "   Emplacement : $PROJECT_DIR/templates/index.html"
echo ""
echo "3. Rendez le script de lancement exécutable :"
echo "   chmod +x start.sh"
echo ""
echo "4. Lancez le jeu avec :"
echo "   ./start.sh"
echo ""
echo "   Ou manuellement :"
echo "   cd $PROJECT_DIR"
echo "   source venv/bin/activate"
echo "   python3 app.py"
echo ""
echo "=================================================="
echo ""

# Créer un script de lancement simple
cat > start.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python3 app.py
EOF

chmod +x start.sh

echo "💡 Un script de lancement a été créé : start.sh"
echo ""

# Ouvrir le dossier dans le gestionnaire de fichiers
if command -v xdg-open &> /dev/null; then
    read -p "Voulez-vous ouvrir le dossier du projet ? (O/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        xdg-open "$PROJECT_DIR"
    fi
fi

echo "🎉 Installation terminée avec succès !"