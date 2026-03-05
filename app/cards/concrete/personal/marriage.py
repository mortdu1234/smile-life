"""Re-export de MarriageCard depuis flirt.py pour compatibilité des imports."""
from app.cards.concrete.personal.flirt import MarriageCard, AdulteryCard, FlirtCard, FlirtWithChildCard

__all__ = ["MarriageCard", "AdulteryCard", "FlirtCard", "FlirtWithChildCard"]
