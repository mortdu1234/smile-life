# www.smilelife.fr/carteshop

class Cards:
    """ensemble des cartes"""
    def __init__(self, smile: int, picture: str):
        """
        Args:
            smile (int): nombre de smile apporté par la carte
            picture (str): nom de l'image
        """
        self.picture: str = f"ressources/{picture}.png"
        self.smile: int = smile

class SpecialCards(Cards):
    """enemble des cartes spéciales"""
    def __init__(self, smile: int, picture: str):
        """
        Args:
            smile (int): nombre de smile apporté par la carte
            picture (str): nom de l'image
        """
        super().__init__(smile, f"special_cards/{picture}")

class AttackCards(Cards):
    """ensemble des cartes d'attaques"""
    def __init__(self, smile: int, picture: str):
        """
        Args:
            smile (int): nombre de smile apporté par la carte
            picture (str): nom de l'image
        """
        super().__init__(smile, f"attack_cards/{picture}")

class AquisitionCards(Cards):
    """ensemble des cartes d'aquisition"""
    def __init__(self, price: int, smile: int, picture: str):
        """
        Args:
            price (int): prix de l'aquisition
            smile (int): nombre de smile apporté par la carte
            picture (str): nom de l'image
        """
        super().__init__(smile, f"aquisition_cards/{picture}")
        self.price: int = price

class PersonnalLifeCards(Cards):
    """ensemble des cartes en lien avec la vie personnelle"""
    def __init__(self, smile: int, picture: str):
        """
        Args:
            smile (int): nombre de smile apporté par la carte
            picture (str): nom de l'image
        """
        super().__init__(smile, f"personnal_life/{picture}")

class ProfessionnalLifeCards(Cards):
    """ensemble des cartes en lien avec la vie professionnelle"""
    def __init__(self, smile: int, picture: str):
        """
        Args:
            smile (int): nombre de smile apporté par la carte
            picture (str): nom de l'image
        """
        super().__init__(smile, f"professionnal_life/{picture}")

# =============================================================================
# PROFESSIONNAL LIFE CARDS
# =============================================================================

class StudyCards(ProfessionnalLifeCards):
    """ensemble des cartes d'études, simple et double"""
    def __init__(self, number:int, smile: int, picture: str):
        """
        Args:
            number (int): etude simple ou double
            smile (int): nombre de smile apporté par la carte
            picture (str): nom de l'image
        """
        super().__init__(smile, f"StudyCards/{picture}")
        if number not in [1, 2]:
            print("ERROR | StudyCards | trop de niveau d'etude ")
        else:
            self.number: int = number

class JobCards(ProfessionnalLifeCards):
    """ensemble des cartes métiers"""
    def __init__(self, official: bool, interrimere: bool, study_min:int, salary_max: int, smile: int, picture: str):
        """
        Args:
            official (bool): si c'est un fonctionnaire
            interrimere (bool): si c'est un interrimere
            study_min (int): nombre d'étude necessaire
            salary_max (int): gain de salaire maximum
            smile (int): nombre de smile apporté par la carte
            picture (str): nom de l'image
        """
        super().__init__(smile, f"JobCards/{picture}")
        self.official: bool= official
        self.interrimere: bool= interrimere
        if study_min not in [1, 2, 3, 4, 5, 6]:
            print("ERROR | JobCards | trop d'etude minimum ")
        else:
            self.study_min: int= study_min
        if salary_max not in [1, 2, 3, 4]:
            print("ERROR | JobCards | trop de gain de salaire max")
        else:
            self.salary_max: int= salary_max

class SalaryCards(ProfessionnalLifeCards):
    """ensemble des cartes salaires"""
    def __init__(self, number:int, smile: int, picture: str):
        """
        Args:
            number (int): nombre d'argent sur la carte
            smile (int): nombre de smile apporté par la carte
            picture (str): nom de l'image
        """
        super().__init__(smile, f"SalaryCards/{picture}")
        if number not in [1, 2, 3, 4]:
            print("ERROR | SalaryCards | pas de salaire possible")
        else:
            self.number: int = number

# =============================================================================
# AQUISITIONS CARDS
# =============================================================================

class TripCards(AquisitionCards):
    """ensemble des cartes de voyage"""
    def __init__(self, price: int, smile: int, picture: str):
        """
        Args:
            price (int): prix de l'aquisition
            smile (int): nombre de smile de la carte
            picture (str): nom de l'image
        """
        super().__init__(price, smile, f"trip/{picture}")

class HouseCards(AquisitionCards):
    """ensemble des cartes maison"""
    def __init__(self, price: int, smile: int, picture: str):
        """
        Args:
            price (int): prix de l'aquisition
            smile (int): nombre de smile de la carte
            picture (str): nom de l'image
        """
        super().__init__(price, smile, f"houses/{picture}")

class Animal(AquisitionCards):
    """ensemble des cartes d'animaux de compagnie"""
    def __init__(self, price: int, smile: int, picture: str):
        """
        Args:
            price (int): prix de l'aquisition
            smile (int): nombre de smile de la carte
            picture (str): nom de l'image
        """
        super().__init__(price, smile, f"animals/{picture}")

# =============================================================================
# PERSONNAL LIFE CARDS
# =============================================================================

class FlirtCards(PersonnalLifeCards):
    """ensemble des cartes flirts"""
    def __init__(self, have_child: bool, smile: int, picture: str):
        """
        Args:
            have_child (bool): si on peut avoir un enfant
            smile (int): nombre de smile de la carte
            picture (str): nom de l'image
        """
        super().__init__(smile, f"flirts/{picture}")
        self.have_child: bool= have_child

class MariageCard(PersonnalLifeCards):
    """ensemble des cartes mariage"""
    def __init__(self, smile: int, picture: str):
        """
        Args:
            smile (int): nombre de smile de la carte
            picture (str): nom de l'image
        """
        super().__init__(smile, f"mariages/{picture}")

class AdultaryCard(PersonnalLifeCards):
    """ensemble des cartes adultaire"""
    def __init__(self, smile: int, picture: str):
        """
        Args:
            smile (int): nombre de smile de la carte
            picture (str): nom de l'image
        """
        super().__init__(smile, f"mariages/{picture}")

class ChildCard(PersonnalLifeCards):
    """ensemble des enfants"""
    def __init__(self, smile: int, picture: str):
        """
        Args:
            smile (int): nombre de smile de la carte
            picture (str): nom de l'image
        """
        super().__init__(smile, f"childs/{picture}")


# =============================================================================
# SPECIAL CARDS
# =============================================================================




# =============================================================================
# ATTACKS CARDS
# =============================================================================

