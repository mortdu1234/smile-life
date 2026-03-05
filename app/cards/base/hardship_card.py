"""
HardshipCard — classe abstraite pour les cartes « coup dur ».
S'applique toujours sur un adversaire.  Aucun import Flask direct.
"""
from typing import TYPE_CHECKING, Dict, Any

from app.cards.base.card import Card
from app.core.io_context import emit

if TYPE_CHECKING:
    from app.core.player import Player
    from app.core.game import Game


class HardshipCard(Card):
    """Carte coup dur : cible toujours un adversaire."""

    def __init__(self, image_path: str):
        super().__init__(image_path)
        self.smiles: int = 0

    def __str__(self) -> str:
        return f"{self.__class__.__name__}"

    # ------------------------------------------------------------------ #
    #  Sérialisation                                                       #
    # ------------------------------------------------------------------ #

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({"type": "hardship"})
        return base

    # ------------------------------------------------------------------ #
    #  Règles                                                              #
    # ------------------------------------------------------------------ #

    def can_be_played(self, current_player: "Player", game: "Game") -> tuple[bool, str]:
        targets = self.get_available_targets(game, current_player)
        for t in targets:
            if not t["immune"]:
                return True, ""
        return False, "Pas de cible possible"

    def other_rules(self, game: "Game", current_player: "Player", player: "Player") -> bool:
        """Retourne True si le joueur est immunisé (règles propres à la sous-classe)."""
        return False

    def get_card_rule(self) -> str:
        return "Carte Coup Dur — s'applique à un adversaire."

    # ------------------------------------------------------------------ #
    #  Ciblage                                                             #
    # ------------------------------------------------------------------ #

    def get_available_targets(self, game: "Game", current_player: "Player") -> list[dict]:
        targets = []
        for player in game.players:
            info = player.to_dict()
            info["immune"] = (
                player == current_player
                or self.other_rules(game, current_player, player)
            )
            targets.append(info)
        return targets

    # ------------------------------------------------------------------ #
    #  Pose de la carte — étape 1 : demander la cible                     #
    # ------------------------------------------------------------------ #

    def play_card(self, game: "Game", current_player: "Player") -> None:
        """
        Émet la demande de sélection de cible et enregistre pending_interaction.
        next_player() sera appelé par events.py après resolve() ou annulation.
        """
        targets = self.get_available_targets(game, current_player)

        # Cible unique non-immune → on applique directement, pas besoin d'interaction
        non_immune = [t for t in targets if not t["immune"]]
        if len(non_immune) == 1:
            target = game.players[non_immune[0]["id"]]
            self.apply_effect(game, target, current_player)
            current_player.hand.remove(self)
            target.received_hardships.append(self)
            return

        emit("select_hardship_target", {
            "card": self.to_dict(),
            "available_targets": targets,
        }, room=current_player.session_id)

        game.pending_interaction = {
            "type": "hardship_target",
            "card_id": self.id,
            "player_id": current_player.id,
        }

    # ------------------------------------------------------------------ #
    #  Pose de la carte — étape 2 : appliquer après confirmation          #
    # ------------------------------------------------------------------ #

    def resolve(self, game: "Game", current_player: "Player", data: dict) -> None:
        """
        Appelé par events.py après confirm_hardship_target.
        Applique l'effet sur la cible choisie.
        """
        target_id = data.get("target_player_id")
        if target_id is None:
            return
        target = game.players[target_id]
        self.apply_effect(game, target, current_player)
        current_player.hand.remove(self)
        target.received_hardships.append(self)

    # ------------------------------------------------------------------ #
    #  Effet — à surcharger dans chaque sous-classe                       #
    # ------------------------------------------------------------------ #

    def apply_effect(
        self,
        game: "Game",
        target_player: "Player",
        current_player: "Player",
    ) -> None:
        """Applique l'effet du coup dur sur target_player."""
        pass