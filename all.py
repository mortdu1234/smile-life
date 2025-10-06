from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from enum import Enum
import random
from pathlib import Path

# ===== ENUMS =====

class TypeCarte(Enum):
    ENFANT = "enfant"
    MARIAGE = "mariage"
    ADULTERE = "adultere"
    FLIRT = "flirt"
    ANIMAL = "animal"
    ETUDE = "etude"
    METIER = "metier"
    SALAIRE = "salaire"
    ACQUISITION = "acquisition"
    MALUS = "malus"
    LEGION = "legion"
    GRAND_PRIX = "grand_prix"
    SPECIALE = "speciale"

class StatutProfessionnel(Enum):
    RIEN = "rien"
    FONCTIONNAIRE = "fonctionnaire"
    INTERIMAIRE = "interimaire"

class TypeMalus(Enum):
    ACCIDENT = "accident"
    IMPOT = "impot"
    BURNOUT = "burnout"
    ATTENTAT = "attentat"
    DIVORCE = "divorce"
    LICENCIEMENT = "licenciement"
    PRISON = "prison"
    REDOUBLEMENT = "redoublement"
    MALADIE = "maladie"

# ===== GESTIONNAIRE DE RESSOURCES =====

class GestionnaireRessources:
    BASE_DIR = Path(__file__).parent / "ressources"
    
    CHEMINS_IMAGES = {
        TypeCarte.ENFANT: BASE_DIR / "personnal_life" / "childs",
        TypeCarte.MARIAGE: BASE_DIR / "personnal_life" / "mariages",
        TypeCarte.ADULTERE: BASE_DIR / "personnal_life",
        TypeCarte.FLIRT: BASE_DIR / "personnal_life" / "flirts",
        TypeCarte.ANIMAL: BASE_DIR / "animals",
        TypeCarte.ETUDE: BASE_DIR / "professionnal_life" / "StudyCards",
        TypeCarte.METIER: BASE_DIR / "professionnal_life" / "JobCards",
        TypeCarte.SALAIRE: BASE_DIR / "professionnal_life" / "SalaryCards",
        TypeCarte.ACQUISITION: BASE_DIR / "aquisition_cards",
        TypeCarte.MALUS: BASE_DIR / "attack_cards",
        TypeCarte.LEGION: BASE_DIR / "special_cards",
        TypeCarte.GRAND_PRIX: BASE_DIR / "special_cards",
        TypeCarte.SPECIALE: BASE_DIR / "special_cards",
    }
    
    @classmethod
    def obtenir_chemin_image(cls, carte: 'Carte') -> Optional[Path]:
        """Retourne le chemin vers l'image de la carte."""
        base_path = cls.CHEMINS_IMAGES.get(carte.type_carte)
        if not base_path:
            return None
        
        # Construction du nom de fichier selon le type de carte
        if carte.type_carte == TypeCarte.ENFANT:
            filename = f"{carte.nom_enfant}.png"
        
        elif carte.type_carte == TypeCarte.MARIAGE:
            filename = f"{carte.lieu}.png"
        
        elif carte.type_carte == TypeCarte.ADULTERE:
            filename = "adultere.png"
        
        elif carte.type_carte == TypeCarte.FLIRT:
            filename = f"{carte.lieu}.png"
        
        elif carte.type_carte == TypeCarte.ANIMAL:
            filename = f"{carte.type_animal.lower()}.png"
        
        elif carte.type_carte == TypeCarte.ETUDE:
            filename = "etude_double.png" if carte.double else "etude.png"
        
        elif carte.type_carte == TypeCarte.METIER:
            filename = f"{carte.nom_metier.lower().replace(' ', '_')}.png"
        
        elif carte.type_carte == TypeCarte.SALAIRE:
            filename = f"salaire_{carte.niveau}.png"
        
        elif carte.type_carte == TypeCarte.ACQUISITION:
            if "voyage" in carte.type_acquisition.lower():
                chemin = base_path / "trip" / f"voyage.png"
            else:
                chemin = base_path / "houses" / f"{carte.type_acquisition.lower().replace(' ', '_')}.png"
            return chemin if chemin.exists() else None
        
        elif carte.type_carte == TypeCarte.MALUS:
            filename = f"{carte.type_malus.value}.png"
        
        elif carte.type_carte == TypeCarte.LEGION:
            filename = "legion_honneur.png"
        
        elif carte.type_carte == TypeCarte.GRAND_PRIX:
            filename = "grand_prix_excellence.png"
        
        elif carte.type_carte == TypeCarte.SPECIALE:
            filename = f"{carte.nom.lower().replace(' ', '_').replace("'", '')}.png"
        
        else:
            return None
        
        chemin_complet = base_path / filename
        return chemin_complet if chemin_complet.exists() else None
    
    @classmethod
    def charger_image(cls, carte: 'Carte'):
        """Charge l'image de la carte (retourne le chemin ou None)."""
        return cls.obtenir_chemin_image(carte)

