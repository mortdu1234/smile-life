# 🎮 Jeu de Cartes Smiles - Mode Réseau

Système client-serveur pour jouer au jeu de cartes Smiles en ligne.

## 📁 Structure des fichiers

```
projet/
├── code.py              # Classes du jeu (cartes, joueurs, plateau)
├── serveur.py           # Serveur de jeu
├── client.py            # Client de jeu
└── ressources/          # Dossier des images de cartes
    ├── aquisition_cards/
    ├── animals/
    ├── attack_cards/
    ├── personnal_life/
    ├── professionnal_life/
    └── special_cards/
```

## 🚀 Installation

Aucune dépendance externe n'est nécessaire, seulement Python 3.7+

```bash
# Vérifier la version de Python
python --version
```

## 🎯 Utilisation

### 1. Démarrer le serveur

```bash
# Démarrage simple (localhost, port 5555)
python serveur.py

# Avec options personnalisées
python serveur.py --host 0.0.0.0 --port 5555 --max-joueurs 5
```

**Options du serveur :**
- `--host` : Adresse d'écoute (défaut: 0.0.0.0)
- `--port` : Port d'écoute (défaut: 5555)
- `--max-joueurs` : Nombre maximum de joueurs (défaut: 5)

### 2. Connecter des clients

#### Mode interactif (recommandé)
```bash
python client.py
```

Suivez ensuite les menus pour :
1. Entrer l'adresse du serveur
2. Choisir votre nom
3. Marquer que vous êtes prêt
4. Jouer !

#### Mode automatique (pour tests)
```bash
python client.py --host localhost --port 5555 --nom Alice --auto
```

**Options du client :**
- `--host` : Adresse du serveur (défaut: localhost)
- `--port` : Port du serveur (défaut: 5555)
- `--nom` : Nom du joueur
- `--auto` : Connexion automatique sans menu

## 🎮 Déroulement d'une partie

1. **Connexion** : Les joueurs se connectent au serveur
2. **Salon d'attente** : Les joueurs marquent qu'ils sont prêts
3. **Début de partie** : La partie démarre automatiquement quand tous sont prêts (minimum 2 joueurs)
4. **Tours de jeu** : Chaque joueur joue à son tour
5. **Fin de partie** : Quand la pioche est vide, les scores sont calculés

## 🎯 Actions de jeu disponibles

Pendant votre tour, vous pouvez :
- **Piocher** : Dans la pioche ou la défausse
- **Poser une carte** : Si les conditions sont remplies
- **Défausser une carte** : Pour finir votre tour
- **Jouer un malus** : Sur un adversaire
- **Utiliser une carte spéciale** : Avec effets variés

## 🔧 Architecture technique

### Communication réseau

**Format des messages :**
```json
{
    "type": "action",
    "donnees": {
        "action": "poser_carte",
        "index_carte": 2
    },
    "timestamp": 1234567890.123
}
```

**Types de messages :**
- `connexion` : Demande de connexion au serveur
- `action` : Action de jeu (piocher, poser, défausser)
- `etat_jeu` : État complet du jeu envoyé par le serveur
- `erreur` : Message d'erreur
- `pret` : Joueur prêt à commencer

### Classes principales

**Serveur (serveur.py) :**
- `ServeurJeu` : Gère les connexions et la partie
- `ClientHandler` : Gère chaque client individuellement
- `Message` : Structure de message

**Client (client.py) :**
- `ClientJeu` : Connexion au serveur et envoi d'actions
- `InterfaceConsole` : Interface en ligne de commande
- `Message` : Structure de message

## 🧪 Tests

### Tester en local avec 3 joueurs

**Terminal 1 - Serveur :**
```bash
python serveur.py
```

**Terminal 2 - Joueur 1 :**
```bash
python client.py
# Entrer: localhost, 5555, Alice
```

**Terminal 3 - Joueur 2 :**
```bash
python client.py
# Entrer: localhost, 5555, Bob
```

**Terminal 4 - Joueur 3 :**
```bash
python client.py
# Entrer: localhost, 5555, Charlie
```

Tous les joueurs marquent "Prêt" et la partie démarre !

## 🌐 Jouer sur le réseau local

1. **Sur la machine serveur :**
```bash
# Trouver votre IP locale
# Windows: ipconfig
# Linux/Mac: ifconfig ou ip addr

# Démarrer le serveur
python serveur.py --host 0.0.0.0
```

2. **Sur les machines clientes :**
```bash
python client.py
# Entrer l'IP du serveur (ex: 192.168.1.10)
```

## 🔒 Sécurité

⚠️ **Attention** : Ce serveur est conçu pour un usage local/privé :
- Pas d'authentification
- Pas de chiffrement
- Pas de protection contre les tricheurs

Pour un usage en ligne, il faudrait ajouter :
- SSL/TLS pour chiffrer les communications
- Authentification des joueurs
- Validation côté serveur de toutes les actions
- Rate limiting
- Gestion des déconnexions/reconnexions

## 🐛 Dépannage

### Le client ne peut pas se connecter
- Vérifier que le serveur est démarré
- Vérifier l'adresse IP et le port
- Vérifier le pare-feu (autoriser le port)

### La partie ne démarre pas
- Minimum 2 joueurs requis
- Tous les joueurs doivent être marqués "Prêt"

### Déconnexion inattendue
- Vérifier la stabilité du réseau
- Le serveur affiche les déconnexions dans la console

## 📝 TODO / Améliorations futures

- [ ] Interface graphique (Pygame, Tkinter, ou web)
- [ ] Reconnexion automatique en cas de déconnexion
- [ ] Chat entre joueurs
- [ ] Sauvegarde/chargement de partie
- [ ] Statistiques des joueurs
- [ ] Replay de parties
- [ ] Mode spectateur
- [ ] Animations des cartes
- [ ] Sons et musique
- [ ] Support mobile

## 📄 Licence

Projet éducatif - À définir selon vos besoins

## 👥 Contribution

Pour contribuer au projet :
1. Fork le repository
2. Créer une branche pour votre feature
3. Commit vos changements
4. Push vers la branche
5. Créer une Pull Request

## 📞 Support

En cas de problème, vérifier :
1. Les logs du serveur (dans la console)
2. Les logs du client (dans la console)
3. La structure des fichiers et dossiers

Bon jeu ! 🎉
