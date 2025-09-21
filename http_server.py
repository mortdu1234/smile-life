#!/usr/bin/env python3
"""
Serveur HTTP simple pour servir les fichiers statiques (images des cartes)
"""

import http.server
import socketserver
import os
import threading
import webbrowser
import time
from pathlib import Path

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Handler HTTP avec support CORS pour éviter les problèmes d'accès aux images"""
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_GET(self):
        """Gérer les requêtes GET avec fallback pour les images manquantes"""
        # Si le fichier demandé n'existe pas et que c'est une image
        if self.path.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg')):
            file_path = self.path.lstrip('/')
            if not os.path.exists(file_path):
                # Servir une image par défaut ou une réponse 404 personnalisée
                self.send_response(404)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(f"Image not found: {file_path}".encode())
                return
        
        # Comportement normal pour les autres fichiers
        super().do_GET()

def create_default_images():
    """Créer des images par défaut si le dossier ressources n'existe pas"""
    base_dirs = [
        'ressources/special_cards',
        'ressources/attack_cards', 
        'ressources/aquisition_cards/trip',
        'ressources/aquisition_cards/houses',
        'ressources/aquisition_cards/animals',
        'ressources/personnal_life/flirts',
        'ressources/personnal_life/mariages',
        'ressources/personnal_life/childs',
        'ressources/professionnal_life/StudyCards',
        'ressources/professionnal_life/JobCards',
        'ressources/professionnal_life/SalaryCards'
    ]
    
    # Créer les dossiers s'ils n'existent pas
    for dir_path in base_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    # Créer un fichier README avec des instructions
    readme_content = """# Images des cartes

Ce dossier contient les images des cartes du jeu.

## Structure des dossiers :
- ressources/special_cards/ : Cartes spéciales
- ressources/attack_cards/ : Cartes d'attaque
- ressources/aquisition_cards/trip/ : Cartes de voyage
- ressources/aquisition_cards/houses/ : Cartes de maisons
- ressources/aquisition_cards/animals/ : Cartes d'animaux
- ressources/personnal_life/flirts/ : Cartes de flirt
- ressources/personnal_life/mariages/ : Cartes de mariage
- ressources/personnal_life/childs/ : Cartes d'enfants
- ressources/professionnal_life/StudyCards/ : Cartes d'études
- ressources/professionnal_life/JobCards/ : Cartes de métiers
- ressources/professionnal_life/SalaryCards/ : Cartes de salaire

## Format des images :
- Format recommandé : PNG ou JPG
- Dimensions recommandées : 200x280 pixels (ratio carte standard)
- Nommage : selon les noms utilisés dans votre code Python

## Images manquantes :
Si une image est manquante, le jeu affichera un placeholder avec l'icône 🃏
"""
    
    with open('ressources/README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)

def start_http_server(port=8080):
    """Démarrer le serveur HTTP"""
    try:
        # Créer les dossiers par défaut si nécessaire
        create_default_images()
        
        # Démarrer le serveur
        with socketserver.TCPServer(("", port), CORSHTTPRequestHandler) as httpd:
            print(f"🌐 Serveur HTTP démarré sur http://localhost:{port}")
            print(f"📁 Servant les fichiers depuis : {os.getcwd()}")
            httpd.serve_forever()
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"⚠️ Le port {port} est déjà utilisé")
            # Essayer le port suivant
            start_http_server(port + 1)
        else:
            raise

def main():
    """Fonction principale pour lancer le serveur HTTP"""
    print("🖼️ Serveur d'images pour le jeu de cartes")
    print("=" * 50)
    
    # Vérifier si le dossier ressources existe
    if not os.path.exists('ressources'):
        print("📁 Création du dossier ressources...")
        create_default_images()
        print("✅ Dossiers créés. Ajoutez vos images dans le dossier 'ressources'")
    
    print("\n🚀 Démarrage du serveur HTTP...")
    start_http_server(8080)

if __name__ == "__main__":
    main()