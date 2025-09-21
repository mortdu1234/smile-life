from cards import *
from players import *
from deck import deck

class game:
    def __init__(self):
        self.deck: deck = deck()
        self.discard: deck = deck()
        self.players: list[players] = []
        self.current_player_idx: int = 0
        self.init_game()

    def new_player(self, player_name: str):
        """add a new player to the game

        Args:
            player_name (str): name of the player
        """
        if len(self.players) == 5:
            print("there is already 5 players in the game") # ERROR
        checker = False
        for player in self.players:
            if player.get_name == player_name:
                checker = True
                print("there is already a player like this") # ERROR
        if not checker:
            print(f"add the player {player_name}")
            self.players.append(players(player_name))

    def remove_player(self, player_name: str):
        """remove a player from the player list

        Args:
            player_name (str): name of the player
        """
        for idx, player in enumerate(self.players):
            if player.get_name == player_name:
                print(f"remove the player {player.get_name}")
                self.players.pop(idx)

    def init_game(self):
        """initialise the game
        """
        # initialisation des cartes
        
        # animaux
        self.deck.add_a_card(Animal(0, 1, "chat"))
        self.deck.add_a_card(Animal(0, 1, "chien"))
        self.deck.add_a_card(Animal(0, 1, "lapin"))
        self.deck.add_a_card(Animal(0, 3, "licorne"))
        self.deck.add_a_card(Animal(0, 1, "poussin"))


        print("the game is initialised")
        # melange des cartes

    def take_card(self, from_deck: deck, player: players):
        """give a card from the deck to the player

        Args:
            deck (deck): the deck from which we take the card
            player (players): the player who will receive the card
        """
        if len(from_deck.values) > 0:
            card = from_deck.extract_first_elem()
            player.add_card_to_hand(card)
            print(f"the player {player.get_name} takes a card")
        else:
            print("there is no cards in deck.values")

    def get_players_by_name(self, player_name: str):
        """return the player with the given name

        Args:
            player_name (str): name of the player

        Returns:
            players: the player with the given name
        """
        for player in self.players:
            if player.get_name == player_name:
                return player
        print("there is no player with this name")


