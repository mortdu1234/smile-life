from src.model.Card import Card

class PlayedCards:
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.cards: list[Card] = []

    def removeCard(self, card: Card):
        self.cards.remove(card)
    
    def addCard(self, card: Card):
        self.cards.append(card)
    
    def findCardByType(self, type: type) -> list[Card]:
        return [card for card in self.cards if isinstance(card, type)]