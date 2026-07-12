"""
Registre des cartes : mappe les card_id du preset JSON vers les classes Card.
Ajoute ici chaque nouvelle carte ; le reste du code n'a pas à changer.
"""
from __future__ import annotations
from re import L

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
from .animals.Dragon import Dragon
from .animals.Rat import Rat
from .animals.ChauveSourie import ChauveSourie
from .animals.Phoenix import Phoenix
from .animals.Hibou import Hibou

# Acquisitions
from .acquisitions.HouseAcquisition import House
from .acquisitions.TripAcquisition import Trip, Ecosse, Atlandide, Salem, Transylvanie
from .acquisitions.PlaceDeConcert import Concert
from .acquisitions.Nounou import Nounou
from .acquisitions.Sabre import Sabre

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
from .hardships.ChargeMentale import ChargeMentale
from .hardships.TachesMenagere import TachesMenagere
from .hardships.Porc import Porc
from .hardships.Phalocratie import Phalocratie
from .hardships.Gynocratie import Gynocratie
from .hardships.PlafondDeVerre import PlafondDeVerre

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
    BeatrixChild,
    DaenerysChild,
    PeterChild,
    MerlinChild,
    BuffyChild
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
from .specials.ClicheAccident import ClicheAccident
from .specials.ClicheFlirt import ClicheFlirt
from .specials.CoupDeFoudre import CoupDeFoudre
from .specials.EgaliteSalaire import EgaliteSalaire
from .specials.SoireeEntreFille import SoireeEntreFille
from .specials.GirlPower import GrilPower
from .specials.ErreurEtiquetage import ErreurEtiquetage
from .specials.RedistributionTaches import RedistributionTaches

from ..FlirtPlaces import FlirtPlaces

from .ephemerides.LuneBleu import LuneBleu
from .ephemerides.Eclipse import Eclipse
from .ephemerides.Equinoxe import Equinoxe
from .ephemerides.LuneRouge import LuneRouge
from .ephemerides.PleineLune import PleineLune

from .acquisitions.potions.AmourEternelPotion import AmourEternelPotion
from .acquisitions.potions.ArgentPotion import ArgentPotion
from .acquisitions.potions.ChancePotion import ChancePotion
from .acquisitions.potions.EpousaillePotion import EpousaillePotion
from .acquisitions.potions.ExcellencePotion import ExcellencePotion
from .acquisitions.potions.FertilitePotion import FertilitePotion
from .acquisitions.potions.InterimPotion import InterimPotion
from .acquisitions.potions.ResurrectionPotion import ResurrectionPotion
from .acquisitions.potions.RistournellePotion import RistournellePotion
from .acquisitions.potions.SavoirPotion import SavoirPotion
from .acquisitions.potions.VitalitePotion import VitalitePotion

from .acquisitions.objets_magiques.Amulette import Amulette
from .acquisitions.objets_magiques.AnneauDePouvoir import AnneauDePouvoir
from .acquisitions.objets_magiques.BaguetteMagique import BaguetteMagique
from .acquisitions.objets_magiques.Balai import Balai
from .acquisitions.objets_magiques.BouleDeCristal import BouleDeCristal
from .acquisitions.objets_magiques.Miroir import Miroir
from .acquisitions.objets_magiques.LassoMagique import LassoMagique
from .acquisitions.objets_magiques.LampeMagique import LampeMagique
from .acquisitions.objets_magiques.Grimoire import Grimoire
from .acquisitions.objets_magiques.FluteEnchantee import FluteEnchantee
from .acquisitions.objets_magiques.Chaudron import Chaudron
from .acquisitions.objets_magiques.CapeInvisible import CapeInvisible

from .hardships.Malefices.Alcatras import Alcatras
from .hardships.Malefices.Sacrapas import Sacrapas
from .hardships.Malefices.Restataplas import Restataplas
from .hardships.Malefices.MinusMiserablis import MinusMiserablis
from .hardships.Malefices.MaxusMiserablis import MaxusMiserablis
from .hardships.Malefices.ManoNegra import ManoNegra
from .hardships.Malefices.Desenchantement import Desenchantement
from .hardships.Malefices.CasBurnas import CasBurnas
from .hardships.Malefices.BisRepetitas import BisRepetitas
from .hardships.Malefices.Aveuglement import Aveuglement