# ===== CLASSE CARTE ABSTRAITE =====

class Carte(ABC):
    def __init__(self, nom: str, type_carte: TypeCarte, smiles: int = 0):
        self.nom = nom
        self.type_carte = type_carte
        self.smiles = smiles
        self._chemin_image: Optional[Path] = None
    
    @property
    def chemin_image(self) -> Optional[Path]:
        """Retourne le chemin vers l'image de la carte."""
        if self._chemin_image is None:
            self._chemin_image = GestionnaireRessources.obtenir_chemin_image(self)
        return self._chemin_image
    
    @abstractmethod
    def peut_etre_posee(self, joueur: 'Joueur') -> bool:
        pass
    
    @abstractmethod
    def effet(self, joueur: 'Joueur', plateau: 'Plateau'):
        pass
    
    def __str__(self):
        return f"{self.nom} ({self.smiles} smiles)"

# ===== CARTES FAMILIALES =====

class CarteEnfant(Carte):
    def __init__(self, nom_enfant: str):
        super().__init__(nom_enfant, TypeCarte.ENFANT, smiles=2)
        self.nom_enfant = nom_enfant
    
    def peut_etre_posee(self, joueur: 'Joueur') -> bool:
        return joueur.marie and not joueur.a_divorce
    
    def effet(self, joueur: 'Joueur', plateau: 'Plateau'):
        joueur.enfants.append(self)

class CarteMariage(Carte):
    def __init__(self, lieu: str):
        multiplicateur = 3 if lieu == "Fourqueux" else 1
        super().__init__(f"Mariage à {lieu}", TypeCarte.MARIAGE, smiles=3*multiplicateur)
        self.lieu = lieu
    
    def peut_etre_posee(self, joueur: 'Joueur') -> bool:
        return joueur.nombre_flirts >= 1 and not joueur.marie
    
    def effet(self, joueur: 'Joueur', plateau: 'Plateau'):
        joueur.marie = True
        joueur.carte_mariage = self

class CarteAdultere(Carte):
    def __init__(self):
        super().__init__("Adultère", TypeCarte.ADULTERE, smiles=1)
    
    def peut_etre_posee(self, joueur: 'Joueur') -> bool:
        return joueur.marie
    
    def effet(self, joueur: 'Joueur', plateau: 'Plateau'):
        joueur.adultere = True

class CarteFlirt(Carte):
    LIEUX_AVEC_ENFANT = ["camping", "hotel"]
    
    def __init__(self, lieu: str):
        super().__init__(f"Flirt au {lieu}", TypeCarte.FLIRT, smiles=1)
        self.lieu = lieu
        self.permet_enfant = lieu in self.LIEUX_AVEC_ENFANT
    
    def peut_etre_posee(self, joueur: 'Joueur') -> bool:
        if joueur.marie and not joueur.adultere:
            return False
        if joueur.metier and joueur.metier.nom == "Barman":
            return not joueur.marie
        return joueur.nombre_flirts < 6
    
    def effet(self, joueur: 'Joueur', plateau: 'Plateau'):
        joueur.flirts.append(self)

