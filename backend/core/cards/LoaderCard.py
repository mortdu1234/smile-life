"""
Registre des cartes : mappe les card_id du preset JSON vers les classes Card.
Ajoute ici chaque nouvelle carte ; le reste du code n'a pas à changer.
"""
from __future__ import annotations

from backend.core.cards.professionnals.NoPowerJob import Designer, Jardinier, Pizzaiolo
from backend.core.cards.professionnals.Policier import Policier
from backend.core.cards.professionnals.Prof import Prof
from backend.core.cards.professionnals.Stripteaser import Stripteaser
from .Card import Card

# Animals
from .animals.SimpleAnimalCard import (
    Chien,
    Chat,
    Crapaud,
    Lapin,
    Poussin,
)
from .animals.LicorneCard import LicorneAnimal

# Acquisitions
from .acquisitions.HouseAcquisition import House
from .acquisitions.TripAcquisition import Trip

# Hardships
from .hardships.AccidentHardship import Accident
from .hardships.MaladieHardship import Maladie
from .hardships.TaxHardship import Tax
from .hardships.BurnOutHardship import BurnOut
from .hardships.DivorceHardship import Divorce
from .hardships.LicenciementHardship import Licenciement
from .hardships.Redoublement import Redoublement
from .hardships.Prison import Prison
from .hardships.Attentat import Attentat

# Personnal life
from .personnals.Flirts import Flirt, FlirtWithChild
from .personnals.Wedding import Wedding, Adultery
from .personnals.Children import (
    AngelaChild,
    DianaChild,
    HarryChild,
    HermioneChild,
    LaraChild,
    LeiaChild,
    LouiseChild,
    LuigiChild,
    MarioChild,
    LukeChild,
    OlympeChild,
    RockyChild,
    SimoneChild,
    ZeldaChild,
)

# Professionnals
from .professionnals.SalaryCard import SalaryCard
from .professionnals.StudyCard import StudyCard

from .professionnals.Serveur import Serveur
from .professionnals.Garagiste import Garagiste
from .professionnals.Plombier import Plombier
from .professionnals.Bandit import Bandit
from .professionnals.Ecrivain import Ecrivain
from .professionnals.Pharmacien import Pharmacien
from .professionnals.Architect import Architect
from .professionnals.Militaire import Militaire
from .professionnals.Medium import Medium
from .professionnals.Journaliste import Journaliste
from .professionnals.ChefDesAchats import ChefDesAchats
from .professionnals.Medecin import Medecin
from .professionnals.Chirurgien import Chirurgien
from .professionnals.PiloteDeLigne import PiloteDeLigne
from .professionnals.Astronaute import Astronaute
from .professionnals.Avocat import Avocat
from .professionnals.Barman import Barman
from .professionnals.ChefDesVentes import ChefDesVentes
from .professionnals.Chercheur import Chercheur
from .professionnals.Gourou import Gourou
from .professionnals.Grandprof import Grandprof

# Other
from .other.Legion import Legion
from .other.Price import Price

# Specials
from .specials.Casino import Casino
from .specials.ArcEnCiel import ArcEnCiel
from .specials.Chance import Chance
from .specials.EtoileFilante import EtoileFilante
from .specials.Anniversaire import Anniversaire
from .specials.Tsunami import Tsunami
from .specials.Vengeance import Vengeance
from .specials.Piston import Piston
from .specials.Heritage import Heritage
from .specials.Troc import Troc

from ..FlirtPlaces import FlirtPlaces

# ── Compteur d'ID unique ───────────────────────────────────────────────────────
_next_id = 0

def _uid() -> int:
    global _next_id
    _next_id += 1
    return _next_id


