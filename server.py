import socket
import threading
import json
import pickle
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import time

# Import des classes du jeu
from code import Jeu, Joueur, Carte, Plateau, FabriqueCartes, Pioche

@dataclass
class Message:
    """Structure de message pour la communication client-serveur."""
    type: str  # 'connexion', 'action', 'etat', 'erreur', 'fin_partie'
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


class ClientHandler(threading.Thread):
    """Gère la connexion d'un client individuel."""
    
    def __init__(self, client_socket: socket.socket, address: tuple, server: 'ServeurJeu'):
        super().__init__()
        self.socket = client_socket
        self.address = address
        self.server = server
        self.nom_joueur: Optional[str] = None
        self.actif = True
    
    def run(self):
        """Boucle principale de gestion du client."""
        print(f"[CONNEXION] Nouveau client depuis {self.address}")
        
        try:
            while self.actif:
                # Réception des données
                data = self.socket.recv(4096)
                if not data:
                    break
                
                message = Message.from_json(data.decode('utf-8'))
                self.traiter_message(message)
        
        except Exception as e:
            print(f"[ERREUR] Client {self.address}: {e}")
        
        finally:
            self.deconnecter()
    
    def traiter_message(self, message: Message):
        """Traite les messages reçus du client."""
        if message.type == 'connexion':
            self.gerer_connexion(message.donnees)
        
        elif message.type == 'action':
            self.gerer_action(message.donnees)
        
        elif message.type == 'pret':
            self.server.joueur_pret(self.nom_joueur)
        
        elif message.type == 'deconnexion':
            self.actif = False
    
    def gerer_connexion(self, donnees: dict):
        """Gère la connexion d'un nouveau joueur."""
        nom = donnees.get('nom')
        
        if not nom:
            self.envoyer_message(Message('erreur', {'message': 'Nom invalide'}))
            return
        
        if self.server.ajouter_joueur(nom, self):
            self.nom_joueur = nom
            self.envoyer_message(Message('connexion_ok', {
                'nom': nom,
                'joueurs_connectes': self.server.obtenir_liste_joueurs()
            }))
            
            # Notifier tous les autres joueurs
            self.server.diffuser_message(Message('nouveau_joueur', {
                'nom': nom,
                'joueurs_connectes': self.server.obtenir_liste_joueurs()
            }), excluant=self)
        else:
            self.envoyer_message(Message('erreur', {
                'message': 'Nom déjà pris ou partie pleine'
            }))
    
    def gerer_action(self, donnees: dict):
        """Gère une action de jeu du joueur."""
        action = donnees.get('action')
        
        if action == 'piocher':
            self.server.action_piocher(self.nom_joueur, donnees)
        
        elif action == 'poser_carte':
            self.server.action_poser_carte(self.nom_joueur, donnees)
        
        elif action == 'defausser':
            self.server.action_defausser(self.nom_joueur, donnees)
        
        elif action == 'jouer_malus':
            self.server.action_jouer_malus(self.nom_joueur, donnees)
        
        elif action == 'utiliser_special':
            self.server.action_utiliser_special(self.nom_joueur, donnees)
    
    def envoyer_message(self, message: Message):
        """Envoie un message au client."""
        try:
            self.socket.send(message.to_json().encode('utf-8'))
        except Exception as e:
            print(f"[ERREUR] Envoi message à {self.nom_joueur}: {e}")
            self.actif = False
    
    def deconnecter(self):
        """Déconnecte le client."""
        print(f"[DECONNEXION] {self.nom_joueur or self.address}")
        self.socket.close()
        if self.nom_joueur:
            self.server.retirer_joueur(self.nom_joueur)


