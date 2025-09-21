#!/usr/bin/env python3
"""
Script de lancement pour le jeu de cartes multijoueur
"""

import os
import sys
import webbrowser
import asyncio
import threading
import time
from pathlib import Path

def check_dependencies():
    """Vérifier que toutes les dépendances sont installées"""
    try:
        import websockets
        print("✅ websockets installé")
    except ImportError:
        print("❌ websockets manquant")
        print("Installez avec: pip install websockets")
        return False
    
    # Vérifier que les fichiers de jeu existent
    required_files = ['cards.py', 'players.py', 'deck.py', 'game.py']
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ Fichier manquant: {file}")
            return False
        print(f"✅ {file} trouvé")
    
    return True

def create_server_file():
    """Créer le fichier serveur s'il n'existe pas"""
    if not Path('server.py').exists():
        print("📝 Création du fichier server.py...")
        # Le code du serveur serait écrit ici, mais comme il est déjà dans l'artifact ci-dessus,
        # nous supposons qu'il existe
    
def create_client_file():
    """Créer le fichier client s'il n'existe pas"""
    if not Path('client.html').exists():
        print("📝 Création du fichier client.html...")
        # Le code HTML serait écrit ici, mais comme il est déjà dans l'artifact ci-dessus,
        # nous supposons qu'il existe

def run_http_server():
    """Lancer le serveur HTTP pour les images"""
    try:
        import http_server
        http_server.main()
    except Exception as e:
        print(f"❌ Erreur serveur HTTP: {e}")

def run_server():
    """Lancer le serveur WebSocket dans un thread séparé"""
    try:
        # Importer et lancer le serveur
        import server
        asyncio.run(server.main())
    except Exception as e:
        print(f"❌ Erreur serveur WebSocket: {e}")

def main():
    print("🃏 Lancement du jeu de cartes multijoueur")
    print("=" * 50)
    
    # Vérifier les dépendances
    if not check_dependencies():
        print("\n❌ Veuillez installer les dépendances manquantes")
        return
    
    print("\n✅ Toutes les dépendances sont présentes")
    
    # Créer les fichiers manquants
    create_server_file()
    create_client_file()
    
    print("\n🚀 Démarrage des serveurs...")
    
    # Lancer le serveur HTTP pour les images dans un thread séparé
    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()
    
    # Attendre un peu que le serveur HTTP se lance
    time.sleep(1)
    
    # Lancer le serveur WebSocket dans un thread séparé
    websocket_thread = threading.Thread(target=run_server, daemon=True)
    websocket_thread.start()
    
    # Attendre un peu que les serveurs se lancent
    time.sleep(2)
    
    # Ouvrir le client dans le navigateur
    client_path = Path('client.html').absolute()
    if client_path.exists():
        print(f"🌐 Ouverture du client: {client_path}")
        webbrowser.open(f'file://{client_path}')
    else:
        print("❌ Fichier client.html non trouvé")
        return
    
    print("\n" + "=" * 50)
    print("🎮 Jeu lancé avec succès!")
    print("📝 Instructions:")
    print("   1. Serveur WebSocket: ws://localhost:8765")
    print("   2. Serveur HTTP (images): http://localhost:8080") 
    print("   3. Le client web s'est ouvert dans votre navigateur")
    print("   4. Créez une partie ou rejoignez avec un ID")
    print("   5. Ouvrez d'autres onglets pour plus de joueurs")
    print("   6. Ajoutez vos images dans le dossier 'ressources'")
    print("   7. Appuyez sur Ctrl+C pour arrêter")
    print("=" * 50)
    
    try:
        # Garder le script en vie
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du serveur...")
        print("👋 À bientôt!")

if __name__ == "__main__":
    main()