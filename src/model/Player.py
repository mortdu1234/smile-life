from uuid import UUID
from Card import Card
from Players.PlayedCards import PlayedCards

class Player:
    def __init__(self, name: str):
        self.name: str = name
        self.playerID: UUID = UUID()
        self.hand: list[Card] = []
        self.vieProfessionnelle: PlayedCards = PlayedCards("vie professionnelle")
        self.viePersonnelle: PlayedCards = PlayedCards("vie personnelle")
        self.acquisitions: PlayedCards = PlayedCards("acquisitions")
        self.salairesDepenses: PlayedCards = PlayedCards("salaires dépensés")
        self.specialCards: PlayedCards = PlayedCards("cartes spéciales")
        self.permanentEffects: PlayedCards = PlayedCards("effets permanents")

    
        