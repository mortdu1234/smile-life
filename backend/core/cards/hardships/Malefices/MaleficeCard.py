from backend.core.cards.hardships.HardshipCard import Hardship


class MaleficeCard(Hardship):
    
    def get_card_rule(self) -> str:
        return """applique un effet (souvent permanent) a un adversaire"""+ "\n"+ "="*10+ "\n" + super().get_card_rule()