class CarteAnimal(Carte):
    def __init__(self, type_animal: str, smiles: int):
        super().__init__(f"{type_animal}", TypeCarte.ANIMAL, smiles=smiles)
        self.type_animal = type_animal
    
    def peut_etre_posee(self, joueur: 'Joueur') -> bool:
        return True
    
    def effet(self, joueur: 'Joueur', plateau: 'Plateau'):
        joueur.animaux.append(self)
        # Bonus licorne si possède arc-en-ciel et étoile filante
        if self.type_animal == "Licorne":
            if joueur.a_carte_speciale("Arc-en-ciel") and joueur.a_carte_speciale("Étoile filante"):
                self.smiles = 6

# ===== CARTES TRAVAIL =====

class CarteEtude(Carte):
    def __init__(self, double: bool = False):
        nom = "Étude double" if double else "Étude"
        niveau = 2 if double else 1
        super().__init__(nom, TypeCarte.ETUDE, smiles=niveau)
        self.double = double
        self.niveau = niveau
    
    def peut_etre_posee(self, joueur: 'Joueur') -> bool:
        if joueur.metier:
            return joueur.metier.nom in ["Médecin", "Chirurgien"]
        return joueur.nombre_etudes < 6
    
    def effet(self, joueur: 'Joueur', plateau: 'Plateau'):
        joueur.etudes.append(self)

class CarteMetier(Carte):
    def __init__(self, nom_metier: str, niveau_requis: int, salaire_max: int, 
                 statut: StatutProfessionnel, pouvoir: Optional[str] = None):
        super().__init__(nom_metier, TypeCarte.METIER, smiles=2)
        self.nom_metier = nom_metier
        self.niveau_requis = niveau_requis
        self.salaire_max = salaire_max
        self.statut = statut
        self.pouvoir = pouvoir
    
    def peut_etre_posee(self, joueur: 'Joueur') -> bool:
        return joueur.nombre_etudes >= self.niveau_requis and not joueur.metier
    
    def effet(self, joueur: 'Joueur', plateau: 'Plateau'):
        joueur.metier = self
        joueur.statut_professionnel = self.statut

class CarteSalaire(Carte):
    def __init__(self, niveau: int):
        super().__init__(f"Salaire niveau {niveau}", TypeCarte.SALAIRE, smiles=niveau)
        self.niveau = niveau
        self.bloque = False
    
    def peut_etre_posee(self, joueur: 'Joueur') -> bool:
        if not joueur.metier:
            return False
        return self.niveau <= joueur.metier.salaire_max
    
    def effet(self, joueur: 'Joueur', plateau: 'Plateau'):
        joueur.salaires_disponibles.append(self)

class CarteAcquisition(Carte):
    def __init__(self, type_acq: str, cout: int, smiles: int):
        super().__init__(f"{type_acq}", TypeCarte.ACQUISITION, smiles=smiles)
        self.type_acquisition = type_acq
        self.cout = cout
    
    def peut_etre_posee(self, joueur: 'Joueur') -> bool:
        cout_reel = self.cout
        if "maison" in self.type_acquisition.lower() and joueur.marie:
            cout_reel = cout_reel // 2
        
        total_salaires = sum(s.niveau for s in joueur.salaires_disponibles)
        return total_salaires >= cout_reel
    
    def effet(self, joueur: 'Joueur', plateau: 'Plateau'):
        cout_reel = self.cout
        if "maison" in self.type_acquisition.lower() and joueur.marie:
            cout_reel = cout_reel // 2
        
        # Bloquer les salaires nécessaires
        salaires_a_bloquer = []
        total = 0
        for salaire in joueur.salaires_disponibles:
            if total < cout_reel:
                salaires_a_bloquer.append(salaire)
                total += salaire.niveau
        
        for salaire in salaires_a_bloquer:
            salaire.bloque = True
            joueur.salaires_disponibles.remove(salaire)
            joueur.salaires_bloques.append(salaire)
        
        joueur.acquisitions.append(self)