# ── Fabrique : card_id (str) → instance Card ──────────────────────────────────
# Signature de chaque lambda : () -> Card
_REGISTRY: dict[str, callable] = { # type: ignore
    # Salary cards
    "salary__1": lambda: SalaryCard(_uid(), "img/personnal_life/professionnal_life/SalaryCards/salary1.png", 1, 1),
    "salary__2": lambda: SalaryCard(_uid(), "img/personnal_life/professionnal_life/SalaryCards/salary2.png", 1, 2),
    "salary__3": lambda: SalaryCard(_uid(), "img/personnal_life/professionnal_life/SalaryCards/salary3.png", 1, 3),
    "salary__4": lambda: SalaryCard(_uid(), "img/personnal_life/professionnal_life/SalaryCards/salary4.png", 1, 4),

    # Study cards
    "study__1": lambda: StudyCard(_uid(), "img/personnal_life/professionnal_life/StudyCards/study1.png", 1, 1),
    "study__2": lambda: StudyCard(_uid(), "img/personnal_life/professionnal_life/StudyCards/study2.png", 1, 2),

    # Children
    "angela":   lambda: AngelaChild(_uid(), "img/personnal_life/children/angela.png"),
    "diana":    lambda: DianaChild(_uid(), "img/personnal_life/children/diana.png"),
    "harry":    lambda: HarryChild(_uid(), "img/personnal_life/children/harry.png"),
    "hermione": lambda: HermioneChild(_uid(), "img/personnal_life/children/hermione.png"),
    "lara":     lambda: LaraChild(_uid(), "img/personnal_life/children/lara.png"),
    "leia":     lambda: LeiaChild(_uid(), "img/personnal_life/children/leia.png"),
    "louise":   lambda: LouiseChild(_uid(), "img/personnal_life/children/louise.png"),
    "luigi":    lambda: LuigiChild(_uid(), "img/personnal_life/children/luigi.png"),
    "mario":    lambda: MarioChild(_uid(), "img/personnal_life/children/mario.png"),
    "luke":     lambda: LukeChild(_uid(), "img/personnal_life/children/luke.png"),
    "olympe":   lambda: OlympeChild(_uid(), "img/personnal_life/children/olympe.png"),
    "rocky":    lambda: RockyChild(_uid(), "img/personnal_life/children/rocky.png"),
    "simone":   lambda: SimoneChild(_uid(), "img/personnal_life/children/simone.png"),
    "zelda":    lambda: ZeldaChild(_uid(), "img/personnal_life/children/zelda.png"),
    # ── Animaux ────────────────────────────────────────────────────────────────
    "chien":   lambda: Chien(_uid(), "img/acquisition_cards/animals/chien.png"),
    "chat":    lambda: Chat(_uid(), "img/acquisition_cards/animals/chat.png"),
    "crapaud": lambda: Crapaud(_uid(), "img/acquisition_cards/animals/crapaud.png"),
    "lapin":   lambda: Lapin(_uid(), "img/acquisition_cards/animals/lapin.png"),
    "poussin": lambda: Poussin(_uid(), "img/acquisition_cards/animals/poussin.png"),
    "licorne": lambda: LicorneAnimal(_uid(), "img/acquisition_cards/animals/licorne.png"),

    # ── Acquisitions ───────────────────────────────────────────────────────────
    "house__1": lambda: House(_uid(), "img/acquisition_cards/houses/maison1.png", 1, 6),
    "house__2": lambda: House(_uid(), "img/acquisition_cards/houses/maison2.png", 2, 8),
    "house__3": lambda: House(_uid(), "img/acquisition_cards/houses/maison3.png", 3, 10),

    "travel__le_caire": lambda: Trip(_uid(), "img/acquisition_cards/trip/le_caire.png", 1, 3),
    "travel__londre":   lambda: Trip(_uid(), "img/acquisition_cards/trip/londres.png", 1, 3),
    "travel__new_york": lambda: Trip(_uid(), "img/acquisition_cards/trip/new_york.png", 1, 3),
    "travel__rio":      lambda: Trip(_uid(), "img/acquisition_cards/trip/rio.png", 1, 3),
    "travel__sydney":   lambda: Trip(_uid(), "img/acquisition_cards/trip/sydney.png", 1, 3),

    # ── Hardships ──────────────────────────────────────────────────────────────
    "accident":      lambda: Accident(_uid(), "img/hardship_cards/accident.png"),
    "maladie":       lambda: Maladie(_uid(), "img/hardship_cards/maladie.png"),
    "tax":           lambda: Tax(_uid(), "img/hardship_cards/tax.png"),
    "burnout":       lambda: BurnOut(_uid(), "img/hardship_cards/burnout.png"),
    "divorce":       lambda: Divorce(_uid(), "img/hardship_cards/divorce.png"),
    "licenciement":  lambda: Licenciement(_uid(), "img/hardship_cards/licenciement.png"),
    "redoublement":  lambda: Redoublement(_uid(), "img/hardship_cards/redoublement.png"),
    "prison":        lambda: Prison(_uid(), "img/hardship_cards/prison.png"),
    "attentat":      lambda: Attentat(_uid(), "img/hardship_cards/attentat.png"),

    # ── Personnal life ─────────────────────────────────────────────────────────
    "adultery": lambda: Adultery(_uid(), "img/personnal_life/mariages/adultery.png", 1),

    "marriage__corps_nuds":         lambda: Wedding(_uid(), "img/personnal_life/mariages/marriage_corps_nuds.png", 3),
    "marriage__fourqueux":          lambda: Wedding(_uid(), "img/personnal_life/mariages/marriage_fourqueux.png", 3),
    "marriage__montcuq":            lambda: Wedding(_uid(), "img/personnal_life/mariages/marriage_montcuq.png", 3),
    "marriage__monteton":           lambda: Wedding(_uid(), "img/personnal_life/mariages/marriage_monteton.png", 3),
    "marriage__sainte_vierge":      lambda: Wedding(_uid(), "img/personnal_life/mariages/marriage_sainte_vierge.png", 3),

    "flirt__bar":            lambda: Flirt(_uid(), "img/personnal_life/flirts/bar.png", 1, FlirtPlaces.BAR),
    "flirt__boite_de_nuit":  lambda: Flirt(_uid(), "img/personnal_life/flirts/boite_de_nuit.png", 1, FlirtPlaces.BOITE_DE_NUIT),
    "flirt__cinema":         lambda: Flirt(_uid(), "img/personnal_life/flirts/cinema.png", 1, FlirtPlaces.CINEMA),
    "flirt__internet":       lambda: Flirt(_uid(), "img/personnal_life/flirts/internet.png", 1, FlirtPlaces.INTERNET),
    "flirt__parc":           lambda: Flirt(_uid(), "img/personnal_life/flirts/parc.png", 1, FlirtPlaces.PARC),
    "flirt__restaurant":     lambda: Flirt(_uid(), "img/personnal_life/flirts/restaurant.png", 1, FlirtPlaces.RESTAURANT),
    "flirt__theatre":        lambda: Flirt(_uid(), "img/personnal_life/flirts/theatre.png", 1, FlirtPlaces.THEATRE),
    "flirt__zoo":            lambda: Flirt(_uid(), "img/personnal_life/flirts/zoo.png", 1, FlirtPlaces.ZOO),
    "flirt_with_child__hotel":            lambda: FlirtWithChild(_uid(), "img/personnal_life/flirts/hotel.png", 1, FlirtPlaces.HOTEL),
    "flirt_with_child__camping":            lambda: FlirtWithChild(_uid(), "img/personnal_life/flirts/camping.png", 1, FlirtPlaces.CAMPING),

    # ── Professionnel ──────────────────────────────────────────────────────────
    "serveur":       lambda: Serveur(_uid(), "img/personnal_life/professionnal_life/JobCards/serveur.png"),
    "garagiste":     lambda: Garagiste(_uid(), "img/personnal_life/professionnal_life/JobCards/garagiste.png"),
    "plombier":      lambda: Plombier(_uid(), "img/personnal_life/professionnal_life/JobCards/plombier.png"),
    "bandit":        lambda: Bandit(_uid(), "img/personnal_life/professionnal_life/JobCards/bandit.png"),
    "ecrivain":      lambda: Ecrivain(_uid(), "img/personnal_life/professionnal_life/JobCards/ecrivain.png"),
    "pharmacien":    lambda: Pharmacien(_uid(), "img/personnal_life/professionnal_life/JobCards/pharmacien.png"),
    "architecte":    lambda: Architect(_uid(), "img/personnal_life/professionnal_life/JobCards/architecte.png"),
    "militaire":     lambda: Militaire(_uid(), "img/personnal_life/professionnal_life/JobCards/militaire.png"),
    "medium":        lambda: Medium(_uid(), "img/personnal_life/professionnal_life/JobCards/medium.png"),
    "journaliste":   lambda: Journaliste(_uid(), "img/personnal_life/professionnal_life/JobCards/journaliste.png"),
    "chef_des_achats": lambda: ChefDesAchats(_uid(), "img/personnal_life/professionnal_life/JobCards/chef_des_achats.png"),
    "medecin":       lambda: Medecin(_uid(), "img/personnal_life/professionnal_life/JobCards/medecin.png"),
    "chirurgien":    lambda: Chirurgien(_uid(), "img/personnal_life/professionnal_life/JobCards/chirurgien.png"),
    "pilote":        lambda: PiloteDeLigne(_uid(), "img/personnal_life/professionnal_life/JobCards/pilote_de_ligne.png"),
    "astronaute":    lambda: Astronaute(_uid(), "img/personnal_life/professionnal_life/JobCards/astronaute.png"),
    "avocat":        lambda: Avocat(_uid(), "img/personnal_life/professionnal_life/JobCards/avocat.png"),
    "barman":        lambda: Barman(_uid(), "img/personnal_life/professionnal_life/JobCards/barman.png"),
    "chef_des_ventes": lambda: ChefDesVentes(_uid(), "img/personnal_life/professionnal_life/JobCards/chef_des_ventes.png"),
    "chercheur":     lambda: Chercheur(_uid(), "img/personnal_life/professionnal_life/JobCards/chercheur.png"),
    "gourou":        lambda: Gourou(_uid(), "img/personnal_life/professionnal_life/JobCards/gourou.png"),
    "grand_prof":    lambda: Grandprof(_uid(), "img/personnal_life/professionnal_life/JobCards/grand_prof.png"),
    'designer':     lambda: Designer(_uid(), "img/personnal_life/professionnal_life/JobCards/disigner.png"),
    'jardinier':     lambda: Jardinier(_uid(), "img/personnal_life/professionnal_life/JobCards/jardinier.png"),
    'pizzaiolo':     lambda: Pizzaiolo(_uid(), "img/personnal_life/professionnal_life/JobCards/pizzaiolo.png"),
    'policier':     lambda: Policier(_uid(), "img/personnal_life/professionnal_life/JobCards/policier.png"),
    'prof__maths':  lambda: Prof(_uid(), "img/personnal_life/professionnal_life/JobCards/prof_maths.png"),
    'prof__francais':lambda: Prof(_uid(), "img/personnal_life/professionnal_life/JobCards/prof_francais.png"),
    'prof__anglais':    lambda: Prof(_uid(), "img/personnal_life/professionnal_life/JobCards/prof_anglais.png"),
    'prof__geo':    lambda: Prof(_uid(), "img/personnal_life/professionnal_life/JobCards/prof_de_geo.png"),
    'stripteaser':  lambda: Stripteaser(_uid(), "img/personnal_life/professionnal_life/JobCards/stripteaser.png"),

    # ── Other ──────────────────────────────────────────────────────────────────
    "legion": lambda: Legion(_uid(), "img/personnal_life/professionnal_life/legion.png", 3),
    "prix":   lambda: Price(_uid(), "img/personnal_life/professionnal_life/price.png", 4),

    # ── Specials ───────────────────────────────────────────────────────────────
    "casino":         lambda: Casino(_uid(), "img/special_cards/casino.png"),
    "arc_en_ciel":    lambda: ArcEnCiel(_uid(), "img/special_cards/arc_en_ciel.png", 0),
    "chance":         lambda: Chance(_uid(), "img/special_cards/chance.png", 0),
    "etoile_filante": lambda: EtoileFilante(_uid(), "img/special_cards/etoile_filante.png", 0),
    "anniversaire":   lambda: Anniversaire(_uid(), "img/special_cards/anniversaire.png", 0),
    "tsunami":        lambda: Tsunami(_uid(), "img/special_cards/tsunami.png", 0),
    "vengeance":      lambda: Vengeance(_uid(), "img/special_cards/vengeance.png"),
    "piston":         lambda: Piston(_uid(), "img/special_cards/piston.png", 0),
    "heritage":       lambda: Heritage(_uid(), "img/special_cards/heritage.png", 0, 3),
    "troc":           lambda: Troc(_uid(), "img/special_cards/troc.png"),
}



def build_card(card_id: str) -> Card | None:
    """
    Instancie la carte correspondant à card_id.
    Retourne None si card_id est inconnu (carte pas encore implémentée).
    """
    factory = _REGISTRY.get(card_id)
    if factory is None:
        return None
    return factory()