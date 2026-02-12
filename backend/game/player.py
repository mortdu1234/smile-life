from uuid import UUID
from ..cards import Card 

class Player:
    def __init__(self, player_id: 'UUID', player_name: str):
        self.player_id: 'UUID' = player_id      # Unique identifier for the player
        self.player_name: str = player_name     # Name of the player
        self.hand: 'list[Card]' = []            # Cards in the player's hand
        
        # cartes jouées
        self.played_vie_pro: 'list[Card]' = []   # Cartes Vie Professionnelles
        self.played_vie_perso: 'list[Card]'= []  # Cartes Vie Personnelles
        self.played_aquisitions: 'list[Card]' = []  # Cartes Acquisitions
        self.played_salaires_depenses: 'list[Card]' = []  # Cartes Salaires et Dépenses
        self.played_cartes_speciales: 'list[Card]' = []  # Cartes Spéciales
        self.played_effets_permanents: 'list[Card]' = []  # Cartes Effets Permanents

    def play_card(self, card: 'Card'):
        """Place la carte jouée dans la bonne liste"""
        pass

    # GESTION DE LA MAIN
    def add_card_to_hand(self, card: 'Card'):
        """Ajoute une carte à la main du joueur"""
        self.hand.append(card)
    
    def remove_card_from_hand(self, card: 'Card'):
        """Retire une carte de la main du joueur"""
        self.hand.remove(card)

    def get_card_by_id_in_hand(self, card_id: UUID) -> 'Card | None':
        """Retourne la carte si elle est dans la main du joueur, sinon None"""
        for c in self.hand:
            if c.get_card_id() == card_id:
                return c
        return None
    
    
