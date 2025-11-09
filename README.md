# ðŸ˜Š Jeu de Cartes Smile - Version Multijoueur

Un jeu de cartes stratégique et humoristique où vous devez construire la vie la plus heureuse possible en accumulant des smiles ! Gérez votre carrière, votre vie personnelle, vos acquisitions tout en évitant les coups durs de vos adversaires.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![Flask](https://img.shields.io/badge/Flask-3.0.0-lightgrey)
![License](https://img.shields.io/badge/license-MIT-orange)

## 📋 Table des matières

- [Fonctionnalités](#-fonctionnalités)
- [Prérequis](#-prérequis)
- [Installation](#-installation)
- [Démarrage](#-démarrage)
- [Comment jouer](#-comment-jouer)
- [Structure du projet](#-structure-du-projet)
- [Technologies utilisées](#-technologies-utilisées)
- [Configuration avancée](#-configuration-avancée)
- [Développement](#-développement)

## ✨ Fonctionnalités

### 🎮 Gameplay
- **Multijoueur en temps réel** : 2 à 5 joueurs simultanés via WebSocket
- **Système de cartes diversifié** : 
  - 🏢 **Métiers** : 30+ professions avec pouvoirs uniques (Astronaute, Bandit, Chercheur...)
  - 📚 **Études** : Cartes simples et doubles pour débloquer les métiers
  - 💰 **Salaires** : 4 niveaux de revenus
  - 💕 **Vie personnelle** : Flirts, mariages, adultères, enfants (10 noms)
  - 🏠 **Acquisitions** : Maisons (3 tailles) et voyages (5 destinations)
  - ⭐ **Cartes spéciales** : Casino, Chance, Arc-en-ciel, Vengeance...
  - ⚠️ **Coups durs** : 9 types d'attaques (Divorce, Licenciement, Prison...)

### 🎯 Fonctionnalités techniques
- **Deck personnalisable** : Interface graphique pour configurer chaque carte
- **Presets de jeu** : Configurations prédéfinies (Standard, Test)
- **Gestion des déconnexions** : Reprise automatique si un joueur se reconnecte
- **Mode hôte/invité** : L'hôte contrôle le démarrage et la configuration
- **Affichage en temps réel** : Toutes les actions sont synchronisées instantanément
- **Images des cartes** : Fallback texte automatique si l'image ne charge pas

### 🌐 Modes de jeu
- **Mode privé** : Partie locale sur `localhost:5000`
- **Mode public** : Accessible depuis Internet via Cloudflare Tunnel

## 🔧 Prérequis

- **Python** 3.8 ou supérieur
- **pip** (gestionnaire de paquets Python)
- **Cloudflared** (optionnel, pour le mode public)

### Installation de Cloudflared (optionnel)

**Windows** :
```bash
# Télécharger depuis https://github.com/cloudflare/cloudflared/releases
```

**macOS** :
```bash
brew install cloudflare/cloudflare/cloudflared
```

**Linux** :
```bash
# Debian/Ubuntu
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb
```

## 📥 Installation

### 1. Cloner le projet
```bash
git clone <url-du-repo>
cd smile-card-game
```

### 2. Créer un environnement virtuel (recommandé)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Installer les dépendances
```bash
pip install -r requirement.txt
```

Les dépendances incluent :
- `flask==3.0.0` - Framework web
- `flask-socketio==5.3.5` - Communication temps réel
- `python-socketio==5.10.0` - Client/serveur WebSocket
- `eventlet==0.33.3` - Serveur asynchrone

## 🚀 Démarrage

### Méthode 1 : Lancement automatique (recommandé)

**Windows** :
```bash
lancer_jeu.bat
```

**macOS/Linux** :
```bash
chmod +x lancer_jeu.sh
./lancer_jeu.sh
```

Le script vous proposera :
1. **Mode PRIVÉ** : Accessible uniquement sur votre réseau local
2. **Mode PUBLIC** : Accessible depuis Internet (nécessite Cloudflared)

### Méthode 2 : Lancement manuel

```bash
python app.py
```

L'application sera accessible sur `http://127.0.0.1:5000`

## 🎲 Comment jouer

### Création d'une partie

1. **Accédez à l'interface** : Ouvrez votre navigateur sur `http://127.0.0.1:5000`
2. **Créer une partie** :
   - Cliquez sur "🎮 Créer une partie"
   - Entrez votre nom
   - Choisissez le nombre de joueurs (2-5)
   - *Optionnel* : Cliquez sur "🎴 Personnaliser le deck" pour configurer les cartes
3. **Partagez le code** : Un code à 8 caractères s'affiche (ex: `abc12345`)
4. **Attendez les joueurs** : Les autres joueurs doivent rejoindre avec ce code
5. **Démarrez** : Cliquez sur "🚀 Démarrer la partie"

### Rejoindre une partie

1. Cliquez sur "🚪 Rejoindre une partie"
2. Entrez votre nom
3. Saisissez le code de la partie
4. Cliquez sur "Rejoindre"

### Déroulement d'un tour

Chaque tour se compose de 2 phases :

#### Phase 1 : Piocher (DRAW)
- **Option A** : Piocher une carte du deck
- **Option B** : Piocher la dernière carte de la défausse (si jouable immédiatement)
- **Option C** : Défausser un métier/mariage/adultère (avant de piocher)
- **Option D** : Passer son tour

#### Phase 2 : Jouer (PLAY)
- **Jouer une carte** : Respecter les règles de pose
- **Défausser une carte** : Si vous ne pouvez/voulez pas jouer
- **Passer son tour**

### Types de cartes et règles

#### 📚 Études
- Nécessaires pour obtenir un métier
- Simple = 1 niveau | Double = 2 niveaux
- Maximum 6 études posées (sauf pouvoir spécial)

#### 💼 Métiers
- Donnent accès aux salaires
- Nécessitent un certain niveau d'études
- Certains ont des pouvoirs spéciaux :
  - **Architecte** : 1 maison gratuite
  - **Astronaute** : Récupère une carte de la défausse
  - **Bandit** : Immunisé aux impôts et licenciements
  - **Chercheur** : Joue avec 6 cartes en main
  - **Médium** : Voit les 13 prochaines cartes
  - **Journaliste** : Voit la main de tous les joueurs
  - Et bien d'autres...

#### 💰 Salaires
- Niveaux 1 à 4
- Permettent d'acheter des acquisitions
- Le maximum dépend de votre métier

#### 💕 Vie personnelle
1. **Flirts** (8 lieux)
   - Maximum 5 sans mariage
   - Voler les flirts du même lieu
2. **Mariage** (5 villes)
   - Nécessite au moins 1 flirt
   - Réduit le prix des maisons de 50%
3. **Adultère**
   - Nécessite un mariage
   - Permet de dépasser la limite de flirts
4. **Enfants** (10 prénoms)
   - Nécessite un mariage OU flirt camping/hôtel

#### 🏠 Acquisitions
- **Maisons** : Petite (6💰), Moyenne (8💰), Grande (10💰)
  - Prix réduit de 50% si marié
- **Voyages** : 3💰 chacun (5 destinations)

#### ⭐ Cartes spéciales
- **Casino** : Pariez des salaires (même niveau = gagnant le 2e joueur)
- **Chance** : Choisissez parmi 3 cartes piochées
- **Arc-en-ciel** : Jouez jusqu'à 3 cartes puis repiochez
- **Étoile filante** : Récupérez une carte de la défausse
- **Vengeance** : Renvoyez un coup dur reçu
- **Troc** : Échangez une carte aléatoire avec un joueur
- **Tsunami** : Mélange et redistribue toutes les mains
- **Piston** : Posez un métier sans condition d'études
- **Héritage** : 3 ou 5💰 utilisables pour acheter

#### ⚠️ Coups durs
- **Impôts** : Retire 1 salaire
- **Licenciement** : Retire le métier (sauf fonctionnaires)
- **Divorce** : Retire le mariage (et enfants/adultère si adultère actif)
- **Maladie/Accident/Burn-out** : Passer 1 tour
- **Prison** : Passer 3 tours + perte du métier bandit + 2 cartes
- **Redoublement** : Retire 1 étude
- **Attentat** : TOUS les joueurs perdent TOUS leurs enfants

### Conditions de victoire

🏆 **Objectif** : Avoir le plus de **Smiles** (😊) quand le deck est vide

**Calcul des smiles** :
- Chaque carte posée rapporte des smiles (indiqués sur la carte)
- **Bonus combo** : Licorne + Arc-en-ciel + Étoile filante = +3 😊

## 📁 Structure du projet

```
smile-card-game/
│
├── app.py                      # Point d'entrée principal
├── init.py                     # Routes Flask et gestion des connexions
├── constants.py                # Configuration, variables globales, factory
├── card_classes.py             # Classes de toutes les cartes
├── special_power.py            # Gestion des pouvoirs spéciaux (socket events)
├── requirement.txt             # Dépendances Python
│
├── templates/
│   └── index.html              # Interface principale du jeu
│
├── static/
│   ├── js/
│   │   ├── constants.js        # Variables globales JS
│   │   ├── home.js             # Menu et configuration du deck
│   │   ├── script.js           # Logique principale du jeu
│   │   ├── special_cards.js    # Gestion des cartes spéciales
│   │   └── job_power.js        # Gestion des pouvoirs de métiers
│   └── css/
│       └── style.css           # Styles (actuellement vide, utilise Tailwind)
│
├── ressources/                 # Images des cartes
│   ├── personnal_life/
│   │   ├── professionnal_life/
│   │   ├── flirts/
│   │   ├── mariages/
│   │   └── children/
│   ├── aquisition_cards/
│   ├── special_cards/
│   └── hardship_cards/
│
├── lancer_jeu.bat              # Script de lancement Windows
└── lancer_jeu.sh               # Script de lancement macOS/Linux
```

## 🛠️ Technologies utilisées

### Backend
- **Flask** 3.0.0 - Framework web Python
- **Flask-SocketIO** 5.3.5 - Communication bidirectionnelle temps réel
- **Eventlet** 0.33.3 - Serveur WSGI asynchrone

### Frontend
- **Socket.IO** 4.5.4 - Client WebSocket
- **Tailwind CSS** 3.x - Framework CSS utility-first
- **JavaScript** vanilla - Pas de framework (performance optimale)

### Infrastructure
- **Cloudflare Tunnel** - Exposition publique sécurisée (optionnel)

## ⚙️ Configuration avancée

### Personnaliser le deck

#### Via l'interface (recommandé)
1. Lors de la création de partie, cliquez sur "🎴 Personnaliser le deck"
2. Parcourez les catégories et ajustez les quantités avec +/-
3. Utilisez les presets pour des configurations rapides
4. Validez votre configuration

#### Via le code
Éditez `constants.py` > `cardCategories` :

```python
cardCategories = {
    "Ma Catégorie": [
        { 
            id: "ma_carte", 
            name: "Ma Carte Custom", 
            defaultCount: 5, 
            image: "chemin/vers/image.png" 
        },
        # ...
    ]
}
```

### Ajouter une nouvelle carte

1. **Créer la classe** dans `card_classes.py` :
```python
class MaCarteJob(JobCard):
    def __init__(self, job_name, salary, studies, image_path):
        super().__init__(job_name, salary, studies, image_path)
        self.power = "mon_pouvoir"
    
    def apply_instant_power(self, game, current_player):
        # Logique du pouvoir
        pass
```

2. **Ajouter au factory** dans `constants.py` :
```python
card_builders = {
    "ma_carte": lambda: MaCarteJob("Ma Carte", 3, 2, "path/to/image.png"),
}
```

3. **Ajouter l'image** dans `ressources/`

4. **Ajouter les règles** :
```python
def get_card_rule(self):
    return "Description de ma carte\n" \
           + "RÈGLES\n" \
           + "- Règle 1\n" \
           + "- Règle 2\n"
```

### Configuration du serveur

**Port par défaut** : 5000
Pour changer le port, modifiez `app.py` :
```python
socketio.run(app, debug=True, host='0.0.0.0', port=VOTRE_PORT)
```

**Mode debug** : Activé par défaut
Pour la production, passez `debug=False`

### Gestion des sessions

Les sessions utilisent `flask.session` avec une clé secrète.
⚠️ **Important** : Changez la clé dans `constants.py` :
```python
app.secret_key = 'votre_nouvelle_cle_secrete_super_longue'
```

## 👨‍💻 Développement

### Architecture technique

**Flux de données** :
```
Client (Browser) 
    ↕ Socket.IO
Serveur Flask-SocketIO 
    ↕ Python Objects
Classes Game / Player / Card
```

**Événements Socket.IO principaux** :
- `create_game` / `join_game` - Gestion des parties
- `draw_card` / `play_card` / `discard_card` - Actions de jeu
- `game_updated` - Synchronisation de l'état
- `select_*` - Interactions spéciales (salaires, cibles, etc.)

### Ajouter un pouvoir de métier avec interaction

1. **Créer le métier** dans `card_classes.py`
2. **Ajouter l'événement socket** dans `special_power.py` :
```python
@socketio.on('mon_pouvoir_selection')
def handle_mon_pouvoir(data):
    card_id = data.get('card_id')
    player_id, game, _ = check_game()
    # Logique
```

3. **Créer l'interface** dans `job_power.js` :
```javascript
function showMonPouvoirModal(data) {
    // Afficher modal
}

socket.on('mon_pouvoir_modal', (data) => {
    showMonPouvoirModal(data);
});
```

### Tests

**Tester en local** :
1. Ouvrez plusieurs onglets sur `http://127.0.0.1:5000`
2. Créez une partie dans un onglet
3. Rejoignez avec les autres onglets

**Tester en réseau** :
1. Lancez en mode public avec `lancer_jeu.bat`/`lancer_jeu.sh`
2. Partagez l'URL Cloudflare générée
3. Les autres joueurs peuvent rejoindre depuis n'importe où

### Debugging

**Logs serveur** :
- Tous les événements sont loggés avec `print()`
- Format : `[start]: nom_fonction` ou `[appel]: event_name`

**Logs client** :
- Ouvrez la console du navigateur (F12)
- Les événements sont loggés avec `log(message, data)`

**Problèmes courants** :
- **"Carte non trouvée"** : Vérifiez que l'ID de carte est correct
- **"Ce n'est pas votre tour"** : La synchronisation a échoué, rafraîchissez
- **Images non chargées** : Vérifiez le chemin dans `ressources/`
- **Déconnexions** : Vérifiez que Eventlet est bien installé

## 📝 Licence

Ce projet est sous licence MIT. Vous êtes libre de l'utiliser, le modifier et le distribuer.

## 🤝 Contribution

Les contributions sont les bienvenues ! 

1. Fork le projet
2. Créez une branche (`git checkout -b feature/ma-feature`)
3. Committez vos changements (`git commit -m 'Ajout de ma feature'`)
4. Push vers la branche (`git push origin feature/ma-feature`)
5. Ouvrez une Pull Request

## 📧 Support

Pour toute question ou bug :
- Ouvrez une issue sur GitHub
- Consultez la documentation dans le code source

## 🎉 Crédits

Développé avec ❤️ pour les amateurs de jeux de cartes stratégiques !

---

**Bon jeu ! 😊🎴🎮**