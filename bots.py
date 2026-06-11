"""
simulate_bot_game.py
--------------------
Lance une partie complète entre deux bots et affiche le résultat.

Usage (depuis la racine du projet) :
    python -m simulate_bot_game
ou
    python simulate_bot_game.py
"""

import random
import sys

# ── Imports du projet ─────────────────────────────────────────────────────────
from backend.core.Game import Game, TurnState
from backend.core.Player import Player
from backend.core.cards.LoaderCard import build_card
from backend.userIo.botIO import BotIO

# ── Paramètres de simulation ──────────────────────────────────────────────────
MAX_TURNS   = 300   # sécurité anti-boucle infinie
DECK_COPIES = 2     # nombre d'exemplaires de chaque carte dans le deck


# ─────────────────────────────────────────────────────────────────────────────
#  Construction du deck
# ─────────────────────────────────────────────────────────────────────────────

def build_deck() -> list:
    """Construit un deck mélangé à partir du catalogue complet."""
    import json
    from backend.game import _build_cards
    
    with open("preset/standard.json", "r", encoding="utf-8") as f:
        preset = json.load(f)
    deck = _build_cards(preset)
    random.shuffle(deck)
    return deck


# ─────────────────────────────────────────────────────────────────────────────
#  Calcul du score (smiles) d'un joueur
# ─────────────────────────────────────────────────────────────────────────────

def compute_score(player: Player) -> int:
    """Somme les smiles de toutes les cartes posées."""
    return sum(card.get_smiles() for card in player.cards.values())


# ─────────────────────────────────────────────────────────────────────────────
#  Tour d'un bot
# ─────────────────────────────────────────────────────────────────────────────

def play_bot_turn(game: Game) -> None:
    """Exécute un tour complet pour le bot courant."""
    player = game.get_current_player()
    pid    = player.get_id()

    # ── Cas : joueur doit passer un ou plusieurs tours ────────────────────────
    if player.skip_turn > 0:
        game.skip_turn(pid)
        return

    # ── Phase PIOCHE ──────────────────────────────────────────────────────────
    if game.turn_state == TurnState.PIOCHE:
        # Tente de piocher depuis la défausse si la carte est jouable
        last_discard = game.get_last_discard()
        if last_discard:
            ok, _ = last_discard.can_be_played(player, game)
            if ok and random.random() < 0.3:          # 30 % de chance de prendre la défausse
                game.draw_card_from_discard(pid)
                return

        # Sinon pioche dans la pioche normale
        if game.deck:
            game.draw_card_from_deck(pid)
        else:
            # Pioche vide : on passe le tour (fin de partie imminente)
            return

    # ── Phase POSE ────────────────────────────────────────────────────────────
    if game.turn_state == TurnState.POSE:
        hand = player.get_hand()
        if not hand:
            return

        # Essaie de jouer une carte au hasard parmi celles qui sont jouables
        playable = []
        for card in hand:
            ok, _ = card.can_be_played(player, game)
            if ok:
                playable.append(card)

        if playable:
            chosen = random.choice(playable)
            success, reason = game.place_card(pid, chosen.get_id())
            if success:
                return
            # En cas d'échec inattendu, on se défausse
            game.discard_card_from_hand(pid, chosen.get_id())
        else:
            # Aucune carte jouable : défausse une carte aléatoire
            chosen = random.choice(hand)
            game.discard_card_from_hand(pid, chosen.get_id())


# ─────────────────────────────────────────────────────────────────────────────
#  Point d'entrée
# ─────────────────────────────────────────────────────────────────────────────

def simulate() -> None:
    print("=" * 60)
    print("       SIMULATION BOT vs BOT")
    print("=" * 60)

    # Création des bots
    bot1 = Player("Bot-Alpha", 0, BotIO())
    bot2 = Player("Bot-Beta",  1, BotIO())

    # Deck
    deck = build_deck()
    print(f"[INIT] Deck construit : {len(deck)} cartes")

    # Partie
    game = Game(id="SIM-001", players=[bot1, bot2], deck=deck)
    print(f"[INIT] Partie lancée —\n")

    winner = None
    turn   = 0

    while turn < MAX_TURNS:
        turn += 1
        current = game.get_current_player()

        # Vérification victoire avant le tour
        for p in game.players:
            if len(game.deck) == 0:
                winner = None
                score = 0
                for player in game.players:
                    score_p = player.get_smiles()
                    if score_p > score:
                        winner = player
                        score = score_p
                break
        if winner:
            break

        # Vérifie que la pioche n'est pas vide
        if not game.deck and game.turn_state == TurnState.PIOCHE:
            print(f"[INFO] Tour {turn} — Pioche vide, fin de partie !")
            break

        play_bot_turn(game)

    # ── Résultats ─────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"  FIN DE PARTIE après {turn} tour(s)")
    print("=" * 60)

    scores = {p.name: compute_score(p) for p in game.players}
    for name, score in scores.items():
        print(f"  {name:<15} : {score} smiles  ({len(game.players[0].cards if name == bot1.name else game.players[1].cards)} cartes posées)")

    if winner:
        print(f"\n🏆  VAINQUEUR : {winner.name} avec {scores[winner.name]} smiles !")
    else:
        best = max(scores, key=lambda n: scores[n])
        if list(scores.values()).count(scores[best]) > 1:
            print("\n🤝  ÉGALITÉ !")
        else:
            print(f"\n🏆  VAINQUEUR (meilleur score) : {best} avec {scores[best]} smiles !")

    print("\n── Historique des 5 dernières actions ──")
    for line in game.historique:
        print(f"  • {line}")
    print("=" * 60)


if __name__ == "__main__":
    for i in range(5000):
        simulate()