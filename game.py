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

        # etudes
        self.deck.add_a_card(StudyCards(1, 1, "study1"))
        self.deck.add_a_card(StudyCards(2, 1, "study2"))
        
        # legion d'honneur
        self.deck.add_a_card(ProfessionnalLifeCards(3, "legion"))

        # prix d'exelence
        self.deck.add_a_card(ProfessionnalLifeCards(4, "price"))
        
        # metiers
        self.deck.add_a_card(JobCards(False, True, 0, 1, 2, "serveur"))
        self.deck.add_a_card(JobCards(False, True, 0, 1, 2, "barman"))
        self.deck.add_a_card(JobCards(True, False, 0, 1, 2, "militaire"))
        self.deck.add_a_card(JobCards(False, True, 0, 1, 2, "stripteaser"))
        self.deck.add_a_card(JobCards(False, False, 0, 1, 2, "ecrivain"))
        self.deck.add_a_card(JobCards(False, False, 0, 1, 2, "medium"))
        self.deck.add_a_card(JobCards(False, False, 1, 1, 2, "jardinier"))
        self.deck.add_a_card(JobCards(False, False, 0, 2, 2, "pizzaiolo"))
        self.deck.add_a_card(JobCards(False, False, 0, 3, 2, "gourou"))
        self.deck.add_a_card(JobCards(False, False, 0, 4, 2, "bandit"))
        self.deck.add_a_card(JobCards(False, True, 1, 1, 2, "plombier"))
        self.deck.add_a_card(JobCards(False, False, 1, 2, 2, "garagiste"))
        self.deck.add_a_card(JobCards(True, False, 1, 1, 2, "policier"))
        self.deck.add_a_card(JobCards(True, False, 2, 2, 2, "prof_anglais"))
        self.deck.add_a_card(JobCards(True, False, 2, 2, 2, "prof_francais"))
        self.deck.add_a_card(JobCards(True, False, 2, 2, 2, "prof_histoire"))
        self.deck.add_a_card(JobCards(True, False, 2, 2, 2, "prof_maths"))
        self.deck.add_a_card(JobCards(True, False, 0, 3, 2, "grand_prof"))
        self.deck.add_a_card(JobCards(False, False, 3, 2, 2, "journaliste"))
        self.deck.add_a_card(JobCards(False, False, 3, 3, 2, "chef_des_achats"))
        self.deck.add_a_card(JobCards(False, False, 3, 3, 2, "chef_des_ventes"))
        self.deck.add_a_card(JobCards(False, False, 4, 3, 2, "designer"))
        self.deck.add_a_card(JobCards(False, False, 4, 3, 2, "architecte"))
        self.deck.add_a_card(JobCards(False, False, 4, 3, 2, "avocat"))
        self.deck.add_a_card(JobCards(False, False, 5, 3, 2, "pharmacien"))
        self.deck.add_a_card(JobCards(False, False, 5, 4, 2, "pilote_de_ligne"))
        self.deck.add_a_card(JobCards(False, False, 6, 2, 2, "chercheur"))
        self.deck.add_a_card(JobCards(False, False, 6, 4, 2, "medecin"))
        self.deck.add_a_card(JobCards(False, False, 6, 4, 2, "chirurgien"))
        self.deck.add_a_card(JobCards(False, False, 6, 4, 2, "astronaute"))
        
        # salaires
        self.deck.add_a_card(SalaryCards(1, 1, "salary1"))
        self.deck.add_a_card(SalaryCards(2, 1, "salary2"))
        self.deck.add_a_card(SalaryCards(3, 1, "salary3"))
        self.deck.add_a_card(SalaryCards(4, 1, "salary4"))
        
        # voyages
        self.deck.add_a_card(TripCards(3, 1, "londres"))
        self.deck.add_a_card(TripCards(3, 1, "new_york"))
        self.deck.add_a_card(TripCards(3, 1, "rio"))
        self.deck.add_a_card(TripCards(3, 1, "sydney"))
        self.deck.add_a_card(TripCards(3, 1, "le_caire"))

        # maisons
        self.deck.add_a_card(HouseCards(6, 1, "maison1"))
        self.deck.add_a_card(HouseCards(8, 2, "maison2"))
        self.deck.add_a_card(HouseCards(10, 3, "maison3"))
        
        # animaux
        self.deck.add_a_card(Animal(0, 1, "chat"))
        self.deck.add_a_card(Animal(0, 1, "chien"))
        self.deck.add_a_card(Animal(0, 1, "lapin"))
        self.deck.add_a_card(Animal(0, 3, "licorne"))
        self.deck.add_a_card(Animal(0, 1, "poussin"))

        # flirts
        self.deck.add_a_card(FlirtCards(False, 1, "parc"))
        self.deck.add_a_card(FlirtCards(False, 1, "bar"))
        self.deck.add_a_card(FlirtCards(False, 1, "theatre"))
        self.deck.add_a_card(FlirtCards(False, 1, "cinema"))
        self.deck.add_a_card(FlirtCards(False, 1, "boite_de_nuit"))
        self.deck.add_a_card(FlirtCards(True, 1, "camping"))
        self.deck.add_a_card(FlirtCards(True, 1, "hotel"))
        self.deck.add_a_card(FlirtCards(False, 1, "restaurant"))
        self.deck.add_a_card(FlirtCards(False, 1, "zoo"))
        self.deck.add_a_card(FlirtCards(False, 1, "internet"))

        # mariages
        self.deck.add_a_card(MariageCard(3, "mariage"))

        # adulteres
        self.deck.add_a_card(MariageCard(1, "adultere"))

        # enfants
        self.deck.add_a_card(ChildCard(2, "leia"))
        self.deck.add_a_card(ChildCard(2, "hermione"))
        self.deck.add_a_card(ChildCard(2, "lara"))
        self.deck.add_a_card(ChildCard(2, "luke"))
        self.deck.add_a_card(ChildCard(2, "diana"))
        self.deck.add_a_card(ChildCard(2, "mario"))
        self.deck.add_a_card(ChildCard(2, "zelda"))
        self.deck.add_a_card(ChildCard(2, "luigi"))
        self.deck.add_a_card(ChildCard(2, "harry"))
        self.deck.add_a_card(ChildCard(2, "rocky"))

        # cartes spéciales
        self.deck.add_a_card(SpecialCards(0, "casino"))
        self.deck.add_a_card(SpecialCards(0, "troc"))
        self.deck.add_a_card(SpecialCards(0, "heritage"))
        self.deck.add_a_card(SpecialCards(0, "chance"))
        self.deck.add_a_card(SpecialCards(0, "arc_en_ciel"))
        self.deck.add_a_card(SpecialCards(0, "anniversaire"))
        self.deck.add_a_card(SpecialCards(0, "piston"))
        self.deck.add_a_card(SpecialCards(0, "vengeance"))
        self.deck.add_a_card(SpecialCards(0, "etoile_filante"))
        self.deck.add_a_card(SpecialCards(0, "tsunami"))

        # cartes d'attaque
        self.deck.add_a_card(AttackCards(0, "maladie"))
        self.deck.add_a_card(AttackCards(0, "burn_out"))
        self.deck.add_a_card(AttackCards(0, "impot"))
        self.deck.add_a_card(AttackCards(0, "attentat"))
        self.deck.add_a_card(AttackCards(0, "redoublement"))
        self.deck.add_a_card(AttackCards(0, "accident"))
        self.deck.add_a_card(AttackCards(0, "divorce"))
        self.deck.add_a_card(AttackCards(0, "licenciement"))
        self.deck.add_a_card(AttackCards(0, "prison"))
        


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
            print(f"the path of the card is {card.picture}")
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


