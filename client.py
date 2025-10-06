import socket
import threading
import json
from typing import Optional, Callable, Dict
from dataclasses import dataclass, asdict
import time

@dataclass
class Message:
    """Structure de message pour la communication client-serveur."""
    type: str
    donnees: dict
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
    
    def to_json(self) -> str:
        return json.dumps(asdict(self))
    
    @staticmethod
    def from_json(json_str: str) -> 'Message':
        data = json.loads(json_str)
        return Message(**data)


class ClientJeu:
    """Client pour se connecter au serveur de jeu Smiles."""
    
    def __init__(self, host: str = 'localhost', port: int = 5555):
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None
        self.connecte = False
        self.nom_joueur: Optional[str] = None
        
        # Thread d'écoute
        self.thread_ecoute: Optional[threading.Thread] = None
        
        # Callbacks pour gérer les différents types de messages
        self.callbacks: Dict[str, Callable] = {}
        
        # État du jeu
        self.etat_jeu: Optional[dict] = None
        self.joueurs_connectes: list = []
    
    def se_connecter(self, nom_joueur: str) -> bool:
        """Se connecte au serveur avec le nom du joueur."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connecte = True
            self.nom_joueur = nom_joueur
            
            # Démarrer le thread d'écoute
            self.thread_ecoute = threading.Thread(target=self._ecouter_serveur, daemon=True)
            self.thread_ecoute.start()
            
            # Envoyer la demande de connexion
            self.envoyer_message(Message('connexion', {'nom': nom_joueur}))
            
            print(f"[CLIENT] Connexion au serveur {self.host}:{self.port} en tant que {nom_joueur}")
            return True
        
        except Exception as e:
            print(f"[ERREUR] Impossible de se connecter: {e}")
            self.connecte = False
            return False
    
    def se_deconnecter(self):
        """Se déconnecte du serveur."""
        if self.connecte:
            self.envoyer_message(Message('deconnexion', {}))
            self.connecte = False
            if self.socket:
                self.socket.close()
            print("[CLIENT] Déconnecté du serveur")
    
    def _ecouter_serveur(self):
        """Thread qui écoute les messages du serveur."""
        buffer = ""
        
        while self.connecte:
            try:
                data = self.socket.recv(4096).decode('utf-8')
                if not data:
                    print("[CLIENT] Connexion perdue avec le serveur")
                    self.connecte = False
                    break
                
                buffer += data
                
                # Traiter tous les messages complets dans le buffer
                while '\n' not in buffer:
                    # Essayer de parser le message JSON
                    try:
                        message = Message.from_json(buffer)
                        self._traiter_message(message)
                        buffer = ""
                        break
                    except json.JSONDecodeError:
                        # Message incomplet, attendre plus de données
                        break
            
            except Exception as e:
                if self.connecte:
                    print(f"[ERREUR] Écoute serveur: {e}")
                break
    
    def _traiter_message(self, message: Message):
        """Traite un message reçu du serveur."""
        print(f"[CLIENT] Message reçu: {message.type}")
        
        if message.type == 'connexion_ok':
            self.joueurs_connectes = message.donnees.get('joueurs_connectes', [])
            print(f"[CLIENT] Connexion réussie ! Joueurs: {self.joueurs_connectes}")
        
        elif message.type == 'nouveau_joueur':
            self.joueurs_connectes = message.donnees.get('joueurs_connectes', [])
            nouveau = message.donnees.get('nom')
            print(f"[CLIENT] {nouveau} a rejoint la partie")
        
        elif message.type == 'joueur_parti':
            self.joueurs_connectes = message.donnees.get('joueurs_connectes', [])
            parti = message.donnees.get('nom')
            print(f"[CLIENT] {parti} a quitté la partie")
        
        elif message.type == 'joueur_pret':
            nom = message.donnees.get('nom')
            prets = message.donnees.get('prets', [])
            total = message.donnees.get('total', 0)
            print(f"[CLIENT] {nom} est prêt ({len(prets)}/{total})")
        
        elif message.type == 'etat_jeu':
            self.etat_jeu = message.donnees
            self._afficher_etat_jeu()
        
        elif message.type == 'erreur':
            erreur = message.donnees.get('message', 'Erreur inconnue')
            print(f"[ERREUR] {erreur}")
        
        # Appeler le callback personnalisé si défini
        if message.type in self.callbacks:
            self.callbacks[message.type](message.donnees)
    
    def _afficher_etat_jeu(self):
        """Affiche l'état actuel du jeu."""
        if not self.etat_jeu:
            return
        
        print("\n" + "="*50)
        print(f"TOUR {self.etat_jeu['tour']} - Joueur actuel: {self.etat_jeu['joueur_actuel']}")
        print(f"Cartes restantes dans la pioche: {self.etat_jeu['cartes_restantes']}")
        
        print("\n--- Votre main ---")
        for i, carte in enumerate(self.etat_jeu['votre_main']):
            print(f"{i}: {carte['nom']} ({carte['smiles']} smiles)")
        
        print("\n--- Vos cartes posées ---")
        posees = self.etat_jeu['vos_cartes_posees']
        if posees.get('metier'):
            print(f"Métier: {posees['metier']['nom']}")
        if posees.get('mariage'):
            print(f"Mariage: {posees['mariage']['nom']}")
        print(f"Flirts: {len(posees.get('flirts', []))}")
        print(f"Enfants: {len(posees.get('enfants', []))}")
        print(f"Études: {len(posees.get('etudes', []))}")
        print(f"Salaires disponibles: {len(posees.get('salaires_disponibles', []))}")
        
        print("\n--- Scores ---")
        for nom, score in self.etat_jeu['scores'].items():
            marqueur = " ← VOUS" if nom == self.nom_joueur else ""
            print(f"{nom}: {score} smiles{marqueur}")
        
        print("="*50 + "\n")
    
    def envoyer_message(self, message: Message):
        """Envoie un message au serveur."""
        if not self.connecte:
            print("[ERREUR] Non connecté au serveur")
            return False
        
        try:
            self.socket.send(message.to_json().encode('utf-8'))
            return True
        except Exception as e:
            print(f"[ERREUR] Envoi message: {e}")
            return False
    
    def enregistrer_callback(self, type_message: str, callback: Callable):
        """Enregistre un callback pour un type de message."""
        self.callbacks[type_message] = callback
    
    # Actions de jeu
    
    def marquer_pret(self):
        """Marque le joueur comme prêt à commencer."""
        return self.envoyer_message(Message('pret', {}))
    
    def piocher(self, source: str = 'pioche'):
        """Pioche une carte (source: 'pioche' ou 'defausse')."""
        return self.envoyer_message(Message('action', {
            'action': 'piocher',
            'source': source
        }))
    
    def poser_carte(self, index_carte: int):
        """Pose une carte de la main."""
        return self.envoyer_message(Message('action', {
            'action': 'poser_carte',
            'index_carte': index_carte
        }))
    
    def defausser_carte(self, index_carte: int):
        """Défausse une carte de la main."""
        return self.envoyer_message(Message('action', {
            'action': 'defausser',
            'index_carte': index_carte
        }))
    
    def jouer_malus(self, index_carte: int, nom_cible: str):
        """Joue un malus sur un adversaire."""
        return self.envoyer_message(Message('action', {
            'action': 'jouer_malus',
            'index_carte': index_carte,
            'cible': nom_cible
        }))
    
    def utiliser_carte_speciale(self, index_carte: int, **params):
        """Utilise une carte spéciale."""
        return self.envoyer_message(Message('action', {
            'action': 'utiliser_special',
            'index_carte': index_carte,
            **params
        }))


