from cards import Cards

class deck:
    def __init__(self):
        self.values: list[Cards] = []

    def get_first_elem(self):
        """return the first elem in the list

        Returns:
            cards: a card of the game
        """
        if len(self.values) > 0:
            return self.values[0]
        print("there is no cards in deck.values") # ERROR

    def add_a_card(self, card: Cards):
        """add a new card in the deck

        Args:
            card : the card to add
        """
        self.values.append(card)

    def extract_first_elem(self):
        """return the first elem in the list and remove it

        Returns:
            cards: a card of the game
        """
        if len(self.values) > 0:
            return self.values.pop(0)
        print("there is no cards in deck.values") # ERROR
        