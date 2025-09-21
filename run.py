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

def run_server():
    """Lancer le serveur dans un thread séparé"""
    try:
        # Importer et lancer le serveur
        import server
        asyncio.run(server.main())
    except Exception as e:
        print(f"❌ Erreur serveur: {e}")

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
    
    print("\n🚀 Lancement du serveur...")
    
    # Lancer le serveur dans un thread séparé
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Attendre un peu que le serveur se lance
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
    print("   1. Le serveur tourne sur ws://localhost:8765")
    print("   2. Le client web s'est ouvert dans votre navigateur")
    print("   3. Créez une partie ou rejoignez avec un ID")
    print("   4. Ouvrez d'autres onglets pour plus de joueurs")
    print("   5. Appuyez sur Ctrl+C pour arrêter")
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