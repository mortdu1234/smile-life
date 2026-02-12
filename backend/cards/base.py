class Card:
    def __init__(self, card_id: 'UUID', name: str):
        self.card_id: 'UUID' = card_id
        self.name: str = name

    def get_card_id(self) -> 'UUID':
        return self.card_id