# ===== CARTES MALUS =====

class CarteMalus(Carte):
    def __init__(self, type_malus: TypeMalus):
        super().__init__(type_malus.value.capitalize(), TypeCarte.MALUS, smiles=0)
        self.type_malus = type_malus
    
    def peut_etre_posee(self, joueur: 'Joueur') -> bool:
        return True  # Peut toujours être jouée sur un adversaire
    
    def effet(self, joueur: 'Joueur', plateau: 'Plateau'):
        # À implémenter selon le type de malus
        if self.type_malus == TypeMalus.ACCIDENT:
            if not (joueur.metier and joueur.metier.nom == "Garagiste"):
                joueur.tours_a_passer = 1
        
        elif self.type_malus == TypeMalus.IMPOT:
            if joueur.metier and not (joueur.metier.nom == "Bandit"):
                if joueur.salaires_disponibles:
                    joueur.salaires_disponibles.pop()
        
        elif self.type_malus == TypeMalus.BURNOUT:
            if joueur.metier:
                joueur.tours_a_passer = 1
        
        elif self.type_malus == TypeMalus.ATTENTAT:
            if not (joueur.metier and joueur.metier.nom == "Militaire"):
                joueur.enfants.clear()
        
        elif self.type_malus == TypeMalus.DIVORCE:
            if joueur.marie and not (joueur.metier and joueur.metier.nom == "Avocat"):
                joueur.marie = False
                joueur.a_divorce = True
                joueur.enfants.clear()
                joueur.carte_mariage = None
        
        elif self.type_malus == TypeMalus.LICENCIEMENT:
            if joueur.metier and joueur.statut_professionnel != StatutProfessionnel.FONCTIONNAIRE:
                if joueur.metier.nom != "Bandit":
                    joueur.metier = None
                    joueur.statut_professionnel = StatutProfessionnel.RIEN
        
        elif self.type_malus == TypeMalus.PRISON:
            if joueur.metier and joueur.metier.nom == "Bandit":
                joueur.tours_a_passer = 3
        
        elif self.type_malus == TypeMalus.REDOUBLEMENT:
            if not joueur.metier and joueur.etudes:
                joueur.etudes.pop()
        
        elif self.type_malus == TypeMalus.MALADIE:
            immunise = False
            if joueur.metier and joueur.metier.nom in ["Médecin", "Chirurgien", "Pharmacien"]:
                immunise = True
            if not immunise:
                joueur.tours_a_passer = 1

# ===== CARTES AUTRES =====

class CarteLegion(Carte):
    def __init__(self):
        super().__init__("Légion d'honneur", TypeCarte.LEGION, smiles=3)
    
    def peut_etre_posee(self, joueur: 'Joueur') -> bool:
        return not joueur.a_ete_bandit
    
    def effet(self, joueur: 'Joueur', plateau: 'Plateau'):
        pass  # Juste des points

class CarteGrandPrix(Carte):
    def __init__(self):
        super().__init__("Grand prix d'excellence", TypeCarte.GRAND_PRIX, smiles=4)
    
    def peut_etre_posee(self, joueur: 'Joueur') -> bool:
        if not joueur.metier:
            return False
        return joueur.metier.nom in ["Journaliste", "Écrivain", "Chercheur"]
    
    def effet(self, joueur: 'Joueur', plateau: 'Plateau'):
        pass  # Juste des points

# ===== CARTES SPÉCIALES =====

class CarteSpeciale(Carte):
    def __init__(self, nom: str, effet_special: str):
        super().__init__(nom, TypeCarte.SPECIALE, smiles=0)
        self.effet_special = effet_special
    
    def peut_etre_posee(self, joueur: 'Joueur') -> bool:
        return True
    
    def effet(self, joueur: 'Joueur', plateau: 'Plateau'):
        # Les effets spéciaux sont gérés dans le plateau
        pass