class InterfaceConsole:
    """Interface en ligne de commande pour le client."""
    
    def __init__(self, client: ClientJeu):
        self.client = client
        self.en_jeu = False
    
    def demarrer(self):
        """Démarre l'interface."""
        print("=== Client Jeu Smiles ===\n")
        
        # Menu principal
        while True:
            print("\n1. Se connecter à une partie")
            print("2. Quitter")
            
            choix = input("\nVotre choix: ").strip()
            
            if choix == '1':
                self.se_connecter_partie()
            elif choix == '2':
                print("Au revoir !")
                break
            else:
                print("Choix invalide")
    
    def se_connecter_partie(self):
        """Menu de connexion à une partie."""
        host = input("Adresse du serveur (localhost): ").strip() or 'localhost'
        port_str = input("Port (5555): ").strip() or '5555'
        
        try:
            port = int(port_str)
        except ValueError:
            print("Port invalide")
            return
        
        nom = input("Votre nom: ").strip()
        if not nom:
            print("Nom invalide")
            return
        
        # Créer et connecter le client
        self.client.host = host
        self.client.port = port
        
        if self.client.se_connecter(nom):
            time.sleep(0.5)  # Attendre la confirmation de connexion
            self.menu_salon()
        else:
            print("Échec de la connexion")
    
    def menu_salon(self):
        """Menu d'attente dans le salon."""
        print("\n=== Salon d'attente ===")
        
        while self.client.connecte and not self.en_jeu:
            print(f"\nJoueurs connectés: {', '.join(self.client.joueurs_connectes)}")
            print("\n1. Prêt à jouer")
            print("2. Rafraîchir")
            print("3. Quitter le salon")
            
            choix = input("\nVotre choix: ").strip()
            
            if choix == '1':
                self.client.marquer_pret()
                print("Vous êtes prêt ! En attente des autres joueurs...")
                # Attendre le début de la partie
                self.attendre_debut_partie()
                break
            elif choix == '2':
                continue
            elif choix == '3':
                self.client.se_deconnecter()
                break
    
    def attendre_debut_partie(self):
        """Attend que la partie démarre."""
        print("En attente du début de la partie...")
        
        # Enregistrer un callback pour le début de partie
        def debut_partie(donnees):
            self.en_jeu = True
            print("\n🎮 La partie commence !")
            self.menu_jeu()
        
        self.client.enregistrer_callback('etat_jeu', debut_partie)
        
        # Attendre passivement
        while self.client.connecte and not self.en_jeu:
            time.sleep(1)
    
    def menu_jeu(self):
        """Menu principal du jeu."""
        while self.client.connecte and self.en_jeu:
            if not self.client.etat_jeu:
                time.sleep(1)
                continue
            
            etat = self.client.etat_jeu
            c_est_mon_tour = etat['joueur_actuel'] == self.client.nom_joueur
            
            if not c_est_mon_tour:
                print(f"\nEn attente du tour de {etat['joueur_actuel']}...")
                time.sleep(2)
                continue
            
            if etat.get('tours_a_passer', 0) > 0:
                print(f"\nVous devez passer {etat['tours_a_passer']} tour(s)")
                input("Appuyez sur Entrée pour passer...")
                continue
            
            # C'est notre tour !
            print("\n" + "="*50)
            print("🎯 C'EST VOTRE TOUR !")
            print("="*50)
            
            self.afficher_menu_actions()
    
    def afficher_menu_actions(self):
        """Affiche le menu des actions possibles."""
        etat = self.client.etat_jeu
        
        print("\nQue voulez-vous faire ?")
        print("1. Piocher dans la pioche")
        print("2. Piocher dans la défausse")
        print("3. Poser une carte")
        print("4. Défausser une carte")
        print("5. Jouer un malus sur un adversaire")
        print("6. Afficher l'état du jeu")
        print("7. Afficher ma main")
        print("8. Passer mon tour")
        
        choix = input("\nVotre choix: ").strip()
        
        if choix == '1':
            self.action_piocher('pioche')
        elif choix == '2':
            self.action_piocher('defausse')
        elif choix == '3':
            self.action_poser_carte()
        elif choix == '4':
            self.action_defausser()
        elif choix == '5':
            self.action_jouer_malus()
        elif choix == '6':
            self.client._afficher_etat_jeu()
        elif choix == '7':
            self.afficher_main()
        elif choix == '8':
            print("Vous passez votre tour")
        else:
            print("Choix invalide")
    
    def afficher_main(self):
        """Affiche les cartes en main."""
        print("\n--- Votre main ---")
        for i, carte in enumerate(self.client.etat_jeu['votre_main']):
            print(f"{i}: {carte['nom']} - {carte['type']} ({carte['smiles']} smiles)")
    
    def action_piocher(self, source: str):
        """Action: piocher une carte."""
        if self.client.piocher(source):
            print(f"Vous avez pioché dans la {source}")
            time.sleep(1)
    
    def action_poser_carte(self):
        """Action: poser une carte."""
        self.afficher_main()
        
        try:
            index = int(input("\nNuméro de la carte à poser (-1 pour annuler): "))
            if index == -1:
                return
            
            if 0 <= index < len(self.client.etat_jeu['votre_main']):
                if self.client.poser_carte(index):
                    print("Carte posée !")
                    time.sleep(1)
            else:
                print("Index invalide")
        except ValueError:
            print("Entrée invalide")
    
    def action_defausser(self):
        """Action: défausser une carte."""
        self.afficher_main()
        
        try:
            index = int(input("\nNuméro de la carte à défausser (-1 pour annuler): "))
            if index == -1:
                return
            
            if 0 <= index < len(self.client.etat_jeu['votre_main']):
                if self.client.defausser_carte(index):
                    print("Carte défaussée !")
                    time.sleep(1)
            else:
                print("Index invalide")
        except ValueError:
            print("Entrée invalide")
    
    def action_jouer_malus(self):
        """Action: jouer un malus sur un adversaire."""
        self.afficher_main()
        
        # Afficher les cartes malus
        cartes_malus = []
        for i, carte in enumerate(self.client.etat_jeu['votre_main']):
            if carte['type'] == 'malus':
                cartes_malus.append((i, carte))
        
        if not cartes_malus:
            print("Vous n'avez pas de carte malus")
            return
        
        print("\nVos cartes malus:")
        for i, carte in cartes_malus:
            print(f"{i}: {carte['nom']}")
        
        try:
            index = int(input("\nNuméro de la carte malus (-1 pour annuler): "))
            if index == -1:
                return
            
            # Afficher les adversaires
            print("\nAdversaires:")
            adversaires = self.client.etat_jeu.get('adversaires', [])
            for i, adv in enumerate(adversaires):
                print(f"{i}: {adv['nom']} ({adv['smiles']} smiles)")
            
            cible_index = int(input("\nNuméro de l'adversaire cible (-1 pour annuler): "))
            if cible_index == -1:
                return
            
            if 0 <= cible_index < len(adversaires):
                cible_nom = adversaires[cible_index]['nom']
                if self.client.jouer_malus(index, cible_nom):
                    print(f"Malus joué sur {cible_nom} !")
                    time.sleep(1)
            else:
                print("Index invalide")
        
        except ValueError:
            print("Entrée invalide")


def main():
    """Point d'entrée du client."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Client du jeu Smiles')
    parser.add_argument('--host', default='localhost', help='Adresse du serveur')
    parser.add_argument('--port', type=int, default=5555, help='Port du serveur')
    parser.add_argument('--nom', help='Nom du joueur')
    parser.add_argument('--auto', action='store_true', help='Connexion automatique')
    
    args = parser.parse_args()
    
    client = ClientJeu(host=args.host, port=args.port)
    
    if args.auto and args.nom:
        # Connexion automatique
        if client.se_connecter(args.nom):
            print("Connecté ! En attente...")
            # Garder le client actif
            try:
                while client.connecte:
                    time.sleep(1)
            except KeyboardInterrupt:
                client.se_deconnecter()
    else:
        # Interface console interactive
        interface = InterfaceConsole(client)
        interface.demarrer()


if __name__ == "__main__":
    main()