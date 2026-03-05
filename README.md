# 🃏 Card Game — Refactorisation

> Jeu de cartes multijoueur en ligne — Python 3.10+ · Flask · Flask-SocketIO

---

## Contexte — ce qui a été fait

L'ancienne version du projet tenait dans **un seul fichier `cards.py` de 3 741 lignes** contenant pêle-mêle les classes de cartes, la logique de jeu, la classe `Player`, la classe `Game` et des appels directs à `flask_socketio.emit`.

Ce fichier a été découpé en **36 fichiers organisés** selon les principes décrits ci-dessous, sans perdre aucune logique.

---

## Principes clés de l'architecture

### 1. Séparation core / interfaces

Le dossier `app/core/` et `app/cards/` ne contiennent **aucun import Flask**. Toute la logique métier est pure et testable unitairement.

```
core/ + cards/   →  logique métier pure (jeu, joueur, cartes…)
interfaces/      →  fait le lien entre Flask/SocketIO et le core
```

### 2. Injection de l'emit SocketIO (`io_context`)

**Problème de l'ancienne version :** chaque carte faisait `from flask_socketio import emit`, créant une dépendance Flask dans toute la hiérarchie des cartes, ce qui rendait les tests impossibles.

**Solution :** un module `app/core/io_context.py` expose une fonction `emit()` neutre. Flask injecte le vrai emit au démarrage dans `app/__init__.py`. Hors Flask (tests, terminal), l'emit est un no-op.

```python
# Dans les cartes — aucune dépendance Flask
from app.core.io_context import emit

# Au démarrage Flask (app/__init__.py) — injection unique
from app.core import io_context
io_context.set_emit(socketio_emit)
```

### 3. Hiérarchie des cartes

Chaque niveau a une responsabilité précise :

| Classe | Rôle |
|--------|------|
| `Card` (abstraite) | Interface commune : `get_effect()`, `can_be_played()`, `play_card()` |
| `HardshipCard` (abstraite) | Coup dur : cible toujours un adversaire, gère la sélection de cible |
| `SpecialCard` (abstraite) | Cartes à usage unique ou à conditions. Cible configurable. |
| `PermanentEffet` (mixin) | Accorde des pouvoirs passifs via `get_power()` |
| Classes concrètes | Implémentent uniquement leur logique spécifique |

```
Card (abstraite)
├── HardshipCard (abstraite)   → AccidentCard, DivorceCard, TaxCard…
├── SpecialCard (abstraite)    → CasinoCard, ArcEnCielCard, GirlPowerCard…
├── JobCard                    → AstronauteJob, BanditJob, MedecinJob…
├── StudyCard / SalaryCard
├── FlirtCard / MarriageCard / ChildCard
├── AnimalCard                 → LicorneAnimal, DragonAnimal
├── AquisitionCard             → HouseCard, TravelCard, SabreCard…
└── OtherCard                  → LegionCard, PriceCard
```

### 4. Pattern Strategy — Actions

Les cartes **décrivent** leur effet via `get_effect()` qui retourne un `CardEffect` (données pures). Le moteur peut **appliquer** l'effet via le registre des actions pour les effets simples.

```python
# La carte décrit l'effet — aucune logique métier
def get_effect(self) -> CardEffect:
    return CardEffect(type="block_turns", target="opponent", params={"blocked_turns": 1})

# Le registre fait le lien effet → action
ACTION_REGISTRY = {
    "block_turns":    BlockTurnsAction,
    "drain_resource": DrainResourceAction,
    "gain_resource":  GainResourceAction,
}
```

### 5. Deux registres — les seuls points d'extension

| Fichier | Mapping |
|---------|---------|
| `app/cards/registry.py` | `id` (str) → classe carte concrète |
| `app/actions/registry.py` | `type effet` (str) → classe action |

> **Pour ajouter une nouvelle carte :**
> 1. Créer la classe dans `app/cards/concrete/.../ma_carte.py`
> 2. L'enregistrer dans `app/cards/registry.py`
> 3. Créer l'action dans `app/actions/` si elle est nouvelle
> 4. L'enregistrer dans `app/actions/registry.py`
> 5. Ajouter l'entrée dans `data/cards.json`
>
> **Aucun autre fichier à modifier.**

---

## Structure complète du projet