# ===== CLASSE JOUEUR =====

class Joueur:
    def __init__(self, nom: str):
        self.nom = nom
        self.main: List[Carte] = []
        
        # Cartes posées
        self.enfants: List[CarteEnfant] = []
        self.flirts: List[CarteFlirt] = []
        self.etudes: List[CarteEtude] = []
        self.animaux: List[CarteAnimal] = []
        self.acquisitions: List[CarteAcquisition] = []
        self.salaires_disponibles: List[CarteSalaire] = []
        self.salaires_bloques: List[CarteSalaire] = []
        
        # États
        self.marie = False
        self.a_divorce = False
        self.adultere = False
        self.carte_mariage: Optional[CarteMariage] = None
        self.metier: Optional[CarteMetier] = None
        self.statut_professionnel = StatutProfessionnel.RIEN
        self.tours_a_passer = 0
        self.a_ete_bandit = False
        self.cartes_speciales_posees: List[CarteSpeciale] = []
        self.heritage_salaires = 0  # Pour la carte Héritage
    
    @property
    def nombre_flirts(self) -> int:
        return len(self.flirts)
    
    @property
    def nombre_etudes(self) -> int:
        return sum(etude.niveau for etude in self.etudes)
    
    def calculer_smiles(self) -> int:
        total = 0
        total += sum(e.smiles for e in self.enfants)
        total += sum(f.smiles for f in self.flirts)
        total += sum(e.smiles for e in self.etudes)
        total += sum(a.smiles for a in self.animaux)
        total += sum(acq.smiles for acq in self.acquisitions)
        total += sum(s.smiles for s in self.salaires_disponibles + self.salaires_bloques)
        
        if self.carte_mariage:
            total += self.carte_mariage.smiles
        if self.adultere:
            total += 1
        if self.metier:
            total += self.metier.smiles
        
        return total
    
    def peut_jouer(self) -> bool:
        if self.tours_a_passer > 0:
            self.tours_a_passer -= 1
            return False
        return True
    
    def piocher(self, carte: Carte):
        self.main.append(carte)
    
    def a_carte_speciale(self, nom: str) -> bool:
        return any(c.nom == nom for c in self.cartes_speciales_posees)
    
    def __str__(self):
        return f"{self.nom} ({self.calculer_smiles()} smiles)"

# ===== CLASSE PIOCHE =====

class Pioche:
    def __init__(self, cartes: List[Carte]):
        self.cartes = cartes
        self.defausse: List[Carte] = []
        self.melanger()
    
    def melanger(self):
        random.shuffle(self.cartes)
    
    def piocher_carte(self) -> Optional[Carte]:
        if self.est_vide():
            return None
        return self.cartes.pop()
    
    def defausser(self, carte: Carte):
        self.defausse.append(carte)
    
    def est_vide(self) -> bool:
        return len(self.cartes) == 0
    
    def voir_defausse(self) -> Optional[Carte]:
        return self.defausse[-1] if self.defausse else None

# ===== CLASSE CASINO =====

class Casino:
    def __init__(self):
        self.actif = False
        self.mises: Dict[Joueur, CarteSalaire] = {}
    
    def ouvrir(self):
        self.actif = True
        self.mises.clear()
    
    def miser(self, joueur: Joueur, salaire: CarteSalaire):
        self.mises[joueur] = salaire
    
    def resoudre_mise(self) -> Optional[Joueur]:
        if len(self.mises) < 2:
            return None
        
        joueurs = list(self.mises.keys())
        j1, j2 = joueurs[0], joueurs[1]
        s1, s2 = self.mises[j1], self.mises[j2]
        
        if s1.niveau == s2.niveau:
            gagnant = j2
        else:
            gagnant = j1
        
        # Le gagnant récupère les deux salaires
        gagnant.salaires_disponibles.append(s1)
        gagnant.salaires_disponibles.append(s2)
        
        self.mises.clear()
        self.actif = False
        
        return gagnant

