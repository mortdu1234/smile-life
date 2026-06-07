"""
Logique métier de la partie.
Responsabilités :
  - Charger les presets JSON
  - Construire le deck (liste de Card) via le registre de cartes
  - Instancier Game() et Player()
  - Exposer les actions de jeu (piocher, jouer une carte, passer le tour…)

Aucune dépendance Flask ici.
"""
from __future__ import annotations

import json
import random
from pathlib import Path

from .webSocket import broadcast_game
from .userIo.web import WebIO

from .core.Game import Game
from .core.Player import Player
from .core.cards.Card import Card

from .hub import get_room, mark_playing
from .store import game_save, game_get, game_delete
from .core.cards.LoaderCard import build_card

# ── Presets ────────────────────────────────────────────────────────────────────

_ROOT = Path(__file__).parent.parent
PRESET_DIR = next(
    (p for p in [_ROOT / "preset", _ROOT / "presets"] if p.exists()),
    _ROOT / "presets",
)


def _card_count(deck_spec: dict) -> int:
    return sum(int(v) for v in deck_spec.values() if int(v) > 0)


def load_presets() -> list[dict]:
    """Retourne les métadonnées de tous les presets (triés par nom de fichier)."""
    if not PRESET_DIR.exists():
        return []
    result = []
    for path in sorted(PRESET_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            result.append({
                "id": data["id"],
                "label": data["label"],
                "description": data.get("description", ""),
                "card_count": _card_count(data.get("deck", {})),
            })
        except (KeyError, json.JSONDecodeError):
            continue
    return result


def load_preset(preset_id: str) -> dict | None:
    """Retourne le preset complet ou None."""
    if not PRESET_DIR.exists():
        return None
    for path in PRESET_DIR.glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if data.get("id") == preset_id:
                return data
        except (KeyError, json.JSONDecodeError):
            continue
    return None


# ── Construction du deck ───────────────────────────────────────────────────────

def _build_cards(preset: dict) -> list[Card]:
    cards: list[Card] = []
    skipped: list[str] = []

    for card_id, count in preset.get("deck", {}).items():
        count = int(count)
        if count == 0:
            continue
        for _ in range(count):
            card = build_card(card_id)
            if card is not None:
                cards.append(card)
            else:
                if card_id not in skipped:
                    skipped.append(card_id)

    if skipped:
        print(f"[card_registry] card_id inconnus ignorés : {skipped}")

    random.shuffle(cards)
    return cards


# ── Cycle de vie de la partie ──────────────────────────────────────────────────

def start_game(game_id: str, host_pseudo: str) -> tuple[Game | None, str | None]:
    room = get_room(game_id)
    if not room:
        return None, "Partie introuvable."
    if room["host"] != host_pseudo:
        return None, "Seul l'hôte peut lancer la partie."
    if room["status"] != "waiting":
        return None, "La partie a déjà été lancée."
    if not room.get("preset_id"):
        return None, "Aucun preset sélectionné."

    preset = load_preset(room["preset_id"])
    if not preset:
        return None, f"Preset « {room['preset_id']} » introuvable."

    deck = _build_cards(preset)
    players = [Player(pseudo, idx, WebIO()) for idx, pseudo in enumerate(room["players"])]

    game = Game(id=game_id, players=players, deck=deck)
    game_save(game)
    mark_playing(game_id)

    return game, None


def get_game(game_id: str) -> Game | None:
    return game_get(game_id)


# ── Helpers internes ───────────────────────────────────────────────────────────

def _resolve_player(game: Game, pseudo: str) -> tuple[Player | None, str | None]:
    """Retourne le joueur correspondant au pseudo, ou une erreur."""
    player = next((p for p in game.players if p.name == pseudo), None)
    if not player:
        return None, "Joueur introuvable."
    return player, None


# ── Actions de jeu — délèguent à Game.py ──────────────────────────────────────

def draw_from_deck(game_id: str, pseudo: str) -> tuple[bool, str]:
    """Game.draw_card_from_deck — phase PIOCHE uniquement."""
    game = game_get(game_id)
    if not game:
        return False, "Partie introuvable."
    player, err = _resolve_player(game, pseudo)
    if err:
        return False, err
    success, reason = game.draw_card_from_deck(player.id)
    if success:
        game_save(game)
        broadcast_game(game)
    return success, reason


def draw_from_discard(game_id: str, pseudo: str) -> tuple[bool, str]:
    """Game.draw_card_from_discard — phase PIOCHE uniquement."""
    game = game_get(game_id)
    if not game:
        return False, "Partie introuvable."
    player, err = _resolve_player(game, pseudo)
    if err:
        return False, err
    success, reason = game.draw_card_from_discard(player.id)
    if success:
        game_save(game)
        broadcast_game(game)
    return success, reason


def place_card(game_id: str, pseudo: str, card_id: int) -> tuple[bool, str]:
    """Game.place_card — phase POSE uniquement."""
    game = game_get(game_id)
    if not game:
        return False, "Partie introuvable."
    player, err = _resolve_player(game, pseudo)
    if err:
        return False, err
    success, reason = game.place_card(player.id, card_id)
    if success:
        game_save(game)
        broadcast_game(game)
    return success, reason


def discard_from_hand(game_id: str, pseudo: str, card_id: int) -> tuple[bool, str]:
    """Game.discard_card_from_hand — phase POSE uniquement."""
    game = game_get(game_id)
    if not game:
        return False, "Partie introuvable."
    player, err = _resolve_player(game, pseudo)
    if err:
        return False, err
    success, reason = game.discard_card_from_hand(player.id, card_id)
    if success:
        game_save(game)
        broadcast_game(game)
    return success, reason


def discard_job(game_id: str, pseudo: str, card_id: int) -> tuple[bool, str]:
    """Game.discard_job_card — démissionner d'un métier posé."""
    game = game_get(game_id)
    if not game:
        return False, "Partie introuvable."
    player, err = _resolve_player(game, pseudo)
    if err:
        return False, err
    success, reason = game.discard_job_card(player.id, card_id)
    if success:
        game_save(game)
        broadcast_game(game)
    return success, reason


def discard_wedding(game_id: str, pseudo: str, card_id: int) -> tuple[bool, str]:
    """Game.discard_wedding_card — divorcer, phase PIOCHE uniquement."""
    game = game_get(game_id)
    if not game:
        return False, "Partie introuvable."
    player, err = _resolve_player(game, pseudo)
    if err:
        return False, err
    success, reason = game.discard_wedding_card(player.id, card_id)
    if success:
        game_save(game)
        broadcast_game(game)
    return success, reason


def discard_adultery(game_id: str, pseudo: str, card_id: int) -> tuple[bool, str]:
    """Game.discard_adultery_card — mettre fin à l'adultère, phase PIOCHE uniquement."""
    game = game_get(game_id)
    if not game:
        return False, "Partie introuvable."
    player, err = _resolve_player(game, pseudo)
    if err:
        return False, err
    success, reason = game.discard_adultery_card(player.id, card_id)
    if success:
        game_save(game)
        broadcast_game(game)
    return success, reason


def skip_turn(game_id: str, pseudo: str) -> tuple[bool, str]:
    """Game.skip_turn — passe le tour si le joueur a des tours à passer."""
    game = game_get(game_id)
    if not game:
        return False, "Partie introuvable."
    player, err = _resolve_player(game, pseudo)
    if err:
        return False, err
    success, reason = game.skip_turn(player.id)
    if success:
        game_save(game)
        broadcast_game(game)
    return success, reason


def next_turn(game_id: str, pseudo: str) -> tuple[bool, str]:
    """Passe au tour suivant manuellement (cas d'urgence/debug)."""
    game = game_get(game_id)
    if not game:
        return False, "Partie introuvable."
    if game.get_current_player().name != pseudo:
        return False, "Ce n'est pas votre tour."
    game.next_turn()
    game_save(game)
    broadcast_game(game)
    return True, ""


def end_game(game_id: str) -> None:
    game_delete(game_id)