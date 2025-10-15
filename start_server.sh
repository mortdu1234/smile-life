#!/bin/bash

echo "🚀 Démarrage du tunnel Serveo..."

# Configuration
LOCAL_PORT=5000
SUBDOMAIN="smile-life"  # Personnalisez ici

# Fonction pour démarrer le tunnel
start_tunnel() {
    echo "📡 Création du tunnel SSH..."
    ssh -o ServerAliveInterval=60 \
        -o ServerAliveCountMax=3 \
        -o ExitOnForwardFailure=yes \
        -R $SUBDOMAIN:80:localhost:$LOCAL_PORT \
        serveo.net
}

# Boucle de reconnexion automatique
while true; do
    start_tunnel
    echo "⚠️ Connexion perdue. Reconnexion dans 5 secondes..."
    sleep 5
done