# ===== CLASSE PLATEAU =====

class Plateau:
    def __init__(self, joueurs: List[Joueur], pioche: Pioche):
        self.joueurs = joueurs
        self.pioche = pioche
        self.tour_actuel = 0
        self.casino = Casino()
        self.joueur_actuel_index = 0
    
    def joueur_actuel(self) -> Joueur:
        return self.joueurs[self.joueur_actuel_index]
    
    def joueur_suivant(self):
        self.joueur_actuel_index = (self.joueur_actuel_index + 1) % len(self.joueurs)
        self.tour_actuel += 1
    
    def initialiser_partie(self):
        # Distribuer 5 cartes à chaque joueur
        for joueur in self.joueurs:
            for _ in range(5):
                carte = self.pioche.piocher_carte()
                if carte:
                    joueur.piocher(carte)
    
    def verifier_fin_partie(self) -> bool:
        return self.pioche.est_vide()
    
    def calculer_scores(self) -> Dict[Joueur, int]:
        return {joueur: joueur.calculer_smiles() for joueur in self.joueurs}
    
    def determiner_gagnant(self) -> Joueur:
        scores = self.calculer_scores()
        return max(scores, key=scores.get)

# ===== CLASSE FABRIQUE DE CARTES =====

class FabriqueCartes:
    @staticmethod
    def creer_deck_complet() -> List[Carte]:
        deck = []
        
        # Enfants (10)
        noms_enfants = ["diana", "harry", "hermione", "lara", "leia", 
                        "luigi", "luke", "mario", "rocky", "zelda"]
        for nom in noms_enfants:
            deck.append(CarteEnfant(nom))
        
        # Études (22 simples + 3 doubles)
        for _ in range(22):
            deck.append(CarteEtude(double=False))
        for _ in range(3):
            deck.append(CarteEtude(double=True))
        
        # Salaires (10 de chaque niveau)
        for niveau in range(1, 5):
            for _ in range(10):
                deck.append(CarteSalaire(niveau))
        
        # Flirts (20 dans 10 lieux)
        lieux_flirt = ["bar", "boite de nuit", "camping", "cinema", "hotel", 
                       "internet", "parc", "restaurant", "theatre", "zoo"]
        for _ in range(2):
            for lieu in lieux_flirt:
                deck.append(CarteFlirt(lieu))
        
        # Mariages (7)
        lieux_mariage = ["corps-nuds", "montcuq", "monteton", "Sainte-Vierge"] + ["Fourqueux"] * 3
        for lieu in lieux_mariage:
            deck.append(CarteMariage(lieu))
        
        # Adultères (3)
        for _ in range(3):
            deck.append(CarteAdultere())
        
        # Animaux (5 uniques)
        deck.append(CarteAnimal("Chat", 1))
        deck.append(CarteAnimal("Chien", 1))
        deck.append(CarteAnimal("Lapin", 1))
        deck.append(CarteAnimal("Poussin", 1))
        deck.append(CarteAnimal("Licorne", 3))
        
        # Acquisitions
        deck.append(CarteAcquisition("Petite maison", 6, 1))
        deck.append(CarteAcquisition("Petite maison", 6, 1))
        deck.append(CarteAcquisition("Moyenne maison", 8, 2))
        deck.append(CarteAcquisition("Moyenne maison", 8, 2))
        deck.append(CarteAcquisition("Grande maison", 10, 3))
        
        for _ in range(5):
            deck.append(CarteAcquisition("Voyage", 3, 1))
        
        # Malus (5 de chaque sauf Prison et Attentat)
        for _ in range(5):
            deck.append(CarteMalus(TypeMalus.ACCIDENT))
            deck.append(CarteMalus(TypeMalus.BURNOUT))
            deck.append(CarteMalus(TypeMalus.DIVORCE))
            deck.append(CarteMalus(TypeMalus.IMPOT))
            deck.append(CarteMalus(TypeMalus.LICENCIEMENT))
            deck.append(CarteMalus(TypeMalus.MALADIE))
            deck.append(CarteMalus(TypeMalus.REDOUBLEMENT))
        
        deck.append(CarteMalus(TypeMalus.PRISON))
        deck.append(CarteMalus(TypeMalus.ATTENTAT))
        
        # Autres
        deck.append(CarteLegion())
        deck.append(CarteGrandPrix())
        deck.append(CarteGrandPrix())
        
        # Cartes spéciales (1 de chaque)
        speciales = ["Anniversaire", "Arc-en-ciel", "Casino", "Chance", 
                     "Étoile filante", "Héritage", "Piston", "Troc", 
                     "Tsunami", "Vengeance"]
        for nom in speciales:
            deck.append(CarteSpeciale(nom, nom.lower()))
        
        # Métiers - À compléter avec tous les métiers
        deck.append(CarteMetier("Architecte", 4, 3, StatutProfessionnel.RIEN, "architecte"))
        deck.append(CarteMetier("Astronaute", 6, 4, StatutProfessionnel.RIEN, "astronaute"))
        deck.append(CarteMetier("Avocat", 4, 3, StatutProfessionnel.RIEN, "avocat"))
        deck.append(CarteMetier("Bandit", 0, 4, StatutProfessionnel.RIEN, "bandit"))
        deck.append(CarteMetier("Barman", 0, 1, StatutProfessionnel.INTERIMAIRE, "barman"))
        # ... (ajouter tous les autres métiers)
        
        return deck

