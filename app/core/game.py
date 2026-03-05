"""
Game — moteur de jeu.
Aucun import Flask. Utilise io_context.emit pour les broadcasts.
"""
from typing import TYPE_CHECKING, List

from app.core.game_state import GameState

if TYPE_CHECKING:
    from app.cards.base.card import Card
    from app.cards.concrete.special.cards import CasinoCard, ArcEnCielCard
    from app.core.player import Player


class Game:
    """Orchestre une partie : joueurs, deck, phases de jeu."""

    def __init__(self, game_id: str, deck: List["Card"], num_players: int):
        self.id: str = game_id
        self.players: List["Player"] = []
        self.num_players: int = num_players
        self.deck: List["Card"] = deck
        self.discard: List["Card"] = []
        self.last_discard = None
        self.current_player: int = 0
        self.phase: str = "waiting"
        self.players_joined: int = 0
        self.host_id: int = 0
        self.casino_card: "CasinoCard | None" = None
        self.pending_hardship = None
        self.pending_interaction: dict | None = None  # état d'attente interaction joueur
        self.arcEnCielMode: bool = False
        self.arcEnCielCard: "ArcEnCielCard | None" = None

    # ------------------------------------------------------------------ #
    #  Deck                                                                #
    # ------------------------------------------------------------------ #

    def get_card_from_deck(self) -> "Card":
        return self.deck.pop()

    def add_to_discard(self, card: "Card") -> None:
        self.discard.append(card)

    # ------------------------------------------------------------------ #
    #  Joueurs                                                             #
    # ------------------------------------------------------------------ #

    def add_player(self, player: "Player") -> None:
        from app.core.player import Player as P
        if isinstance(player, P):
            self.players.append(player)
            if player.connected:
                self.players_joined += 1

    def next_player(self) -> None:
        self.change_current_player()
        self.phase = "draw"

    def change_current_player(self) -> None:
        """Passe au prochain joueur connecté."""
        self.current_player = (self.current_player + 1) % self.num_players
        attempts = 0
        while not self.players[self.current_player].connected and attempts < self.num_players:
            self.current_player = (self.current_player + 1) % self.num_players
            attempts += 1

    # ------------------------------------------------------------------ #
    #  Sérialisation                                                       #
    # ------------------------------------------------------------------ #

    def to_snapshot(self) -> GameState:
        return GameState(
            game_id=self.id,
            players=[p.to_dict() for p in self.players],
            deck_count=len(self.deck),
            discard=[c.to_dict() for c in self.discard],
            current_player=self.current_player,
            phase=self.phase,
            num_players=self.num_players,
            players_joined=self.players_joined,
            host_id=self.host_id,
            casino=self.casino_card.to_dict() if self.casino_card else {"open": False},
            pending_hardship=self.pending_hardship,
            arc_en_ciel=self.arcEnCielMode,
            arc_en_ciel_card=self.arcEnCielCard.to_dict() if self.arcEnCielCard else {},
            last_discard=self.last_discard,
        )

    def to_dict(self) -> dict:
        return self.to_snapshot().to_dict()

    # ------------------------------------------------------------------ #
    #  Broadcast                                                          #
    # ------------------------------------------------------------------ #

    def broadcast_update(self, message: str = "") -> None:
        from app.core.io_context import emit
        for player in self.players:
            if player.connected:
                state = self._get_state_for_player(player.id)
                emit(
                    "game_updated",
                    {"game": state, "message": message},
                    room=player.session_id,
                )

    def _get_state_for_player(self, player_id: int) -> dict:
        state = self.to_dict()
        state["players"] = [
            p.to_dict(hide_hand=(p.id != player_id))
            for p in self.players
        ]
        return state

    # ------------------------------------------------------------------ #
    #  Recherche de carte                                                  #
    # ------------------------------------------------------------------ #

    def find_card_by_id(self, card_id: str) -> "Card | None":
        """Cherche une carte dans tout le jeu (main, posées, reçues, casino)."""
        if self.casino_card and self.casino_card.id == card_id:
            return self.casino_card
        if self.arcEnCielCard and self.arcEnCielCard.id == card_id:
            return self.arcEnCielCard
        for player in self.players:
            for card in player.hand:
                if card.id == card_id:
                    return card
            for card in player.get_all_played_cards():
                if card.id == card_id:
                    return card
            for card in player.received_hardships:
                if card.id == card_id:
                    return card
        return None

    # ------------------------------------------------------------------ #
    #  Actions de tour                                                     #
    # ------------------------------------------------------------------ #

    def skip_turn(self, player_id: int) -> tuple[bool, str]:
        """
        Le joueur confirme qu'il passe son tour (skip_turns > 0).
        Appelé uniquement via le bouton dédié côté client.
        """
        if self.current_player != player_id:
            return False, "Ce n'est pas votre tour"
        if self.phase != "draw":
            return False, "Action impossible dans cette phase"

        player = self.players[player_id]
        if player.skip_turns <= 0:
            return False, "Vous n'avez pas de tour à passer"

        player.skip_turns -= 1
        self.next_player()
        self.broadcast_update(f"{player.name} passe son tour.")
        return True, f"{player.name} passe son tour"

    def draw_card_from_deck(self, player_id: int) -> tuple[bool, str]:
        """
        Phase draw : pioche depuis la pioche.
        Bloqué si le joueur a des tours à passer (doit utiliser skip_turn).
        """
        if self.current_player != player_id:
            return False, "Ce n'est pas votre tour"
        if self.phase != "draw":
            return False, "Ce n'est pas la phase de pioche"

        player = self.players[player_id]

        # Empêcher la pioche si le joueur doit passer son tour
        if player.skip_turns > 0:
            return False, f"Vous devez passer votre tour ({player.skip_turns} restant(s))"

        if not self.deck:
            return False, "La pioche est vide"

        card = self.get_card_from_deck()
        player.add_card_to_hand(card)
        self.phase = "play"
        return True, ""

    def draw_card_from_discard(self, player_id: int) -> tuple[bool, str]:
        """
        Phase draw : prend la dernière carte de la défausse et la joue directement.
        La carte doit pouvoir être jouée.
        """
        if self.current_player != player_id:
            return False, "Ce n'est pas votre tour"
        if self.phase != "draw":
            return False, "Ce n'est pas la phase de pioche"
        if not self.discard:
            return False, "La défausse est vide"

        player = self.players[player_id]
        card = self.discard[-1]

        can_play, reason = card.can_be_played(player, self)
        if not can_play:
            return False, reason

        self.discard.pop()
        player.add_card_to_hand(card)
        was_arc_mode = self.arcEnCielMode
        card.play_card(self, player)

        if was_arc_mode and self.arcEnCielMode and self.arcEnCielCard:
            self.arcEnCielCard.add_card_played(self, player)

        if self.pending_interaction is None and not self.arcEnCielMode:
            self.next_player()

        self.broadcast_update(f"{player.name} pioche depuis la défausse.")
        return True, ""

    def discard_card_from_hand(self, player_id: int, card_id: str) -> tuple[bool, str]:
        """
        Phase play : défausse une carte de sa main pour terminer son tour.
        Interdit pendant l'arc-en-ciel (utiliser stop_arc_en_ciel à la place).
        """
        if self.current_player != player_id:
            return False, "Ce n'est pas votre tour"
        if self.phase != "play":
            return False, "Vous devez d'abord piocher"
        if self.arcEnCielMode:
            return False, "Arc-en-ciel actif — utilisez 'Arrêter mon tour' pour terminer"

        player = self.players[player_id]
        card = next((c for c in player.hand if c.id == card_id), None)
        if card is None:
            return False, "Carte introuvable dans la main"

        player.remove_card_from_hand(card)
        self.discard.append(card)
        self.last_discard = card.to_dict()
        self.next_player()
        return True, ""

    def discard_job_card(self, player_id: int, job_id: str | None = None) -> tuple[bool, str]:
        """
        Défausse un métier.
        - En phase draw : à la place de piocher (termine le tour).
        - En phase play : uniquement si le métier est intérimaire (ne termine PAS le tour).
        """
        if self.current_player != player_id:
            return False, "Ce n'est pas votre tour"
        if self.phase not in ("draw", "play"):
            return False, "Action impossible dans cette phase"

        player = self.players[player_id]
        jobs = player.get_job()
        if not jobs:
            return False, "Vous n'avez pas de métier"

        if self.phase == "play":
            # Uniquement les intérimaires peuvent être défaussés en cours de tour
            interim_jobs = [j for j in jobs if j.status == "intérimaire"]
            if not interim_jobs:
                return False, "Seul un métier intérimaire peut être défaussé en cours de tour"
            if job_id:
                job = next((j for j in interim_jobs if j.id == job_id), None)
            else:
                job = interim_jobs[0]
        else:
            # Phase draw : on peut défausser n'importe quel métier
            if job_id:
                job = next((j for j in jobs if j.id == job_id), None)
            else:
                job = jobs[0]

        if job is None:
            return False, "Métier introuvable"

        job.discard_play_card(self, player)

        if self.phase == "draw":
            # Défausser le métier en début de tour termine le tour
            self.next_player()
        # En phase play + intérimaire : on reste en phase play, le joueur continue

        return True, ""

    def discard_marriage_card(self, player_id: int) -> tuple[bool, str]:
        """
        Phase draw : divorce (défausse le mariage à la place de piocher).
        """
        if self.current_player != player_id:
            return False, "Ce n'est pas votre tour"
        if self.phase != "draw":
            return False, "Le divorce n'est possible qu'en début de tour"
        if not self.players[player_id].is_married():
            return False, "Vous n'êtes pas marié(e)"

        player = self.players[player_id]
        marriage = player.get_marriage()
        if marriage is None:
            return False, "Carte mariage introuvable"

        marriage.discard_play_card(self, player)
        self.next_player()
        return True, ""

    def stop_arc_en_ciel(self, player_id: int) -> tuple[bool, str]:
        """
        Le joueur arrête volontairement son tour Arc-en-Ciel.
        Repioche autant de cartes qu'il en a posées (nb_cards_played).
        """
        if self.current_player != player_id:
            return False, "Ce n'est pas votre tour"
        if not self.arcEnCielMode or not self.arcEnCielCard:
            return False, "L'arc-en-ciel n'est pas actif"

        player = self.players[player_id]
        self.arcEnCielCard.end_arc_en_ciel(self, player)
        self.next_player()
        self.broadcast_update(f"{player.name} termine son arc-en-ciel !")
        return True, ""

    # ------------------------------------------------------------------ #
    #  Logique de jeu                                                      #
    # ------------------------------------------------------------------ #

    def play_card(self, player_id: int, card_id: str) -> tuple[bool, str]:
        """
        Pose une carte pour le joueur donné.
        Retourne (succès, message).
        Si la carte déclenche une interaction (pending_interaction),
        next_player() sera appelé par events.py après résolution.
        """
        player = self.players[player_id]
        card = next((c for c in player.hand if c.id == card_id), None)
        if card is None:
            return False, "Carte introuvable dans la main du joueur"

        can_play, reason = card.can_be_played(player, self)
        if not can_play:
            return False, reason

        # Mémoriser si l'arc-en-ciel était déjà actif AVANT ce coup
        was_arc_mode = self.arcEnCielMode

        card.play_card(self, player)

        # Compter uniquement les cartes SUPPLÉMENTAIRES (pas l'arc-en-ciel elle-même)
        if was_arc_mode and self.arcEnCielMode and self.arcEnCielCard:
            self.arcEnCielCard.add_card_played(self, player)

        # Ne passer le tour que si : pas d'interaction en attente ET arc-en-ciel terminé/inactif
        if self.pending_interaction is None and not self.arcEnCielMode:
            self.next_player()

        self.broadcast_update()
        return True, ""