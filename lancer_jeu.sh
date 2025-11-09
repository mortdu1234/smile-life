#!/bin/bash
# Fonction pour lancement en mode privé
launch_private() {
    clear
    echo -e "${GREEN}========================================"
    echo "  MODE PRIVÉ - Localhost uniquement"
    echo -e "========================================${NC}"
    echo ""
    echo "Lancement de l'application Flask..."
    echo ""
    
    # Déterminer quel émulateur de terminal utiliser
    if command -v gnome-terminal &> /dev/null; then
        gnome-terminal -- bash -c "echo -e '\033[0;32m========================================'; echo '   APPLICATION FLASK - MODE PRIVÉ'; echo -e '========================================\033[0m'; echo ''; echo 'URL locale : http://127.0.0.1:5000'; echo ''; python3 app.py; echo ''; echo 'Appuyez sur une touche pour fermer...'; read" &
    elif command -v xterm &> /dev/null; then
        xterm -hold -e "echo '========================================'; echo '   APPLICATION FLASK - MODE PRIVÉ'; echo '========================================'; echo ''; echo 'URL locale : http://127.0.0.1:5000'; echo ''; python3 app.py" &
    elif command -v konsole &> /dev/null; then
        konsole --hold -e bash -c "echo '========================================'; echo '   APPLICATION FLASK - MODE PRIVÉ'; echo '========================================'; echo ''; echo 'URL locale : http://127.0.0.1:5000'; echo ''; python3 app.py" &
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        osascript -e 'tell app "Terminal" to do script "cd \"'"$(pwd)"'\" && echo \"========================================\" && echo \"   APPLICATION FLASK - MODE PRIVÉ\" && echo \"========================================\" && echo \"\" && echo \"URL locale : http://127.0.0.1:5000\" && echo \"\" && python3 app.py"' &
    else
        echo -e "${YELLOW}Lancement de Flask en arrière-plan...${NC}"
        python3 app.py &
    fi
    
    echo ""
    echo -e "${GREEN}========================================"
    echo "Application lancée en mode PRIVÉ"
    echo "URL : http://127.0.0.1:5000"
    echo -e "========================================${NC}"
}

# Fonction pour lancement en mode public
launch_public() {
    clear
    echo -e "${GREEN}========================================"
    echo "  MODE PUBLIC - Cloudflare Tunnel"
    echo -e "========================================${NC}"
    echo ""
    
    # Vérifier si cloudflared est installé
    if ! command -v cloudflared &> /dev/null; then
        echo -e "${RED}[ERREUR] cloudflared n'est pas installé${NC}"
        echo "Installation:"
        echo "  macOS: brew install cloudflare/cloudflare/cloudflared"
        echo "  Linux: https://github.com/cloudflare/cloudflared/releases"
        exit 1
    fi
    
    # Fichier log temporaire
    FLASK_LOG=$(mktemp)
    
    # Fonction pour nettoyer les processus à la sortie
    cleanup() {
        echo ""
        echo -e "${YELLOW}Arrêt du tunnel Cloudflare...${NC}"
        echo -e "${YELLOW}FERMEZ MANUELLEMENT le terminal Flask si nécessaire.${NC}"
        rm -f "$FLASK_LOG"
        exit 0
    }
    
    trap cleanup SIGINT SIGTERM EXIT
    
    echo -e "${BLUE}[1/2]${NC} Démarrage de l'application Flask dans un terminal séparé..."
    
    # Déterminer quel émulateur de terminal utiliser
    if command -v gnome-terminal &> /dev/null; then
        gnome-terminal -- bash -c "echo -e '\033[0;32m========================================'; echo '   APPLICATION FLASK - MODE PUBLIC'; echo -e '========================================\033[0m'; echo ''; python3 app.py; echo ''; echo 'Appuyez sur une touche pour fermer...'; read" &
    elif command -v xterm &> /dev/null; then
        xterm -hold -e "echo '========================================'; echo '   APPLICATION FLASK - MODE PUBLIC'; echo '========================================'; echo ''; python3 app.py" &
    elif command -v konsole &> /dev/null; then
        konsole --hold -e bash -c "echo '========================================'; echo '   APPLICATION FLASK - MODE PUBLIC'; echo '========================================'; echo ''; python3 app.py" &
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        osascript -e 'tell app "Terminal" to do script "cd \"'"$(pwd)"'\" && echo \"========================================\" && echo \"   APPLICATION FLASK - MODE PUBLIC\" && echo \"========================================\" && echo \"\" && python3 app.py"' &
    else
        echo -e "${RED}[ERREUR] Impossible de trouver un émulateur de terminal${NC}"
        echo "Lancement de Flask en arrière-plan..."
        python3 app.py &
        FLASK_PID=$!
    fi
    
    # Attendre que Flask démarre
    sleep 3
    
    echo -e "${BLUE}[2/2]${NC} Création du tunnel Cloudflare..."
    echo ""
    echo -e "${GREEN}========================================"
    echo "  VOTRE URL PUBLIQUE APPARAITRA ICI :"
    echo -e "========================================${NC}"
    echo ""
    
    # Lancer cloudflared
    cloudflared tunnel --url http://localhost:5000
}

# Couleurs pour l'affichage
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================"
echo "  Lancement Flask + Cloudflare Tunnel"
echo -e "========================================${NC}"
echo ""

# Vérifier si app.py existe
if [ ! -f "app.py" ]; then
    echo -e "${RED}[ERREUR] Le fichier app.py n'existe pas dans ce dossier${NC}"
    exit 1
fi

# Menu de choix
while true; do
    echo "Choisissez le mode de lancement :"
    echo ""
    echo -e "${CYAN}[1]${NC} Mode PRIVÉ (localhost uniquement)"
    echo -e "${CYAN}[2]${NC} Mode PUBLIC (accessible depuis Internet via Cloudflare)"
    echo -e "${CYAN}[Q]${NC} Quitter"
    echo ""
    read -p "Votre choix (1/2/Q) : " choice
    
    case $choice in
        1)
            launch_private
            exit 0
            ;;
        2)
            launch_public
            exit 0
            ;;
        q|Q)
            echo "Au revoir !"
            exit 0
            ;;
        *)
            echo -e "${RED}Choix invalide, veuillez réessayer.${NC}"
            echo ""
            ;;
    esac
done