class ServeurJeu:
    """Serveur principal du jeu Smiles."""
    
    def __init__(self, host: str = '0.0.0.0', port: int = 5555, max_joueurs: int = 5):
        self.host = host
        self.port = port
        self.max_joueurs = max_joueurs
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        self.clients: Dict[str, ClientHandler] = {}
        self.joueurs_prets: set = set()
        self.jeu: Optional[Jeu] = None
        self.partie_en_cours = False
        self.verrou = threading.Lock()
    
    def demarrer(self):
        """Démarre le serveur."""
        self.socket.bind((self.host, self.port))
        self.socket.listen()
        print(f"[SERVEUR] Démarré sur {self.host}:{self.port}")
        print(f"[SERVEUR] En attente de joueurs (max: {self.max_joueurs})...")
        
        try:
            while True:
                client_socket, address = self.socket.accept()
                
                if len(self.clients) >= self.max_joueurs:
                    # Partie pleine
                    msg = Message('erreur', {'message': 'Partie pleine'})
                    client_socket.send(msg.to_json().encode('utf-8'))
                    client_socket.close()
                    continue
                
                # Créer un handler pour ce client
                handler = ClientHandler(client_socket, address, self)
                handler.start()
        
        except KeyboardInterrupt:
            print("\n[SERVEUR] Arrêt du serveur...")
        
        finally:
            self.arreter()
    
    def arreter(self):
        """Arrête le serveur et déconnecte tous les clients."""
        for client in list(self.clients.values()):
            client.actif = False
            client.socket.close()
        self.socket.close()
        print("[SERVEUR] Arrêté")
    
    def ajouter_joueur(self, nom: str, handler: ClientHandler) -> bool:
        """Ajoute un joueur à la partie."""
        with self.verrou:
            if nom in self.clients or len(self.clients) >= self.max_joueurs:
                return False
            
            self.clients[nom] = handler
            print(f"[JOUEUR] {nom} a rejoint la partie ({len(self.clients)}/{self.max_joueurs})")
            return True
    
    def retirer_joueur(self, nom: str):
        """Retire un joueur de la partie."""
        with self.verrou:
            if nom in self.clients:
                del self.clients[nom]
                self.joueurs_prets.discard(nom)
                
                # Notifier les autres joueurs
                self.diffuser_message(Message('joueur_parti', {
                    'nom': nom,
                    'joueurs_connectes': self.obtenir_liste_joueurs()
                }))
                
                print(f"[JOUEUR] {nom} a quitté la partie")
    
    def obtenir_liste_joueurs(self) -> List[str]:
        """Retourne la liste des noms de joueurs connectés."""
        return list(self.clients.keys())
    
    def joueur_pret(self, nom: str):
        """Marque un joueur comme prêt."""
        self.joueurs_prets.add(nom)
        print(f"[PRET] {nom} est prêt ({len(self.joueurs_prets)}/{len(self.clients)})")
        
        # Notifier tous les joueurs
        self.diffuser_message(Message('joueur_pret', {
            'nom': nom,
            'prets': list(self.joueurs_prets),
            'total': len(self.clients)
        }))
        
        # Si tous les joueurs sont prêts et qu'il y en a au moins 2
        if len(self.joueurs_prets) == len(self.clients) >= 2:
            self.initialiser_partie()
    
    def initialiser_partie(self):
        """Initialise et démarre une nouvelle partie."""
        print("[PARTIE] Initialisation de la partie...")
        
        with self.verrou:
            noms_joueurs = list(self.clients.keys())
            self.jeu = Jeu(noms_joueurs)
            self.jeu.demarrer()
            self.partie_en_cours = True
        
        # Envoyer l'état initial à tous les joueurs
        self.diffuser_etat_jeu()
        
        print("[PARTIE] Partie démarrée !")
    
    def diffuser_message(self, message: Message, excluant: Optional[ClientHandler] = None):
        """Diffuse un message à tous les clients (sauf celui exclu)."""
        for client in self.clients.values():
            if client != excluant and client.actif:
                client.envoyer_message(message)
    
    def diffuser_etat_jeu(self):
        """Envoie l'état actuel du jeu à tous les joueurs."""
        if not self.jeu:
            return
        
        plateau = self.jeu.plateau
        joueur_actuel = plateau.joueur_actuel()
        
        # Préparer l'état général du jeu
        etat_general = {
            'tour': plateau.tour_actuel,
            'joueur_actuel': joueur_actuel.nom,
            'pioche_vide': plateau.pioche.est_vide(),
            'cartes_restantes': len(plateau.pioche.cartes),
            'defausse_visible': self.serialiser_carte(plateau.pioche.voir_defausse()) if plateau.pioche.voir_defausse() else None,
            'scores': {j.nom: j.calculer_smiles() for j in plateau.joueurs}
        }
        
        # Envoyer un état personnalisé à chaque joueur
        for joueur in plateau.joueurs:
            client = self.clients.get(joueur.nom)
            if client and client.actif:
                etat_perso = {
                    **etat_general,
                    'votre_main': [self.serialiser_carte(c) for c in joueur.main],
                    'vos_cartes_posees': self.serialiser_cartes_posees(joueur),
                    'peut_jouer': joueur.peut_jouer(),
                    'tours_a_passer': joueur.tours_a_passer,
                    'adversaires': self.serialiser_adversaires(joueur, plateau.joueurs)
                }
                
                client.envoyer_message(Message('etat_jeu', etat_perso))
    
    def serialiser_carte(self, carte: Carte) -> dict:
        """Sérialise une carte en dictionnaire."""
        return {
            'nom': carte.nom,
            'type': carte.type_carte.value,
            'smiles': carte.smiles,
            'image': str(carte.chemin_image) if carte.chemin_image else None
        }
    
    def serialiser_cartes_posees(self, joueur: Joueur) -> dict:
        """Sérialise toutes les cartes posées d'un joueur."""
        return {
            'enfants': [self.serialiser_carte(c) for c in joueur.enfants],
            'flirts': [self.serialiser_carte(c) for c in joueur.flirts],
            'etudes': [self.serialiser_carte(c) for c in joueur.etudes],
            'animaux': [self.serialiser_carte(c) for c in joueur.animaux],
            'acquisitions': [self.serialiser_carte(c) for c in joueur.acquisitions],
            'salaires_disponibles': [self.serialiser_carte(c) for c in joueur.salaires_disponibles],
            'salaires_bloques': [self.serialiser_carte(c) for c in joueur.salaires_bloques],
            'mariage': self.serialiser_carte(joueur.carte_mariage) if joueur.carte_mariage else None,
            'metier': self.serialiser_carte(joueur.metier) if joueur.metier else None,
            'marie': joueur.marie,
            'adultere': joueur.adultere
        }
    
    def serialiser_adversaires(self, joueur_actuel: Joueur, tous_joueurs: List[Joueur]) -> list:
        """Sérialise les informations visibles des adversaires."""
        adversaires = []
        for joueur in tous_joueurs:
            if joueur != joueur_actuel:
                adversaires.append({
                    'nom': joueur.nom,
                    'nombre_cartes_main': len(joueur.main),
                    'cartes_posees': self.serialiser_cartes_posees(joueur),
                    'smiles': joueur.calculer_smiles()
                })
        return adversaires
    
    # Actions de jeu
    
    def action_piocher(self, nom_joueur: str, donnees: dict):
        """Gère l'action de piocher."""
        if not self.verifier_tour(nom_joueur):
            return
        
        source = donnees.get('source', 'pioche')  # 'pioche' ou 'defausse'
        
        joueur = self.obtenir_joueur(nom_joueur)
        if not joueur:
            return
        
        if source == 'defausse':
            carte = self.jeu.plateau.pioche.voir_defausse()
            if carte:
                self.jeu.plateau.pioche.defausse.pop()
                joueur.piocher(carte)
        else:
            carte = self.jeu.plateau.pioche.piocher_carte()
            if carte:
                joueur.piocher(carte)
        
        self.diffuser_etat_jeu()
    
    def action_poser_carte(self, nom_joueur: str, donnees: dict):
        """Gère l'action de poser une carte."""
        if not self.verifier_tour(nom_joueur):
            return
        
        joueur = self.obtenir_joueur(nom_joueur)
        if not joueur:
            return
        
        index_carte = donnees.get('index_carte')
        if index_carte is None or index_carte >= len(joueur.main):
            return
        
        carte = joueur.main[index_carte]
        
        if carte.peut_etre_posee(joueur):
            joueur.main.pop(index_carte)
            carte.effet(joueur, self.jeu.plateau)
            self.diffuser_etat_jeu()
            
            # Passer au joueur suivant
            self.jeu.plateau.joueur_suivant()
            self.diffuser_etat_jeu()
        else:
            client = self.clients.get(nom_joueur)
            if client:
                client.envoyer_message(Message('erreur', {
                    'message': 'Vous ne pouvez pas poser cette carte'
                }))
    
    def action_defausser(self, nom_joueur: str, donnees: dict):
        """Gère l'action de défausser une carte."""
        if not self.verifier_tour(nom_joueur):
            return
        
        joueur = self.obtenir_joueur(nom_joueur)
        if not joueur:
            return
        
        index_carte = donnees.get('index_carte')
        if index_carte is None or index_carte >= len(joueur.main):
            return
        
        carte = joueur.main.pop(index_carte)
        self.jeu.plateau.pioche.defausser(carte)
        
        # Passer au joueur suivant
        self.jeu.plateau.joueur_suivant()
        self.diffuser_etat_jeu()
    
    def action_jouer_malus(self, nom_joueur: str, donnees: dict):
        """Gère l'action de jouer un malus sur un adversaire."""
        if not self.verifier_tour(nom_joueur):
            return
        
        joueur = self.obtenir_joueur(nom_joueur)
        cible_nom = donnees.get('cible')
        cible = self.obtenir_joueur(cible_nom)
        index_carte = donnees.get('index_carte')
        
        if not joueur or not cible or index_carte is None:
            return
        
        if index_carte >= len(joueur.main):
            return
        
        carte = joueur.main[index_carte]
        if carte.type_carte.value == 'malus':
            joueur.main.pop(index_carte)
            carte.effet(cible, self.jeu.plateau)
            self.diffuser_etat_jeu()
    
    def action_utiliser_special(self, nom_joueur: str, donnees: dict):
        """Gère l'utilisation d'une carte spéciale."""
        # À implémenter selon les cartes spéciales
        pass
    
    def verifier_tour(self, nom_joueur: str) -> bool:
        """Vérifie si c'est le tour du joueur."""
        if not self.partie_en_cours or not self.jeu:
            return False
        
        joueur_actuel = self.jeu.plateau.joueur_actuel()
        return joueur_actuel.nom == nom_joueur
    
    def obtenir_joueur(self, nom: str) -> Optional[Joueur]:
        """Retourne l'objet Joueur correspondant au nom."""
        if not self.jeu:
            return None
        
        for joueur in self.jeu.plateau.joueurs:
            if joueur.nom == nom:
                return joueur
        return None


def main():
    """Point d'entrée du serveur."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Serveur du jeu Smiles')
    parser.add_argument('--host', default='0.0.0.0', help='Adresse du serveur')
    parser.add_argument('--port', type=int, default=5555, help='Port du serveur')
    parser.add_argument('--max-joueurs', type=int, default=5, help='Nombre maximum de joueurs')
    
    args = parser.parse_args()
    
    serveur = ServeurJeu(host=args.host, port=args.port, max_joueurs=args.max_joueurs)
    serveur.demarrer()


if __name__ == "__main__":
    main()