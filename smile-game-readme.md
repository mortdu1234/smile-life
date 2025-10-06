# 🎮 Jeu de Cartes Smile - Version Python

Un jeu de cartes multijoueur développé avec Flask et Python.

## 📋 Prérequis

- Python 3.7 ou supérieur
- pip (gestionnaire de paquets Python)
- Un navigateur web moderne

## 🚀 Installation sous Linux Mint

### Étape 1 : Installer Python et pip

```bash
# Mettre à jour les paquets
sudo apt update

# Installer Python 3 et pip (normalement déjà installés)
sudo apt install python3 python3-pip python3-venv

# Vérifier l'installation
python3 --version
pip3 --version
```

### Étape 2 : Créer le projet

```bash
# Créer un dossier pour le projet
mkdir ~/smile-game-python
cd ~/smile-game-python

# Créer la structure des dossiers
mkdir templates static

# Créer l'environnement virtuel
python3 -m venv venv

# Activer l'environnement virtuel
source venv/bin/activate
```

### Étape 3 : Installer Flask

```bash
# Installer Flask
pip install flask
```

### Étape 4 : Créer les fichiers

Créez les 3 fichiers suivants :

#### 1. `app.py` (fichier principal)
Copiez le contenu du fichier "Smile Game - Flask Backend (app.py)"

#### 2. `templates/index.html` (interface web)
Copiez le contenu du fichier "Smile Game - Frontend HTML (templates/index.html)"

#### 3. `static/style.css` (optionnel - styles supplémentaires)
Vous pouvez créer ce fichier vide pour l'instant ou y ajouter vos propres styles CSS personnalisés.

## 🎯 Lancement du jeu

```bash
# S'assurer d'être dans le dossier du projet
cd ~/smile-game-python

# Activer l'environnement virtuel (si pas déjà fait)
source venv/bin/activate

# Lancer le serveur
python3 app.py
```

Le serveur démarrera sur `http://localhost:5000`

Ouvrez votre navigateur et allez à cette adresse pour jouer !

## 🎮 Comment jouer

1. Sélectionnez le nombre de joueurs (2-5)
2. Entrez les noms des joueurs
3. Cliquez sur "Commencer la partie"
4. Suivez les instructions à l'écran pour jouer

### Actions possibles par tour :
- **Piocher dans la pioche** : Prenez une carte et jouez-en une de votre main
- **Piocher dans la défausse** : Prenez la dernière carte de la défausse et jouez-la immédiatement
- **Défausser une carte posée** : Retirez une de vos cartes jouées

## 📁 Structure du projet

```
smile-game-python/
├── venv/                  # Environnement virtuel
├── templates/
│   └── index.html        # Interface web du jeu
├── static/
│   └── style.css         # Styles CSS (optionnel)
├── app.py                # Serveur Flask
└── README.md             # Ce fichier
```

## 🛑 Arrêter le serveur

Appuyez sur `Ctrl + C` dans le terminal où le serveur tourne.

## 🔧 Dépannage

### Le port 5000 est déjà utilisé ?
Modifiez la dernière ligne de `app.py` :
```python
app.run(debug=True, host='0.0.0.0', port=3000)  # Changez 5000 en 3000
```

### Erreur "Module not found" ?
```bash
# Réinstaller Flask
pip install --upgrade flask
```

### Permission refusée ?
```bash
# Changer les permissions du dossier
sudo chown -R $USER:$USER ~/smile-game-python
```

### L'environnement virtuel ne s'active pas ?
```bash
# Recréer l'environnement virtuel
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install flask
```

## 🌐 Accès depuis d'autres appareils (même réseau)

Pour permettre à d'autres appareils sur le même réseau local d'accéder au jeu :

1. Trouvez votre adresse IP locale :
```bash
ip addr show | grep inet
```

2. Les autres joueurs peuvent accéder au jeu via :
```
http://VOTRE_IP:5000
```
(Remplacez VOTRE_IP par votre adresse IP locale, ex: 192.168.1.10)

## ✨ Fonctionnalités

- ✅ 2 à 5 joueurs
- ✅ Toutes les cartes du jeu original
- ✅ Tous les métiers avec leurs pouvoirs
- ✅ Toutes les cartes spéciales
- ✅ Tous les coups durs
- ✅ Calcul automatique des scores
- ✅ Interface web moderne et responsive
- ✅ Jeu en local (hot-seat)

## 🔜 Améliorations futures

- [ ] Multijoueur en ligne avec WebSocket
- [ ] Sauvegarde et reprise de partie
- [ ] Statistiques des joueurs
- [ ] Mode IA
- [ ] Animations et effets sonores

## 📝 Notes

- Le jeu se joue en "hot-seat" : tous les joueurs jouent sur le même ordinateur
- Les parties sont stockées en mémoire et disparaissent quand le serveur s'arrête
- Pour un jeu multijoueur en ligne, il faudra implémenter WebSocket ou Socket.IO

## 🆘 Support

Si vous rencontrez des problèmes, vérifiez :
1. Que Python 3.7+ est installé
2. Que Flask est bien installé dans l'environnement virtuel
3. Que vous avez activé l'environnement virtuel avant de lancer le serveur
4. Que le port 5000 n'est pas utilisé par un autre programme

## 📜 Licence

Ce projet est libre d'utilisation pour un usage personnel et éducatif.

## 🎉 Amusez-vous bien !

Bon jeu ! 😊