# ===== CLASSE JEU PRINCIPALE =====

class Jeu:
    def __init__(self, noms_joueurs: List[str]):
        self.joueurs = [Joueur(nom) for nom in noms_joueurs]
        deck = FabriqueCartes.creer_deck_complet()
        self.pioche = Pioche(deck)
        self.plateau = Plateau(self.joueurs, self.pioche)
    
    def demarrer(self):
        self.plateau.initialiser_partie()
        print("=== Partie de Smiles ===")
        print(f"{len(self.joueurs)} joueurs: {', '.join(j.nom for j in self.joueurs)}")
        print()
    
    def tour_joueur(self, joueur: Joueur):
        if not joueur.peut_jouer():
            print(f"{joueur.nom} passe son tour.")
            return
        
        print(f"\n--- Tour de {joueur.nom} ---")
        print(f"Main: {', '.join(str(c) for c in joueur.main)}")
        print(f"Smiles actuels: {joueur.calculer_smiles()}")
        # Logique du tour à implémenter
    
    def jouer(self):
        self.demarrer()
        
        while not self.plateau.verifier_fin_partie():
            joueur = self.plateau.joueur_actuel()
            self.tour_joueur(joueur)
            self.plateau.joueur_suivant()
        
        # Fin de partie
        print("\n=== FIN DE PARTIE ===")
        scores = self.plateau.calculer_scores()
        for joueur, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
            print(f"{joueur.nom}: {score} smiles")
        
        gagnant = self.plateau.determiner_gagnant()
        print(f"\n🎉 {gagnant.nom} remporte la partie !")


# ===== EXEMPLE D'UTILISATION =====
if __name__ == "__main__":
    jeu = Jeu(["Alice", "Bob", "Charlie"])
    # jeu.jouer()  # Décommenter pour lancer une partie
    print("Classes créées avec succès!")
    
    # Test d'accès aux images
    print("\n=== Test d'accès aux images ===")
    test_cartes = [
        CarteEnfant("harry"),
        CarteFlirt("bar"),
        CarteMariage("montcuq"),
        CarteMetier("Architecte", 4, 3, StatutProfessionnel.RIEN),
        CarteSalaire(3),
        CarteAnimal("Chat", 1),
        CarteMalus(TypeMalus.ACCIDENT)
    ]
    
    for carte in test_cartes:
        chemin = carte.chemin_image
        existe = chemin.exists() if chemin else False
        print(f"{carte.nom}: {chemin} {'✓' if existe else '✗'}")