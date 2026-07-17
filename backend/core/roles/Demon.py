from typing import TYPE_CHECKING

from backend.core.cards.acquisitions.Acquisition import Acquisition
from backend.userIo.interface import IOType
from ..PlayerCardGroup import PlayedCardGroup as groupe

from .PlayerRole import PlayerRole
from ..Power import Power
if TYPE_CHECKING:
    from ..Game import Game
    from ..Player import Player
    from ..cards.Card import Card

class Demon(PlayerRole):
    def __init__(self, img_path: str) -> None:
        super().__init__(img_path)
        self.powers = [Power.NO_MALEFICES_EFFECT]
        self._acquisition = Acquisition(-1, "", 0, 0)

    def can_use_instant_power(self, game: "Game", owner: "Player") -> "tuple[bool, str]":
        """vérifie si le joueur peut jouer son pouvoir de role"""
        from ..cards.ephemerides.LuneRouge import LuneRouge
        ephemeride = game.get_ephemeride()
        if not isinstance(ephemeride, LuneRouge):
            return False, "Ce n'est pas le bon ephemeride"
        return super().can_use_instant_power(game, owner)   


     
    def apply_instant_power(self, game: "Game", owner: "Player"):
        """applique le pouvoir instantannée du role"""
        from backend.core.cards.professionnals.SalaryCard import SalaryCard
        interface = owner.get_interface()
        for player in game.players:
            if player== owner:
                continue

            # récupération des cartes achetables
            ##############""
            available_cards = []
            card_value = {i : [] for i in range(0, 10)}
            played_cards = player.get_card_from_group(groupe.ACQUISITIONS)
            played_cards += player.get_card_from_group(groupe.VIE_PERSONNELLE)
            played_cards += player.get_card_from_group(groupe.VIE_PROFESSIONNELLE)
            for card in played_cards:
                if isinstance(card, Acquisition):
                    card.original_price += card.smiles
                success, reason = card.can_be_played(owner, game)

                if isinstance(card, Acquisition):
                    card.original_price -= card.smiles
                if success:
                    card_value[card.smiles].append(card)

            # récupération des salaires
            salaries = owner.get_available_salary()

            card_value[0] = []
            for value in card_value:
                can_place = self._acquisition._has_exact_salary_combination(salaries, value)
                if can_place:
                    available_cards.extend(card_value[value])

            if len(available_cards) == 0:
                continue
            ####################""
            # selectionner la carte
            selected_card = interface.ask_card(
                prompt=f"Selectionner la carte a acheter au joueur {player.name}",
                cards = available_cards, 
                kind=IOType.CARD_PICKER
            )
            assert selected_card is not None, "aucune cartes choisie"


            cost = selected_card.smiles
            while True:
                selected_salaries: list[Card] = interface.ask_salaries(selected_card, salaries, cost)
                selected_sum = sum(card.get_value() for card in selected_salaries)
                if selected_sum == cost:
                    break
                print(f"[ERROR] Demon : le joueur doit payer exactement {cost}, mais a sélectionné un total de {selected_sum}")

            for card in selected_salaries:
                from backend.core.PlayerCardGroup import PlayedCardGroup
                from backend.core.cards.acquisitions.objets_magiques.Amulette import Amulette
                from backend.core.cards.specials.Heritage import Heritage
                success = False
                if isinstance(card, Amulette):
                    success = owner.move_placed_cards(card, PlayedCardGroup.ACQUISITIONS, PlayedCardGroup.CARTES_PROTEGEES)
                elif isinstance(card, Heritage):
                    success = owner.move_placed_cards(card, PlayedCardGroup.CARTES_SPECIALES, PlayedCardGroup.CARTES_PROTEGEES)
                else:    
                    success = owner.move_placed_cards(card, PlayedCardGroup.VIE_PROFESSIONNELLE, PlayedCardGroup.CARTES_PROTEGEES) 
                if not success:
                    print("[ERROR] déplace de carte échouée")
                    return 

            # poser la carte acheter
            player.remove_card(selected_card, game)
            owner.add_card_to_hand(selected_card)
            selected_card.play_card(game, owner)




        return super().apply_instant_power(game, owner)
        
    def get_card_rule(self) -> str:
        return "PP : permet de rejouer apres avoir jouer un malus | PE (Lune Rouge) : permet d'acheter les cartes posés par les autres joueurs en respectant les règles du jeu de base, le prix est 1 liasse par smile, avec un maximum d'une carte par joueur et en mettant l'appoint a chaque fois (le prix exacte)"+ "\n"+ "="*10+ "\n" + super().get_card_rule()
