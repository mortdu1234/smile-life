from .interface import UserIO, IOType
from typing import TYPE_CHECKING, Sequence

if TYPE_CHECKING:
    from ..core.Player import Player
    from ..core.Game import Game
    from ..core.cards.Card import Card
    from ..core.cards.acquisitions.Acquisition import Acquisition

import random

class BotIO(UserIO):

    # ── Boucle principale ──────────────────────────────────────────────────────

    def play_turn(self, player: "Player", game: "Game") -> None:
        """Joue un tour complet : pioche puis pose/défausse."""
        from ..core.Game import TurnState

        # — Phase PIOCHE —
        if game.turn_state == TurnState.PIOCHE:
            drew = self._do_draw(player, game)
            # draw_card_from_discard fait next_turn() en interne → tour terminé
            if not drew:
                return

        # — Phase POSE —
        if game.turn_state == TurnState.POSE:
            self._do_place_or_discard(player, game)

    def _do_draw(self, player: "Player", game: "Game") -> bool:
        """
        Pioche une carte.
        Retourne True si on est encore en phase POSE (pioche deck classique),
        False si le tour est déjà terminé (pioche défausse = next_turn inclus).
        """
        last_discard = game.get_last_discard()

        # 30 % de chance de tenter la défausse si elle est jouable
        if last_discard and random.random() < 0.3:
            ok, _ = game.draw_card_from_discard(player.get_id())
            if ok:
                return False  # next_turn() a déjà été appelé

        ok, _ = game.draw_card_from_deck(player.get_id())
        if not ok:
            # Pioche vide ou tour bloqué (skip_turn) → passe quand même
            game.skip_turn(player.get_id())
            return False

        return True

    def _do_place_or_discard(self, player: "Player", game: "Game") -> None:
        """Pose une carte jouable aléatoire, sinon se défausse."""
        hand = list(player.get_hand())  # copie pour éviter mutation pendant itération
        random.shuffle(hand)

        for card in hand:
            ok, _ = card.can_be_played(player, game)
            if ok:
                game.place_card(player.get_id(), card.get_id())
                return

        # Aucune carte jouable → défausse aléatoire
        if hand:
            card = random.choice(hand)
            game.discard_card_from_hand(player.get_id(), card.get_id())

    # ── Réponses aux questions (déjà présentes, inchangées) ───────────────────

    def ask_player(self, prompt: str, players: list["Player"], kind: IOType) -> "Player | None":
        """retourne l'id du joueur selectionnée"""
        return random.choice(players)
    
    def ask_card(self, prompt: str, cards: list["Card"], kind: IOType) -> "Card | None":
        """retourne l'id de la carte selectionnée"""
        return random.choice(cards)

    def ask_salaries(self, acquisition: "Acquisition", salaries: Sequence["Card"], cost: int) -> list["Card"]:
        """Demande au joueur de sélectionner des salaires pour payer une acquisition.
        Retourne la liste des cartes salaire choisies (somme >= cost garanti côté frontend)."""
        selected_cards = []
        actual_cost = 0
        for card in salaries:
            selected_cards.append(card)
            if actual_cost >= cost:
                return selected_cards
        return selected_cards
    
    def show_cards(self, title: str, prompt: str, cards: Sequence["Card"]) -> None:
        """Affiche une liste de cartes en consultation (pas de sélection).
        Bloque jusqu'à ce que le joueur ferme l'overlay."""
        pass

    
    def show_players_hand(self, players_names: Sequence[str], players_hands: Sequence[Sequence["Card"]]):
        """Affiche la liste des cartes en main des joueurs"""
        pass

    
    def submit(self, index: int) -> None:
        """Appelé par la route Flask quand l'utilisateur choisit (choix simple)."""
        pass

    
    def submit_indices(self, indices: list[int]) -> None:
        """Appelé par la route Flask quand l'utilisateur valide une sélection multiple."""
        pass

    
    def submit_dismiss(self) -> None:
        """Appelé par la route Flask quand l'utilisateur ferme un overlay de consultation."""
        pass