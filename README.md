# 🚀 Démarrage Rapide - Jeu de Cartes Smile

## Installation en 5 minutes ⚡

### 1. Créer le projet

```bash
mkdir ~/smile-game-python
cd ~/smile-game-python
mkdir templates static
```

### 2. Installer Python et les dépendances

```bash
# Créer l'environnement virtuel
python3 -m venv venv

# Activer
source venv/bin/activate

# Installer les dépendances
pip install flask flask-socketio python-socketio eventlet
```

### 3. Créer les fichiers

**Créez `app.py`** :
- Copiez le code depuis l'artifact "Smile Game - Flask Backend (app.py)"

**Créez `templates/index.html`** :
- Copiez le code depuis l'artifact "Smile Game - Frontend HTML"

**Créez `requirements.txt`** :
```
flask==3.0.0
flask-socketio==5.3.5
python-socketio==5.10.0
eventlet==0.33.3
```

### 4. Lancer le jeu

```bash
python3 app.py
```

Ouvrez votre navigateur : **http://localhost:5000**

---

## 🎮 Comment jouer (Mode Multijoueur)

### Joueur 1 (Hôte) :
1. Cliquez sur **"Créer une partie"**
2. Entrez votre nom
3. Choisissez le nombre de joueurs (2-5)
4. **NOTEZ LE CODE** affiché (ex: "abc123")
5. Partagez ce code avec vos amis
6. Attendez que les autres rejoignent
7. Cliquez sur **"Démarrer la partie"**

### Autres joueurs :
1. Cliquez sur **"Rejoindre une partie"**
2. Entrez votre nom
3. Entrez le **CODE** reçu
4. Attendez que l'hôte démarre

### Pendant la partie :
- **C'est votre tour ?** Les boutons sont activés
- **Pas votre tour ?** Attendez et regardez les autres jouer
- Chaque joueur voit sa propre main
- Les cartes posées par tous sont visibles

---

## 🌐 Jouer sur plusieurs appareils

### Sur le même réseau WiFi :

**1. Trouvez votre IP :**
```bash
ip addr show | grep "inet " | grep -v 127.0.0.1
```
Exemple de résultat : `192.168.1.10`

**2. Les autres joueurs se connectent à :**
```
http://192.168.1.10:5000
```

### Via Internet (avec ngrok) :

**1. Installez ngrok :**
```bash
# Télécharger
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar -xvzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/

# Configurer (inscrivez-vous sur ngrok.com)
ngrok config add-authtoken VOTRE_TOKEN
```

**2. Lancez ngrok (terminal séparé) :**
```bash
ngrok http 5000
```

**3. Partagez l'URL ngrok :**
Exemple : `https://abc123.ngrok.io`

---

## ⚡ Commandes rapides

```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Lancer le serveur
python3 app.py

# Installer/réinstaller les dépendances
pip install -r requirements.txt

# Mettre à jour les dépendances
pip install --upgrade flask flask-socketio
```

---

## 🐛 Problèmes courants

### Erreur "Module not found: flask_socketio"
```bash
pip install flask-socketio python-socketio
```

### Port 5000 déjà utilisé
Changez dans `app.py` (dernière ligne) :
```python
socketio.run(app, debug=True, host='0.0.0.0', port=3000)
```

### Les joueurs ne peuvent pas se connecter
1. Vérifiez que tous sont sur le même WiFi
2. Désactivez le pare-feu :
```bash
sudo ufw allow 5000
```

### Déconnexions fréquentes
- Gardez les navigateurs actifs (pas en veille)
- Vérifiez votre connexion Internet

---

## 📝 Structure minimale requise

```
smile-game-python/
├── venv/
├── templates/
│   └── index.html
├── app.py
└── requirements.txt
```

---

## 🎯 Test rapide (Solo)

Pour tester seul avant de jouer avec des amis :

1. Lancez le serveur
2. Ouvrez 2 onglets :
   - **Chrome** : http://localhost:5000
   - **Firefox** (ou navigation privée) : http://localhost:5000
3. Créez une partie dans l'onglet 1
4. Rejoignez avec l'onglet 2
5. Jouez en alternant entre les onglets !

---

## 🎉 C'est tout !

Vous êtes prêt à jouer ! Si vous avez des questions, consultez le **README.md** complet.

**Amusez-vous bien ! 😊🎮**