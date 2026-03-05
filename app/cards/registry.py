"""
Registre des cartes — mapping id (str) → classe concrète.

Pour ajouter une nouvelle carte :
1. Créer la classe dans cards/concrete/...
2. L'enregistrer ici
3. Ajouter l'entrée dans data/cards.json
"""
from app.cards.concrete.personal.flirt import FlirtCard, FlirtWithChildCard, MarriageCard, AdulteryCard
from app.cards.concrete.personal.children import (
    ChildCard, AngelaChild, BeatrixChild, DaenerysChild, DianaChild,
    HarryChild, HermioneChild, LaraChild, LeiaChild, LouiseChild,
    LuigiChild, MarioChild, LukeChild, OlympeChild, RockyChild,
    SimoneChild, ZeldaChild,
)
from app.cards.concrete.professional.study_salary import StudyCard, SalaryCard
from app.cards.concrete.professional.job import (
    JobCard, AstronauteJob, BanditJob, MediumJob, JournalisteJob,
    ChefDesAchatsJob, ArchitecteJob, InfirmierJob, ChirurgienJob,
    DesignerJob, GaragisteJob, JardinierJob, MedecinJob, MilitaireJob,
    PharmacienJob, PiloteDeLigneJob, PizzaioloJob, PlombierJob,
    ServeurJob, StripTeaserJob, EcrivainJob, YoutuberJob, CoiffeurJob, DeejayJob,
)
from app.cards.concrete.acquisitions.cards import (
    AquisitionCard, HouseCard, TravelCard, ConcertTicket, SabreCard, NounouCard,
)
from app.cards.concrete.animals.cards import AnimalCard, LicorneAnimal, DragonAnimal
from app.cards.concrete.hardship.cards import (
    AccidentCard, MaladieCard, TaxCard, BurnOutCard, DivorceCard,
    LicenciementCard, RedoublementCard, PrisonCard, AttentatCard,
    ChargeMentalHardhip, GynocratieHardship, PhalocratieHardship,
    PlafondDeVerreHardship, PorcHardship,
)
from app.cards.concrete.special.cards import (
    EgaliteDesSalaireCard, ClicheAccident, ClicheFlirt, ClicheMetier,
    GirlPowerCard, RedistributionDesTachesCard, SoireeEntreFilleCard,
    CoupDeFoudreCard, ErreurDetiquetageCard, TsunamiCard, HeritageCard,
    PistonCard, VengeanceCard, ChanceCard, EtoileFilanteCard,
    CasinoCard, AnniversaireCard, ArcEnCielCard, MuguetCard,
)
from app.cards.concrete.other.cards import OtherCard, LegionCard, PriceCard

# ---------------------------------------------------------------------------
# Registre principal : card_id → classe concrète
# ---------------------------------------------------------------------------
CARD_REGISTRY: dict[str, type] = {
    # Vie personnelle
    "flirt":                FlirtCard,
    "flirt_with_child":     FlirtWithChildCard,
    "marriage":             MarriageCard,
    "adultery":             AdulteryCard,

    # Enfants
    "child":                ChildCard,
    "angela":               AngelaChild,
    "beatrix":              BeatrixChild,
    "daenerys":             DaenerysChild,
    "diana":                DianaChild,
    "harry":                HarryChild,
    "hermione":             HermioneChild,
    "lara":                 LaraChild,
    "leia":                 LeiaChild,
    "louise":               LouiseChild,
    "luigi":                LuigiChild,
    "mario":                MarioChild,
    "luke":                 LukeChild,
    "olympe":               OlympeChild,
    "rocky":                RockyChild,
    "simone":               SimoneChild,
    "zelda":                ZeldaChild,

    # Vie professionnelle
    "study":                StudyCard,
    "salary":               SalaryCard,
    "job":                  JobCard,
    "astronaute":           AstronauteJob,
    "bandit":               BanditJob,
    "medium":               MediumJob,
    "journaliste":          JournalisteJob,
    "chef_achats":          ChefDesAchatsJob,
    "architecte":           ArchitecteJob,
    "infirmier":            InfirmierJob,
    "chirurgien":           ChirurgienJob,
    "designer":             DesignerJob,
    "garagiste":            GaragisteJob,
    "jardinier":            JardinierJob,
    "medecin":              MedecinJob,
    "militaire":            MilitaireJob,
    "pharmacien":           PharmacienJob,
    "pilote":               PiloteDeLigneJob,
    "pizzaiolo":            PizzaioloJob,
    "plombier":             PlombierJob,
    "serveur":              ServeurJob,
    "stripteaser":          StripTeaserJob,
    "ecrivain":             EcrivainJob,
    "youtubeur":            YoutuberJob,
    "coiffeur":             CoiffeurJob,
    "deejay":               DeejayJob,

    # Acquisitions
    "acquisition":          AquisitionCard,
    "house":                HouseCard,
    "travel":               TravelCard,
    "concert":              ConcertTicket,
    "sabre":                SabreCard,
    "nounou":               NounouCard,

    # Animaux
    "animal":               AnimalCard,
    "licorne":              LicorneAnimal,
    "dragon":               DragonAnimal,

    # Coups durs
    "accident":             AccidentCard,
    "maladie":              MaladieCard,
    "tax":                  TaxCard,
    "burnout":              BurnOutCard,
    "divorce":              DivorceCard,
    "licenciement":         LicenciementCard,
    "redoublement":         RedoublementCard,
    "prison":               PrisonCard,
    "attentat":             AttentatCard,
    "charge_mental":        ChargeMentalHardhip,
    "gynocratie":           GynocratieHardship,
    "phalocratie":          PhalocratieHardship,
    "plafond_verre":        PlafondDeVerreHardship,
    "porc":                 PorcHardship,

    # Spéciales
    "egalite_salaire":          EgaliteDesSalaireCard,
    "cliche_accident":          ClicheAccident,
    "cliche_flirt":             ClicheFlirt,
    "cliche_metier":            ClicheMetier,
    "girl_power":               GirlPowerCard,
    "redistribution_taches":    RedistributionDesTachesCard,
    "soiree_entre_fille":       SoireeEntreFilleCard,
    "coup_de_foudre":           CoupDeFoudreCard,
    "erreur_etiquetage":        ErreurDetiquetageCard,
    "tsunami":                  TsunamiCard,
    "heritage":                 HeritageCard,
    "piston":                   PistonCard,
    "vengeance":                VengeanceCard,
    "chance":                   ChanceCard,
    "etoile_filante":           EtoileFilanteCard,
    "casino":                   CasinoCard,
    "anniversaire":             AnniversaireCard,
    "arc_en_ciel":              ArcEnCielCard,
    "muguet":                   MuguetCard,

    # Autres
    "legion":               LegionCard,
    "prix":                 PriceCard,
}


def get_card_class(card_id: str) -> type | None:
    """Retourne la classe concrète correspondant à l'identifiant."""
    return CARD_REGISTRY.get(card_id)
