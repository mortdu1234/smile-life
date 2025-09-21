from cards import Cards

class players:
    def __init__(self, name: str):
        self.name: str = name
        self.hand: list[Cards] = []
        self.board: list[Cards] = []
    
    def add_card_to_board(self, card: Cards):
        """add a new card from the hand to the board

        Args:
            card (cards): the card to add on the board
        """
        if card in self.hand:
            self.hand.remove(card)
            self.board.append(card)
        else:
            print(f"Card {card} is not in hand.")  # ERROR

    def add_card_to_hand(self, card: Cards):
        self.hand.append(card)

    @property
    def get_name(self):
        return self.name