```
card_game/
│
├── run.py                          # Point d'entrée Flask + SocketIO
├── config.py                       # Configurations dev / prod
├── requirements.txt
│
├── app/
│   ├── __init__.py                 # Factory create_app() + injection io_context
│   │
│   ├── core/                       # Moteur de jeu — AUCUN import Flask
│   │   ├── io_context.py           # Pont d'émission injectable (découple Flask)
│   │   ├── effect.py               # CardEffect (données pures)
│   │   ├── deck.py                 # Deck (mélange, pioche)
│   │   ├── player.py               # Classe Player
│   │   ├── game_state.py           # Snapshot sérialisable de la partie
│   │   └── game.py                 # Moteur — orchestre les tours
│   │
│   ├── cards/
│   │   ├── base/
│   │   │   ├── card.py             # Classe de base abstraite Card
│   │   │   ├── hardship_card.py    # HardshipCard (abstraite) — coups durs
│   │   │   ├── special_card.py     # SpecialCard (abstraite) — cartes spéciales
│   │   │   └── permanent_effect.py # Mixin PermanentEffet (pouvoirs passifs)
│   │   │
│   │   ├── concrete/
│   │   │   ├── personal/
│   │   │   │   ├── flirt.py        # FlirtCard, FlirtWithChildCard, MarriageCard, AdulteryCard
│   │   │   │   ├── marriage.py     # Re-export pour éviter les imports circulaires
│   │   │   │   └── children.py     # ChildCard + tous les enfants (Angela, Beatrix…)
│   │   │   │
│   │   │   ├── professional/
│   │   │   │   ├── study_salary.py # StudyCard, SalaryCard
│   │   │   │   └── job.py          # JobCard + tous les métiers (Astronaute, Bandit…)
│   │   │   │
│   │   │   ├── acquisitions/
│   │   │   │   └── cards.py        # AquisitionCard, HouseCard, TravelCard, SabreCard, NounouCard…
│   │   │   │
│   │   │   ├── animals/
│   │   │   │   └── cards.py        # AnimalCard, LicorneAnimal, DragonAnimal
│   │   │   │
│   │   │   ├── hardship/
│   │   │   │   └── cards.py        # Tous les coups durs (Accident, Divorce, Tax, Prison…)
│   │   │   │
│   │   │   ├── special/
│   │   │   │   └── cards.py        # Toutes les cartes spéciales (Casino, ArcEnCiel, GirlPower…)
│   │   │   │
│   │   │   └── other/
│   │   │       └── cards.py        # LegionCard, PriceCard
│   │   │
│   │   ├── registry.py             # ★ id (str) → classe concrète
│   │   └── loader.py               # Chargement des cartes depuis data/cards.json
│   │
│   ├── actions/                    # Pattern Strategy pour les effets de cartes
│   │   ├── base_action.py          # Interface abstraite BaseAction
│   │   ├── player_actions.py       # Actions sur soi-même (gain, pioche, rejouer)
│   │   ├── opponent_actions.py     # Actions sur les adversaires (bloquer, drainer…)
│   │   └── registry.py             # ★ type effet (str) → classe Action
│   │
│   ├── session/                    # Salles et gestion des tours
│   │   ├── room.py                 # Salle (lobby + partie)
│   │   ├── room_manager.py         # Singleton de toutes les salles actives
│   │   └── turn_manager.py         # Timer et passage automatique des tours
│   │
│   └── interfaces/
│       └── web/                    # Interface navigateur — Flask/SocketIO ICI SEULEMENT
│           ├── routes.py           # Routes HTTP (lobby, login…)
│           └── events.py           # Événements WebSocket (join, play_card, disconnect…)
│
├── data/
│   ├── cards.json                  # Définition de toutes les cartes (à remplir)
│   └── decks/
│       └── starter_deck.json       # (optionnel)
│
└── tests/
    └── test_core/
        └── test_game.py            # Exemples de tests unitaires (sans Flask)
```

---

## Démarrage rapide

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Lancer le serveur
python run.py
```

---

## Format de data/cards.json

Chaque entrée doit avoir une clé `card_id` qui correspond à une entrée du registre (`app/cards/registry.py`). Les autres champs sont passés directement au constructeur de la classe.

```json
[
  {
    "card_id": "accident",
    "image": "static/img/accident.png",
    "count": 3
  },
  {
    "card_id": "study",
    "image": "static/img/bac.png",
    "study_type": "bac",
    "levels": 2,
    "count": 4
  },
  {
    "card_id": "salary",
    "image": "static/img/salary_3.png",
    "level": 3,
    "count": 5
  },
  {
    "card_id": "astronaute",
    "image": "static/img/astronaute.png",
    "job_name": "Astronaute",
    "salary": 5,
    "studies": 6,
    "count": 1
  }
]
```

---

## Ce qu'il reste à faire

| Tâche | Fichiers concernés |
|-------|--------------------|
| Remplir `data/cards.json` | `data/cards.json` |
| Migrer les templates HTML | `app/templates/` (base.html, lobby.html, game.html) |
| Migrer les fichiers statiques | `app/static/` |
| Brancher les callbacks WebSocket des cartes interactives | `app/interfaces/web/events.py` |
| Ajouter l'interface terminal | `app/interfaces/terminal/cli_client.py` |
| Compléter les tests | `tests/` |

---

## Dépendances

| Package | Rôle |
|---------|------|
| `flask` | Framework web |
| `flask-socketio` | WebSocket temps réel |
| `python-dotenv` | Variables d'environnement |
| `eventlet` | Serveur async pour SocketIO |
| `python-socketio[client]` | Client SocketIO pour le terminal |
| `pytest` | Tests unitaires |
