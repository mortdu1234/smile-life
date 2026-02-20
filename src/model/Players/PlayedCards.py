from src.model.Card import Card

class PlayedCards:
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.cards: list[Card] = []