# ── Compteur d'ID unique ───────────────────────────────────────────────────────
_next_id = 0

def _uid() -> int:
    global _next_id
    _next_id += 1
    return _next_id


# ── Fabrique : card_id (str) → instance Card ──────────────────────────────────
# Signature de chaque lambda : () -> Card
_REGISTRY: dict[str, callable] = { # type: ignore
    
    #########################################################################################
    # ── Fantastique ──────────────────────────────────────────────────────────────
    #########################################################################################
    "malefice__alcatras": lambda : Alcatras(_uid(), "img/hardship_cards/malefis/alcatras.png"),
    "malefice__sacrapas": lambda: Sacrapas(_uid(), "img/hardship_cards/malefis/sacrapas.png"),
    "malefice__restataplas": lambda: Restataplas(_uid(), "img/hardship_cards/malefis/restataplas.png"),
    "malefice__minus_miserablis": lambda: MinusMiserablis(_uid(), "img/hardship_cards/malefis/minus_miserablis.png"),
    "malefice__maxus_miserablis": lambda: MaxusMiserablis(_uid(), "img/hardship_cards/malefis/maxus_miserablis.png"),
    "malefice__mano_negra": lambda: ManoNegra(_uid(), "img/hardship_cards/malefis/mano_negra.png"),
    "malefice__desenchantement": lambda: Desenchantement(_uid(), "img/hardship_cards/malefis/desenchantement.png"),
    "malefice__cas_burnas": lambda: CasBurnas(_uid(), "img/hardship_cards/malefis/cas_burnas.png"),
    "malefice__bis_repetitas": lambda: BisRepetitas(_uid(), "img/hardship_cards/malefis/bis_repetitas.png"),
    "malefice__aveuglement": lambda: Aveuglement(_uid(), "img/hardship_cards/malefis/aveuglement.png"),

    "objet_magique__amulette": lambda: Amulette(_uid(), "img/acquisition_cards/objets_magiques/amulette.png", 1, 0),
    "objet_magique__anneau_de_pouvoir": lambda: AnneauDePouvoir(_uid(), "img/acquisition_cards/objets_magiques/anneau_de_pouvoir.png", 3, 0),
    "objet_magique__baguette_magique": lambda: BaguetteMagique(_uid(), "img/acquisition_cards/objets_magiques/baguette_magique.png", 1, 0),
    "objet_magique__balai": lambda: Balai(_uid(), "img/acquisition_cards/objets_magiques/balai.png", 1, 0),
    "objet_magique__boule_de_cristal": lambda: BouleDeCristal(_uid(), "img/acquisition_cards/objets_magiques/boule_de_cristal.png", 1, 0),
    "objet_magique__miroir": lambda: Miroir(_uid(), "img/acquisition_cards/objets_magiques/miroir.png", 1, 0),
    "objet_magique__lasso_magique": lambda: LassoMagique(_uid(), "img/acquisition_cards/objets_magiques/lasso_magique.png", 1, 0),
    "objet_magique__lampe_magique": lambda: LampeMagique(_uid(), "img/acquisition_cards/objets_magiques/lampe_magique.png", 1, 0),
    "objet_magique__grimoire": lambda: Grimoire(_uid(), "img/acquisition_cards/objets_magiques/grimoire.png", 1, 0),
    "objet_magique__flute_enchantee": lambda: FluteEnchantee(_uid(), "img/acquisition_cards/objets_magiques/flute_enchantee.png", 1, 0),
    "objet_magique__chaudron": lambda: Chaudron(_uid(), "img/acquisition_cards/objets_magiques/chaudron.png", 1, 0),
    "objet_magique__cape_invisible": lambda: CapeInvisible(_uid(), "img/acquisition_cards/objets_magiques/cape_invisible.png", 1, 0),


    "potion__amour_eternel": lambda: AmourEternelPotion(_uid(), "img/acquisition_cards/potions/potion_amour_eternel.png", 1, 0),
    "potion__argent": lambda: ArgentPotion(_uid(), "img/acquisition_cards/potions/potion_argent.png", 1, 0),
    "potion__chance": lambda: ChancePotion(_uid(), "img/acquisition_cards/potions/potion_chance.png", 1, 0),
    "potion__epousaille": lambda: EpousaillePotion(_uid(), "img/acquisition_cards/potions/potion_epousaille.png", 1, 0),
    "potion__excellence": lambda: ExcellencePotion(_uid(), "img/acquisition_cards/potions/potion_excellence.png", 1, 0),
    "potion__fertilite": lambda: FertilitePotion(_uid(), "img/acquisition_cards/potions/potion_fertilite.png", 1, 0),
    "potion__interim": lambda: InterimPotion(_uid(), "img/acquisition_cards/potions/potion_interim.png", 1, 0),
    "potion__resurrection": lambda: ResurrectionPotion(_uid(), "img/acquisition_cards/potions/potion_resurrection.png", 1, 0),
    "potion__ristournelle": lambda: RistournellePotion(_uid(), "img/acquisition_cards/potions/potion_ristournelle.png", 1, 0),
    "potion__savoir": lambda: SavoirPotion(_uid(), "img/acquisition_cards/potions/potion_savoir.png", 1, 0),
    "potion__vitalite": lambda: VitalitePotion(_uid(), "img/acquisition_cards/potions/potion_vitalite.png", 1, 0),

    "ephemeride__eclipse": lambda : Eclipse(_uid(), "img/ephemerides/eclipse.png"),
    "ephemeride__equinoxe": lambda : Equinoxe(_uid(), "img/ephemerides/equinoxe.png"),
    "ephemeride__lune_bleu": lambda : LuneBleu(_uid(), "img/ephemerides/lune_bleu.png"),
    "ephemeride__lune_rouge": lambda : LuneRouge(_uid(), "img/ephemerides/lune_rouge.png"),
    "ephemeride__pleine_lune": lambda : PleineLune(_uid(), "img/ephemerides/pleine_lune.png"),

    # Trip
    "travel__transylvanie": lambda: Transylvanie(_uid(), "img/acquisition_cards/trip/transylvanie.png", 1, 3, "transylvanie"),
    "travel__ecosse": lambda: Ecosse(_uid(), "img/acquisition_cards/trip/ecosse.png", 1, 3, "ecosse"),
    "travel__atlantide": lambda: Atlandide(_uid(), "img/acquisition_cards/trip/atlantide.png", 1, 3, "atlandide"),
    "travel__salem": lambda: Salem(_uid(), "img/acquisition_cards/trip/salem.png", 1, 3, "salem"),

    "peter": lambda: PeterChild(_uid(), "img/personnal_life/children/peter.png"),
    "buffy": lambda: BuffyChild(_uid(), "img/personnal_life/children/buffy.png"),
    "merlin": lambda: MerlinChild(_uid(), "img/personnal_life/children/merlin.png"),

    "phoenix": lambda: Phoenix(_uid(), "img/acquisition_cards/animals/phoenix.png"),
    "rat": lambda: Rat(_uid(), "img/acquisition_cards/animals/rat.png"),
    "hibou": lambda: Hibou(_uid(), "img/acquisition_cards/animals/hibou.png"),
    "chauve_sourie": lambda: ChauveSourie(_uid(), "img/acquisition_cards/animals/chauve_sourie.png"),


    # Salary cards
    "salary__1": lambda: SalaryCard(_uid(), "img/personnal_life/professionnal_life/SalaryCards/salary1.png", 1, 1),
    "salary__2": lambda: SalaryCard(_uid(), "img/personnal_life/professionnal_life/SalaryCards/salary2.png", 1, 2),
    "salary__3": lambda: SalaryCard(_uid(), "img/personnal_life/professionnal_life/SalaryCards/salary3.png", 1, 3),
    "salary__4": lambda: SalaryCard(_uid(), "img/personnal_life/professionnal_life/SalaryCards/salary4.png", 1, 4),

    # Study cards
    "study__1": lambda: StudyCard(_uid(), "img/personnal_life/professionnal_life/StudyCards/study1.png", 1, 1),
    "study__2": lambda: StudyCard(_uid(), "img/personnal_life/professionnal_life/StudyCards/study2.png", 1, 2),

    # Children
    "diana":    lambda: DianaChild(_uid(), "img/personnal_life/children/diana.png"),
    "harry":    lambda: HarryChild(_uid(), "img/personnal_life/children/harry.png"),
    "hermione": lambda: HermioneChild(_uid(), "img/personnal_life/children/hermione.png"),
    "lara":     lambda: LaraChild(_uid(), "img/personnal_life/children/lara.png"),
    "leia":     lambda: LeiaChild(_uid(), "img/personnal_life/children/leia.png"),
    "luigi":    lambda: LuigiChild(_uid(), "img/personnal_life/children/luigi.png"),
    "mario":    lambda: MarioChild(_uid(), "img/personnal_life/children/mario.png"),
    "luke":     lambda: LukeChild(_uid(), "img/personnal_life/children/luke.png"),
    "rocky":    lambda: RockyChild(_uid(), "img/personnal_life/children/rocky.png"),
    "zelda":    lambda: ZeldaChild(_uid(), "img/personnal_life/children/zelda.png"),
    # ── Animaux ────────────────────────────────────────────────────────────────
    "chien":   lambda: Chien(_uid(), "img/acquisition_cards/animals/chien.png"  ),
    "chat":    lambda: Chat(_uid(), "img/acquisition_cards/animals/chat.png"),
    "lapin":   lambda: Lapin(_uid(), "img/acquisition_cards/animals/lapin.png"),
    "poussin": lambda: Poussin(_uid(), "img/acquisition_cards/animals/poussin.png"),
    "licorne": lambda: LicorneAnimal(_uid(), "img/acquisition_cards/animals/licorne.png"),

    # ── Acquisitions ───────────────────────────────────────────────────────────
    "house__1": lambda: House(_uid(), "img/acquisition_cards/houses/maison1.png", 1, 6),
    "house__2": lambda: House(_uid(), "img/acquisition_cards/houses/maison2.png", 2, 8),
    "house__3": lambda: House(_uid(), "img/acquisition_cards/houses/maison3.png", 3, 10),

    "travel__le_caire": lambda: Trip(_uid(), "img/acquisition_cards/trip/le_caire.png", 1, 3, "le caire"),
    "travel__londre":   lambda: Trip(_uid(), "img/acquisition_cards/trip/londres.png", 1, 3, "londre"),
    "travel__new_york": lambda: Trip(_uid(), "img/acquisition_cards/trip/new_york.png", 1, 3, "new york"),
    "travel__rio":      lambda: Trip(_uid(), "img/acquisition_cards/trip/rio.png", 1, 3, "rio"),
    "travel__sydney":   lambda: Trip(_uid(), "img/acquisition_cards/trip/sydney.png", 1, 3, "sydney"),

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
    "marriage__bourg_la_reine":      lambda: Wedding(_uid(), "img/personnal_life/mariages/marriage_bourg_la_reine.png", 3),

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
    'designer':     lambda: Designer(_uid(), "img/personnal_life/professionnal_life/JobCards/designer.png"),
    'jardinier':     lambda: Jardinier(_uid(), "img/personnal_life/professionnal_life/JobCards/jardinier.png"),
    'pizzaiolo':     lambda: Pizzaiolo(_uid(), "img/personnal_life/professionnal_life/JobCards/pizzaiolo.png"),
    'policier':     lambda: Policier(_uid(), "img/personnal_life/professionnal_life/JobCards/policier.png"),
    'prof__maths':  lambda: Prof(_uid(), "img/personnal_life/professionnal_life/JobCards/prof_maths.png"),
    'prof__francais':lambda: Prof(_uid(), "img/personnal_life/professionnal_life/JobCards/prof_francais.png"),
    'prof__anglais':    lambda: Prof(_uid(), "img/personnal_life/professionnal_life/JobCards/prof_anglais.png"),
    'prof__histoire':    lambda: Prof(_uid(), "img/personnal_life/professionnal_life/JobCards/prof_histoire.png"),
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



    #########################################################################################
    # ── Girl Power ──────────────────────────────────────────────────────────────
    #########################################################################################
    # ── Enfants ───────────────────────────────────────────────────────────────
    "olympe":   lambda: OlympeChild(_uid(), "img/personnal_life/children/olympe.png"),
    "simone":   lambda: SimoneChild(_uid(), "img/personnal_life/children/simone.png"),
    "angela":   lambda: AngelaChild(_uid(), "img/personnal_life/children/angela.png"),
    "beatrix":   lambda: BeatrixChild(_uid(), "img/personnal_life/children/beatrix.png"),
    "daenerys":   lambda: DaenerysChild(_uid(), "img/personnal_life/children/daenerys.png"),
    "louise":   lambda: LouiseChild(_uid(), "img/personnal_life/children/louise.png"),
    # ── Animaux ───────────────────────────────────────────────────────────────
    "crapaud": lambda: Crapaud(_uid(), "img/acquisition_cards/animals/crapaud.png"),
    "dragon": lambda: Dragon(_uid(), "img/acquisition_cards/animals/dragon.png"),
    # ── Acquisitions ──────────────────────────────────────────────────────────
    "concert": lambda: Concert(_uid(), "img/acquisition_cards/other/place_de_concert.png", 1, 1),
    "nounou": lambda: Nounou(_uid(), "img/acquisition_cards/other/nounou.png", 1, 4),
    "sabre": lambda: Sabre(_uid(), "img/acquisition_cards/other/sabre.png", 1, 1),
    # ── Épreuves ──────────────────────────────────────────────────────────────
    "charge_mentale":      lambda: ChargeMentale(_uid(), "img/hardship_cards/charge_mentale.png"),
    "taches_menageres":      lambda: TachesMenagere(_uid(), "img/hardship_cards/taches_menageres.png"),
    "porc":      lambda: Porc(_uid(), "img/hardship_cards/porc.png"),
    "phalocratie":      lambda: Phalocratie(_uid(), "img/hardship_cards/phalocratie.png"),
    "gynocratie":      lambda: Gynocratie(_uid(), "img/hardship_cards/gynocratie.png"),
    "plafond_de_verre":      lambda: PlafondDeVerre(_uid(), "img/hardship_cards/plafond_de_verre.png"),
    # ── Flirts ────────────────────────────────────────────────────────────────
    "flirt__manif":            lambda: Flirt(_uid(), "img/personnal_life/flirts/manif.png", 1, FlirtPlaces.MANIF),
    "flirt_with_child__bibliotheque":            lambda: FlirtWithChild(_uid(), "img/personnal_life/flirts/bibliotheque.png", 1, FlirtPlaces.BIBLIOTHEQUE),
    # ── Métiers ───────────────────────────────────────────────────────────────
    "serveuse": lambda: Serveur(_uid(), "img/personnal_life/professionnal_life/JobCards/serveuse.png"),
    "garagiste_f": lambda: Garagiste(_uid(), "img/personnal_life/professionnal_life/JobCards/garagiste_f.png"),
    "plombiere": lambda: Plombier(_uid(), "img/personnal_life/professionnal_life/JobCards/plombiere.png"),
    "bandit_f": lambda: Bandit(_uid(), "img/personnal_life/professionnal_life/JobCards/bandit_f.png"),
    "ecrivaine": lambda: Ecrivain(_uid(), "img/personnal_life/professionnal_life/JobCards/ecrivaine.png"),
    "pharmacienne": lambda: Pharmacien(_uid(), "img/personnal_life/professionnal_life/JobCards/pharmacienne.png"),
    "architecte_f": lambda: Architect(_uid(), "img/personnal_life/professionnal_life/JobCards/architecte_f.png"),
    "militaire_f": lambda: Militaire(_uid(), "img/personnal_life/professionnal_life/JobCards/militaire_f.png"),
    "voyante": lambda: Medium(_uid(), "img/personnal_life/professionnal_life/JobCards/voyante.png"),
    "journaliste_f": lambda: Journaliste(_uid(), "img/personnal_life/professionnal_life/JobCards/journaliste_f.png"),
    "cheffe_des_achats": lambda: ChefDesAchats(_uid(), "img/personnal_life/professionnal_life/JobCards/cheffe_des_achats.png"),
    "medecin_f": lambda: Medecin(_uid(), "img/personnal_life/professionnal_life/JobCards/medecin_f.png"),
    "chirurgienne": lambda: Chirurgien(_uid(), "img/personnal_life/professionnal_life/JobCards/chirurgienne.png"),
    "pilote_de_ligne_f": lambda: PiloteDeLigne(_uid(), "img/personnal_life/professionnal_life/JobCards/pilote_de_ligne_f.png"),
    "astronaute_f": lambda: Astronaute(_uid(), "img/personnal_life/professionnal_life/JobCards/astronaute_f.png"),
    "avocate": lambda: Avocat(_uid(), "img/personnal_life/professionnal_life/JobCards/avocate.png"),
    "barmaid": lambda: Barman(_uid(), "img/personnal_life/professionnal_life/JobCards/barmaid.png"),
    "cheffe_des_ventes": lambda: ChefDesVentes(_uid(), "img/personnal_life/professionnal_life/JobCards/cheffe_des_ventes.png"),
    "chercheuse": lambda: Chercheur(_uid(), "img/personnal_life/professionnal_life/JobCards/chercheuse.png"),
    "gourou_f": lambda: Gourou(_uid(), "img/personnal_life/professionnal_life/JobCards/gourou_f.png"),
    "grande_prof": lambda: Grandprof(_uid(), "img/personnal_life/professionnal_life/JobCards/grand_prof_f.png"),
    "designeuse": lambda: Designer(_uid(), "img/personnal_life/professionnal_life/JobCards/designeuse.png"),
    "jardiniere": lambda: Jardinier(_uid(), "img/personnal_life/professionnal_life/JobCards/jardiniere.png"),
    "pizzaiola": lambda: Pizzaiolo(_uid(), "img/personnal_life/professionnal_life/JobCards/pizzaiola.png"),
    "policiere": lambda: Policier(_uid(), "img/personnal_life/professionnal_life/JobCards/policiere.png"),
    "prof__chimie": lambda: Prof(_uid(), "img/personnal_life/professionnal_life/JobCards/prof_chimie.png"),
    "prof__musique": lambda: Prof(_uid(), "img/personnal_life/professionnal_life/JobCards/prof_musique.png"),
    "prof__philo": lambda: Prof(_uid(), "img/personnal_life/professionnal_life/JobCards/prof_philo.png"),
    "prof__geo": lambda: Prof(_uid(), "img/personnal_life/professionnal_life/JobCards/prof_geo.png"),
    "stripteaseuse": lambda: Stripteaser(_uid(), "img/personnal_life/professionnal_life/JobCards/stripteaseuse.png"),
    # ── Specials ───────────────────────────────────────────────────────────────
    "cliche_accident": lambda: ClicheAccident(_uid(), "img/special_cards/cliche_accident.png", 0),
    "cliche_flirt": lambda: ClicheFlirt(_uid(), "img/special_cards/cliche_flirt.png", 0),
    "coup_de_foudre": lambda: CoupDeFoudre(_uid(), "img/special_cards/coup_de_foudre.png", 0),
    "egalite_salaire": lambda: EgaliteSalaire(_uid(), "img/special_cards/egalite_salaire.png", 0),
    "soiree_entre_fille": lambda: SoireeEntreFille(_uid(), "img/special_cards/soiree_entre_filles.png", 0),
    "gril_power": lambda: GrilPower(_uid(), "img/special_cards/girl_power.png", 0),
    "erreur_etiquetage": lambda: ErreurEtiquetage(_uid(), "img/special_cards/erreur_etiquetage.png", 0),
    "redistribution_taches": lambda: RedistributionTaches(_uid(), "img/special_cards/redistribution_taches.png", 0),
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