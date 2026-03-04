from uuid import UUID, uuid4
from src.model.Card import Card
from src.model.Players.PlayedCards import PlayedCards
from src.model.Players.PermanentEffects import PermanentEffects

class Player:
    def __init__(self, name: str):
        self.name: str = name
        self.playerID: UUID = uuid4()
        self.hand: list[Card] = []
        self.vieProfessionnelle: PlayedCards = PlayedCards("vie professionnelle")
        self.viePersonnelle: PlayedCards = PlayedCards("vie personnelle")
        self.acquisitions: PlayedCards = PlayedCards("acquisitions")
        self.salairesDepenses: PlayedCards = PlayedCards("salaires dépensés")
        self.specialCards: PlayedCards = PlayedCards("cartes spéciales")
        self.permanentEffects: list[PermanentEffects] = []

    def getName(self) -> str:
        return self.name
    def getPlayerID(self) -> UUID:
        return self.playerID
    def getHand(self) -> list[Card]:
        return self.hand
    def getVieProfessionnelle(self) -> PlayedCards:
        return self.vieProfessionnelle
    def getViePersonnelle(self) -> PlayedCards:
        return self.viePersonnelle
    def getAcquisitions(self) -> PlayedCards:
        return self.acquisitions
    def getSalairesDepenses(self) -> PlayedCards:
        return self.salairesDepenses
    def getSpecialCards(self) -> PlayedCards:
        return self.specialCards
    def getPermanentEffects(self) -> list[PermanentEffects]:
        return self.permanentEffects
    

    def addcardToHand(self, card: Card):
        self.hand.append(card)
    
    def playCard(self, card: Card, target: 'Player'):
        print("fonction playCard à implémenter")
        pass

    def getJob(self):
        