"""
Registre des cartes : mappe les card_id du preset JSON vers les classes Card.
Ajoute ici chaque nouvelle carte ; le reste du code n'a pas à changer.
"""
from __future__ import annotations
from backend.core.cards.CardAttributes import Extention
# cartes

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

from ..roles.Ange import Ange
from ..roles.Vampire import Vampire
from ..roles.Sorciere import Sorciere
from ..roles.Sirene import Sirene
from ..roles.Mutant import Mutant
from ..roles.Magicien import Magicien
from ..roles.LoupGarou import LoupGarou
from ..roles.Fee import Fee
from ..roles.Demon import Demon
from ..roles.Chasseur import Chasseur

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
    "roles__ange": lambda : Ange("img/roles/ange.png"),
    "roles__vampire": lambda : Vampire("img/roles/vampire.png"),
    "roles__sorciere": lambda : Sorciere("img/roles/sorciere.png"),
    "roles__sirene": lambda : Sirene("img/roles/sirene.png"),
    "roles__mutant": lambda : Mutant("img/roles/mutant.png"),
    "roles__magicien": lambda : Magicien("img/roles/magicien.png"),
    "roles__loupgarou": lambda : LoupGarou("img/roles/loup_garou.png"),
    "roles__fee": lambda : Fee("img/roles/fee.png"),
    "roles__demon": lambda : Demon("img/roles/demon.png"),
    "roles__chasseur": lambda : Chasseur("img/roles/chasseur.png"),

    "malefice__alcatras": lambda : Alcatras(_uid(), "img/hardship_cards/malefis/alcatras.png", Extention.FANTASTIQUE),
    "malefice__sacrapas": lambda: Sacrapas(_uid(), "img/hardship_cards/malefis/sacrapas.png", Extention.FANTASTIQUE),
    "malefice__restataplas": lambda: Restataplas(_uid(), "img/hardship_cards/malefis/restataplas.png", Extention.FANTASTIQUE),
    "malefice__minus_miserablis": lambda: MinusMiserablis(_uid(), "img/hardship_cards/malefis/minus_miserablis.png", Extention.FANTASTIQUE),
    "malefice__maxus_miserablis": lambda: MaxusMiserablis(_uid(), "img/hardship_cards/malefis/maxus_miserablis.png", Extention.FANTASTIQUE),
    "malefice__mano_negra": lambda: ManoNegra(_uid(), "img/hardship_cards/malefis/mano_negra.png", Extention.FANTASTIQUE),
    "malefice__desenchantement": lambda: Desenchantement(_uid(), "img/hardship_cards/malefis/desenchantement.png", Extention.FANTASTIQUE),
    "malefice__cas_burnas": lambda: CasBurnas(_uid(), "img/hardship_cards/malefis/cas_burnas.png", Extention.FANTASTIQUE),
    "malefice__bis_repetitas": lambda: BisRepetitas(_uid(), "img/hardship_cards/malefis/bis_repetitas.png", Extention.FANTASTIQUE),
    "malefice__aveuglement": lambda: Aveuglement(_uid(), "img/hardship_cards/malefis/aveuglement.png", Extention.FANTASTIQUE),

    "objet_magique__amulette": lambda: Amulette(_uid(), "img/acquisition_cards/objets_magiques/amulette.png", 1, 1, Extention.FANTASTIQUE),
    "objet_magique__anneau_de_pouvoir": lambda: AnneauDePouvoir(_uid(), "img/acquisition_cards/objets_magiques/anneau_de_pouvoir.png", 3, 0, Extention.FANTASTIQUE),
    "objet_magique__baguette_magique": lambda: BaguetteMagique(_uid(), "img/acquisition_cards/objets_magiques/baguette_magique.png", 1, 2, Extention.FANTASTIQUE),
    "objet_magique__balai": lambda: Balai(_uid(), "img/acquisition_cards/objets_magiques/balai.png", 1, 3, Extention.FANTASTIQUE),
    "objet_magique__boule_de_cristal": lambda: BouleDeCristal(_uid(), "img/acquisition_cards/objets_magiques/boule_de_cristal.png", 1, 2, Extention.FANTASTIQUE),
    "objet_magique__miroir": lambda: Miroir(_uid(), "img/acquisition_cards/objets_magiques/miroir.png", 1, 5, Extention.FANTASTIQUE),
    "objet_magique__lasso_magique": lambda: LassoMagique(_uid(), "img/acquisition_cards/objets_magiques/lasso_magique.png", 1, 5, Extention.FANTASTIQUE),
    "objet_magique__lampe_magique": lambda: LampeMagique(_uid(), "img/acquisition_cards/objets_magiques/lampe_magique.png", 1, 6, Extention.FANTASTIQUE),
    "objet_magique__grimoire": lambda: Grimoire(_uid(), "img/acquisition_cards/objets_magiques/grimoire.png", 1, 1, Extention.FANTASTIQUE),
    "objet_magique__flute_enchantee": lambda: FluteEnchantee(_uid(), "img/acquisition_cards/objets_magiques/flute_enchantee.png", 1, 2, Extention.FANTASTIQUE),
    "objet_magique__chaudron": lambda: Chaudron(_uid(), "img/acquisition_cards/objets_magiques/chaudron.png", 1, 3, Extention.FANTASTIQUE),
    "objet_magique__cape_invisible": lambda: CapeInvisible(_uid(), "img/acquisition_cards/objets_magiques/cape_invisible.png", 1, 5, Extention.FANTASTIQUE),


    "potion__amour_eternel": lambda: AmourEternelPotion(_uid(), "img/acquisition_cards/potions/potion_amour_eternel.png", 1, 5, Extention.FANTASTIQUE),
    "potion__argent": lambda: ArgentPotion(_uid(), "img/acquisition_cards/potions/potion_argent.png", 1, 5, Extention.FANTASTIQUE),
    "potion__chance": lambda: ChancePotion(_uid(), "img/acquisition_cards/potions/potion_chance.png", 1, 2, Extention.FANTASTIQUE),
    "potion__epousaille": lambda: EpousaillePotion(_uid(), "img/acquisition_cards/potions/potion_epousaille.png", 1, 2, Extention.FANTASTIQUE),
    "potion__excellence": lambda: ExcellencePotion(_uid(), "img/acquisition_cards/potions/potion_excellence.png", 1, 4, Extention.FANTASTIQUE),
    "potion__fertilite": lambda: FertilitePotion(_uid(), "img/acquisition_cards/potions/potion_fertilite.png", 1, 3, Extention.FANTASTIQUE),
    "potion__interim": lambda: InterimPotion(_uid(), "img/acquisition_cards/potions/potion_interim.png", 1, 3, Extention.FANTASTIQUE),
    "potion__resurrection": lambda: ResurrectionPotion(_uid(), "img/acquisition_cards/potions/potion_resurrection.png", 1, 2, Extention.FANTASTIQUE),
    "potion__ristournelle": lambda: RistournellePotion(_uid(), "img/acquisition_cards/potions/potion_ristournelle.png", 1, 4, Extention.FANTASTIQUE),
    "potion__savoir": lambda: SavoirPotion(_uid(), "img/acquisition_cards/potions/potion_savoir.png", 1, 3, Extention.FANTASTIQUE),
    "potion__vitalite": lambda: VitalitePotion(_uid(), "img/acquisition_cards/potions/potion_vitalite.png", 1, 2, Extention.FANTASTIQUE),

    "ephemeride__eclipse": lambda : Eclipse(_uid(), "img/ephemerides/eclipse.png", Extention.FANTASTIQUE),
    "ephemeride__equinoxe": lambda : Equinoxe(_uid(), "img/ephemerides/equinoxe.png", Extention.FANTASTIQUE),
    "ephemeride__lune_bleu": lambda : LuneBleu(_uid(), "img/ephemerides/lune_bleu.png", Extention.FANTASTIQUE),
    "ephemeride__lune_rouge": lambda : LuneRouge(_uid(), "img/ephemerides/lune_rouge.png", Extention.FANTASTIQUE),
    "ephemeride__pleine_lune": lambda : PleineLune(_uid(), "img/ephemerides/pleine_lune.png", Extention.FANTASTIQUE),

    # Trip
    "travel__transylvanie": lambda: Transylvanie(_uid(), "img/acquisition_cards/trip/transylvanie.png", 1, 3, "transylvanie", Extention.FANTASTIQUE),
    "travel__ecosse": lambda: Ecosse(_uid(), "img/acquisition_cards/trip/ecosse.png", 1, 3, "ecosse", Extention.FANTASTIQUE),
    "travel__atlantide": lambda: Atlandide(_uid(), "img/acquisition_cards/trip/atlantide.png", 1, 3, "atlandide", Extention.FANTASTIQUE),
    "travel__salem": lambda: Salem(_uid(), "img/acquisition_cards/trip/salem.png", 1, 3, "salem", Extention.FANTASTIQUE),

    "peter": lambda: PeterChild(_uid(), "img/personnal_life/children/peter.png", Extention.FANTASTIQUE),
    "buffy": lambda: BuffyChild(_uid(), "img/personnal_life/children/buffy.png", Extention.FANTASTIQUE),
    "merlin": lambda: MerlinChild(_uid(), "img/personnal_life/children/merlin.png", Extention.FANTASTIQUE),

    "phoenix": lambda: Phoenix(_uid(), "img/acquisition_cards/animals/phoenix.png", Extention.FANTASTIQUE),
    "rat": lambda: Rat(_uid(), "img/acquisition_cards/animals/rat.png", Extention.FANTASTIQUE),
    "hibou": lambda: Hibou(_uid(), "img/acquisition_cards/animals/hibou.png", Extention.FANTASTIQUE),
    "chauve_sourie": lambda: ChauveSourie(_uid(), "img/acquisition_cards/animals/chauve_sourie.png", Extention.FANTASTIQUE),


    # Salary cards
    "salary__1": lambda: SalaryCard(_uid(), "img/personnal_life/professionnal_life/SalaryCards/salary1.png", 1, 1, Extention.BASE),
    "salary__2": lambda: SalaryCard(_uid(), "img/personnal_life/professionnal_life/SalaryCards/salary2.png", 1, 2, Extention.BASE),
    "salary__3": lambda: SalaryCard(_uid(), "img/personnal_life/professionnal_life/SalaryCards/salary3.png", 1, 3, Extention.BASE),
    "salary__4": lambda: SalaryCard(_uid(), "img/personnal_life/professionnal_life/SalaryCards/salary4.png", 1, 4, Extention.BASE),

    # Study cards
    "study__1": lambda: StudyCard(_uid(), "img/personnal_life/professionnal_life/StudyCards/study1.png", 1, 1, Extention.BASE),
    "study__2": lambda: StudyCard(_uid(), "img/personnal_life/professionnal_life/StudyCards/study2.png", 1, 2, Extention.BASE),

    # Children
    "diana":    lambda: DianaChild(_uid(), "img/personnal_life/children/diana.png", Extention.BASE),
    "harry":    lambda: HarryChild(_uid(), "img/personnal_life/children/harry.png", Extention.BASE),
    "hermione": lambda: HermioneChild(_uid(), "img/personnal_life/children/hermione.png", Extention.BASE),
    "lara":     lambda: LaraChild(_uid(), "img/personnal_life/children/lara.png", Extention.BASE),
    "leia":     lambda: LeiaChild(_uid(), "img/personnal_life/children/leia.png", Extention.BASE),
    "luigi":    lambda: LuigiChild(_uid(), "img/personnal_life/children/luigi.png", Extention.BASE),
    "mario":    lambda: MarioChild(_uid(), "img/personnal_life/children/mario.png", Extention.BASE),
    "luke":     lambda: LukeChild(_uid(), "img/personnal_life/children/luke.png", Extention.BASE),
    "rocky":    lambda: RockyChild(_uid(), "img/personnal_life/children/rocky.png", Extention.BASE),
    "zelda":    lambda: ZeldaChild(_uid(), "img/personnal_life/children/zelda.png", Extention.BASE),
    # ── Animaux ────────────────────────────────────────────────────────────────
    "chien":   lambda: Chien(_uid(), "img/acquisition_cards/animals/chien.png", Extention.BASE),
    "chat":    lambda: Chat(_uid(), "img/acquisition_cards/animals/chat.png", Extention.BASE),
    "lapin":   lambda: Lapin(_uid(), "img/acquisition_cards/animals/lapin.png", Extention.BASE),
    "poussin": lambda: Poussin(_uid(), "img/acquisition_cards/animals/poussin.png", Extention.BASE),
    "licorne": lambda: LicorneAnimal(_uid(), "img/acquisition_cards/animals/licorne.png", Extention.BASE),

    # ── Acquisitions ───────────────────────────────────────────────────────────
    "house__1": lambda: House(_uid(), "img/acquisition_cards/houses/maison1.png", 1, 6, Extention.BASE),
    "house__2": lambda: House(_uid(), "img/acquisition_cards/houses/maison2.png", 2, 8, Extention.BASE),
    "house__3": lambda: House(_uid(), "img/acquisition_cards/houses/maison3.png", 3, 10, Extention.BASE),

    "travel__le_caire": lambda: Trip(_uid(), "img/acquisition_cards/trip/le_caire.png", 1, 3, "le caire", Extention.BASE),
    "travel__londre":   lambda: Trip(_uid(), "img/acquisition_cards/trip/londres.png", 1, 3, "londre", Extention.BASE),
    "travel__new_york": lambda: Trip(_uid(), "img/acquisition_cards/trip/new_york.png", 1, 3, "new york", Extention.BASE),
    "travel__rio":      lambda: Trip(_uid(), "img/acquisition_cards/trip/rio.png", 1, 3, "rio", Extention.BASE),
    "travel__sydney":   lambda: Trip(_uid(), "img/acquisition_cards/trip/sydney.png", 1, 3, "sydney", Extention.BASE),

    # ── Hardships ──────────────────────────────────────────────────────────────
    "accident":      lambda: Accident(_uid(), "img/hardship_cards/accident.png", Extention.BASE),
    "maladie":       lambda: Maladie(_uid(), "img/hardship_cards/maladie.png", Extention.BASE),
    "tax":           lambda: Tax(_uid(), "img/hardship_cards/tax.png", Extention.BASE),
    "burnout":       lambda: BurnOut(_uid(), "img/hardship_cards/burnout.png", Extention.BASE),
    "divorce":       lambda: Divorce(_uid(), "img/hardship_cards/divorce.png", Extention.BASE),
    "licenciement":  lambda: Licenciement(_uid(), "img/hardship_cards/licenciement.png", Extention.BASE),
    "redoublement":  lambda: Redoublement(_uid(), "img/hardship_cards/redoublement.png", Extention.BASE),
    "prison":        lambda: Prison(_uid(), "img/hardship_cards/prison.png", Extention.BASE),
    "attentat":      lambda: Attentat(_uid(), "img/hardship_cards/attentat.png", Extention.BASE),

    # ── Personnal life ─────────────────────────────────────────────────────────
    "adultery": lambda: Adultery(_uid(), "img/personnal_life/mariages/adultery.png", 1, Extention.BASE),

    "marriage__corps_nuds":         lambda: Wedding(_uid(), "img/personnal_life/mariages/marriage_corps_nuds.png", 3, Extention.BASE),
    "marriage__fourqueux":          lambda: Wedding(_uid(), "img/personnal_life/mariages/marriage_fourqueux.png", 3, Extention.BASE),
    "marriage__montcuq":            lambda: Wedding(_uid(), "img/personnal_life/mariages/marriage_montcuq.png", 3, Extention.BASE),
    "marriage__monteton":           lambda: Wedding(_uid(), "img/personnal_life/mariages/marriage_monteton.png", 3, Extention.BASE),
    "marriage__sainte_vierge":      lambda: Wedding(_uid(), "img/personnal_life/mariages/marriage_sainte_vierge.png", 3, Extention.BASE),
    "marriage__bourg_la_reine":      lambda: Wedding(_uid(), "img/personnal_life/mariages/marriage_bourg_la_reine.png", 3, Extention.BASE),

    "flirt__bar":            lambda: Flirt(_uid(), "img/personnal_life/flirts/bar.png", 1, FlirtPlaces.BAR, Extention.BASE),
    "flirt__boite_de_nuit":  lambda: Flirt(_uid(), "img/personnal_life/flirts/boite_de_nuit.png", 1, FlirtPlaces.BOITE_DE_NUIT, Extention.BASE),
    "flirt__cinema":         lambda: Flirt(_uid(), "img/personnal_life/flirts/cinema.png", 1, FlirtPlaces.CINEMA, Extention.BASE),
    "flirt__internet":       lambda: Flirt(_uid(), "img/personnal_life/flirts/internet.png", 1, FlirtPlaces.INTERNET, Extention.BASE),
    "flirt__parc":           lambda: Flirt(_uid(), "img/personnal_life/flirts/parc.png", 1, FlirtPlaces.PARC, Extention.BASE),
    "flirt__restaurant":     lambda: Flirt(_uid(), "img/personnal_life/flirts/restaurant.png", 1, FlirtPlaces.RESTAURANT, Extention.BASE),
    "flirt__theatre":        lambda: Flirt(_uid(), "img/personnal_life/flirts/theatre.png", 1, FlirtPlaces.THEATRE, Extention.BASE),
    "flirt__zoo":            lambda: Flirt(_uid(), "img/personnal_life/flirts/zoo.png", 1, FlirtPlaces.ZOO, Extention.BASE),
    "flirt_with_child__hotel":            lambda: FlirtWithChild(_uid(), "img/personnal_life/flirts/hotel.png", 1, FlirtPlaces.HOTEL, Extention.BASE),
    "flirt_with_child__camping":            lambda: FlirtWithChild(_uid(), "img/personnal_life/flirts/camping.png", 1, FlirtPlaces.CAMPING, Extention.BASE),

    # ── Professionnel ──────────────────────────────────────────────────────────
    "serveur":       lambda: Serveur(_uid(), "img/personnal_life/professionnal_life/JobCards/serveur.png", Extention.BASE),
    "garagiste":     lambda: Garagiste(_uid(), "img/personnal_life/professionnal_life/JobCards/garagiste.png", Extention.BASE),
    "plombier":      lambda: Plombier(_uid(), "img/personnal_life/professionnal_life/JobCards/plombier.png", Extention.BASE),
    "bandit":        lambda: Bandit(_uid(), "img/personnal_life/professionnal_life/JobCards/bandit.png", Extention.BASE),
    "ecrivain":      lambda: Ecrivain(_uid(), "img/personnal_life/professionnal_life/JobCards/ecrivain.png", Extention.BASE),
    "pharmacien":    lambda: Pharmacien(_uid(), "img/personnal_life/professionnal_life/JobCards/pharmacien.png", Extention.BASE),
    "architecte":    lambda: Architect(_uid(), "img/personnal_life/professionnal_life/JobCards/architecte.png", Extention.BASE),
    "militaire":     lambda: Militaire(_uid(), "img/personnal_life/professionnal_life/JobCards/militaire.png", Extention.BASE),
    "medium":        lambda: Medium(_uid(), "img/personnal_life/professionnal_life/JobCards/medium.png", Extention.BASE),
    "journaliste":   lambda: Journaliste(_uid(), "img/personnal_life/professionnal_life/JobCards/journaliste.png", Extention.BASE),
    "chef_des_achats": lambda: ChefDesAchats(_uid(), "img/personnal_life/professionnal_life/JobCards/chef_des_achats.png", Extention.BASE),
    "medecin":       lambda: Medecin(_uid(), "img/personnal_life/professionnal_life/JobCards/medecin.png", Extention.BASE),
    "chirurgien":    lambda: Chirurgien(_uid(), "img/personnal_life/professionnal_life/JobCards/chirurgien.png", Extention.BASE),
    "pilote":        lambda: PiloteDeLigne(_uid(), "img/personnal_life/professionnal_life/JobCards/pilote_de_ligne.png", Extention.BASE),
    "astronaute":    lambda: Astronaute(_uid(), "img/personnal_life/professionnal_life/JobCards/astronaute.png", Extention.BASE),
    "avocat":        lambda: Avocat(_uid(), "img/personnal_life/professionnal_life/JobCards/avocat.png", Extention.BASE),
    "barman":        lambda: Barman(_uid(), "img/personnal_life/professionnal_life/JobCards/barman.png", Extention.BASE),
    "chef_des_ventes": lambda: ChefDesVentes(_uid(), "img/personnal_life/professionnal_life/JobCards/chef_des_ventes.png", Extention.BASE),
    "chercheur":     lambda: Chercheur(_uid(), "img/personnal_life/professionnal_life/JobCards/chercheur.png", Extention.BASE),
    "gourou":        lambda: Gourou(_uid(), "img/personnal_life/professionnal_life/JobCards/gourou.png", Extention.BASE),
    "grand_prof":    lambda: Grandprof(_uid(), "img/personnal_life/professionnal_life/JobCards/grand_prof.png", Extention.BASE),
    'designer':     lambda: Designer(_uid(), "img/personnal_life/professionnal_life/JobCards/designer.png", Extention.BASE),
    'jardinier':     lambda: Jardinier(_uid(), "img/personnal_life/professionnal_life/JobCards/jardinier.png", Extention.BASE),
    'pizzaiolo':     lambda: Pizzaiolo(_uid(), "img/personnal_life/professionnal_life/JobCards/pizzaiolo.png", Extention.BASE),
    'policier':     lambda: Policier(_uid(), "img/personnal_life/professionnal_life/JobCards/policier.png", Extention.BASE),
    'prof__maths':  lambda: Prof(_uid(), "img/personnal_life/professionnal_life/JobCards/prof_maths.png", Extention.BASE),
    'prof__francais':lambda: Prof(_uid(), "img/personnal_life/professionnal_life/JobCards/prof_francais.png", Extention.BASE),
    'prof__anglais':    lambda: Prof(_uid(), "img/personnal_life/professionnal_life/JobCards/prof_anglais.png", Extention.BASE),
    'prof__histoire':    lambda: Prof(_uid(), "img/personnal_life/professionnal_life/JobCards/prof_histoire.png", Extention.BASE),
    'stripteaser':  lambda: Stripteaser(_uid(), "img/personnal_life/professionnal_life/JobCards/stripteaser.png", Extention.BASE),

    # ── Other ──────────────────────────────────────────────────────────────────
    "legion": lambda: Legion(_uid(), "img/personnal_life/professionnal_life/legion.png", 3, Extention.BASE),
    "prix":   lambda: Price(_uid(), "img/personnal_life/professionnal_life/price.png", 4, Extention.BASE),

    # ── Specials ───────────────────────────────────────────────────────────────
    "casino":         lambda: Casino(_uid(), "img/special_cards/casino.png", Extention.BASE),
    "arc_en_ciel":    lambda: ArcEnCiel(_uid(), "img/special_cards/arc_en_ciel.png", 0, Extention.BASE),
    "chance":         lambda: Chance(_uid(), "img/special_cards/chance.png", 0, Extention.BASE),
    "etoile_filante": lambda: EtoileFilante(_uid(), "img/special_cards/etoile_filante.png", 0, Extention.BASE),
    "anniversaire":   lambda: Anniversaire(_uid(), "img/special_cards/anniversaire.png", 0, Extention.BASE),
    "tsunami":        lambda: Tsunami(_uid(), "img/special_cards/tsunami.png", 0, Extention.BASE),
    "vengeance":      lambda: Vengeance(_uid(), "img/special_cards/vengeance.png", Extention.BASE),
    "piston":         lambda: Piston(_uid(), "img/special_cards/piston.png", 0, Extention.BASE),
    "heritage":       lambda: Heritage(_uid(), "img/special_cards/heritage.png", 0, 3, Extention.BASE),
    "troc":           lambda: Troc(_uid(), "img/special_cards/troc.png", Extention.BASE),



    #########################################################################################
    # ── Girl Power ──────────────────────────────────────────────────────────────
    #########################################################################################
    # ── Enfants ───────────────────────────────────────────────────────────────
    "olympe":   lambda: OlympeChild(_uid(), "img/personnal_life/children/olympe.png", Extention.GIRL_POWER),
    "simone":   lambda: SimoneChild(_uid(), "img/personnal_life/children/simone.png", Extention.GIRL_POWER),
    "angela":   lambda: AngelaChild(_uid(), "img/personnal_life/children/angela.png", Extention.GIRL_POWER),
    "beatrix":   lambda: BeatrixChild(_uid(), "img/personnal_life/children/beatrix.png", Extention.GIRL_POWER),
    "daenerys":   lambda: DaenerysChild(_uid(), "img/personnal_life/children/daenerys.png", Extention.GIRL_POWER),
    "louise":   lambda: LouiseChild(_uid(), "img/personnal_life/children/louise.png", Extention.GIRL_POWER),
    # ── Animaux ───────────────────────────────────────────────────────────────
    "crapaud": lambda: Crapaud(_uid(), "img/acquisition_cards/animals/crapaud.png", Extention.GIRL_POWER),
    "dragon": lambda: Dragon(_uid(), "img/acquisition_cards/animals/dragon.png", Extention.GIRL_POWER),
    # ── Acquisitions ──────────────────────────────────────────────────────────
    "concert": lambda: Concert(_uid(), "img/acquisition_cards/other/place_de_concert.png", 1, 1, Extention.GIRL_POWER),
    "nounou": lambda: Nounou(_uid(), "img/acquisition_cards/other/nounou.png", 1, 4, Extention.GIRL_POWER),
    "sabre": lambda: Sabre(_uid(), "img/acquisition_cards/other/sabre.png", 1, 1, Extention.GIRL_POWER),
    # ── Épreuves ──────────────────────────────────────────────────────────────
    "charge_mentale":      lambda: ChargeMentale(_uid(), "img/hardship_cards/charge_mentale.png", Extention.GIRL_POWER),
    "taches_menageres":      lambda: TachesMenagere(_uid(), "img/hardship_cards/taches_menageres.png", Extention.GIRL_POWER),
    "porc":      lambda: Porc(_uid(), "img/hardship_cards/porc.png", Extention.GIRL_POWER),
    "phalocratie":      lambda: Phalocratie(_uid(), "img/hardship_cards/phalocratie.png", Extention.GIRL_POWER),
    "gynocratie":      lambda: Gynocratie(_uid(), "img/hardship_cards/gynocratie.png", Extention.GIRL_POWER),
    "plafond_de_verre":      lambda: PlafondDeVerre(_uid(), "img/hardship_cards/plafond_de_verre.png", Extention.GIRL_POWER),
    # ── Flirts ────────────────────────────────────────────────────────────────
    "flirt__manif":            lambda: Flirt(_uid(), "img/personnal_life/flirts/manif.png", 1, FlirtPlaces.MANIF, Extention.GIRL_POWER),
    "flirt_with_child__bibliotheque":            lambda: FlirtWithChild(_uid(), "img/personnal_life/flirts/bibliotheque.png", 1, FlirtPlaces.BIBLIOTHEQUE, Extention.GIRL_POWER),
    # ── Métiers ───────────────────────────────────────────────────────────────
    "serveuse": lambda: Serveur(_uid(), "img/personnal_life/professionnal_life/JobCards/serveuse.png", Extention.GIRL_POWER),
    "garagiste_f": lambda: Garagiste(_uid(), "img/personnal_life/professionnal_life/JobCards/garagiste_f.png", Extention.GIRL_POWER),
    "plombiere": lambda: Plombier(_uid(), "img/personnal_life/professionnal_life/JobCards/plombiere.png", Extention.GIRL_POWER),
    "bandit_f": lambda: Bandit(_uid(), "img/personnal_life/professionnal_life/JobCards/bandit_f.png", Extention.GIRL_POWER),
    "ecrivaine": lambda: Ecrivain(_uid(), "img/personnal_life/professionnal_life/JobCards/ecrivaine.png", Extention.GIRL_POWER),
    "pharmacienne": lambda: Pharmacien(_uid(), "img/personnal_life/professionnal_life/JobCards/pharmacienne.png", Extention.GIRL_POWER),
    "architecte_f": lambda: Architect(_uid(), "img/personnal_life/professionnal_life/JobCards/architecte_f.png", Extention.GIRL_POWER),
    "militaire_f": lambda: Militaire(_uid(), "img/personnal_life/professionnal_life/JobCards/militaire_f.png", Extention.GIRL_POWER),
    "voyante": lambda: Medium(_uid(), "img/personnal_life/professionnal_life/JobCards/voyante.png", Extention.GIRL_POWER),
    "journaliste_f": lambda: Journaliste(_uid(), "img/personnal_life/professionnal_life/JobCards/journaliste_f.png", Extention.GIRL_POWER),
    "cheffe_des_achats": lambda: ChefDesAchats(_uid(), "img/personnal_life/professionnal_life/JobCards/cheffe_des_achats.png", Extention.GIRL_POWER),
    "medecin_f": lambda: Medecin(_uid(), "img/personnal_life/professionnal_life/JobCards/medecin_f.png", Extention.GIRL_POWER),
    "chirurgienne": lambda: Chirurgien(_uid(), "img/personnal_life/professionnal_life/JobCards/chirurgienne.png", Extention.GIRL_POWER),
    "pilote_de_ligne_f": lambda: PiloteDeLigne(_uid(), "img/personnal_life/professionnal_life/JobCards/pilote_de_ligne_f.png", Extention.GIRL_POWER),
    "astronaute_f": lambda: Astronaute(_uid(), "img/personnal_life/professionnal_life/JobCards/astronaute_f.png", Extention.GIRL_POWER),
    "avocate": lambda: Avocat(_uid(), "img/personnal_life/professionnal_life/JobCards/avocate.png", Extention.GIRL_POWER),
    "barmaid": lambda: Barman(_uid(), "img/personnal_life/professionnal_life/JobCards/barmaid.png", Extention.GIRL_POWER),
    "cheffe_des_ventes": lambda: ChefDesVentes(_uid(), "img/personnal_life/professionnal_life/JobCards/cheffe_des_ventes.png", Extention.GIRL_POWER),
    "chercheuse": lambda: Chercheur(_uid(), "img/personnal_life/professionnal_life/JobCards/chercheuse.png", Extention.GIRL_POWER),
    "gourou_f": lambda: Gourou(_uid(), "img/personnal_life/professionnal_life/JobCards/gourou_f.png", Extention.GIRL_POWER),
    "grande_prof": lambda: Grandprof(_uid(), "img/personnal_life/professionnal_life/JobCards/grand_prof_f.png", Extention.GIRL_POWER),
    "designeuse": lambda: Designer(_uid(), "img/personnal_life/professionnal_life/JobCards/designeuse.png", Extention.GIRL_POWER),
    "jardiniere": lambda: Jardinier(_uid(), "img/personnal_life/professionnal_life/JobCards/jardiniere.png", Extention.GIRL_POWER),
    "pizzaiola": lambda: Pizzaiolo(_uid(), "img/personnal_life/professionnal_life/JobCards/pizzaiola.png", Extention.GIRL_POWER),
    "policiere": lambda: Policier(_uid(), "img/personnal_life/professionnal_life/JobCards/policiere.png", Extention.GIRL_POWER),
    "prof__chimie": lambda: Prof(_uid(), "img/personnal_life/professionnal_life/JobCards/prof_chimie.png", Extention.GIRL_POWER),
    "prof__musique": lambda: Prof(_uid(), "img/personnal_life/professionnal_life/JobCards/prof_musique.png", Extention.GIRL_POWER),
    "prof__philo": lambda: Prof(_uid(), "img/personnal_life/professionnal_life/JobCards/prof_philo.png", Extention.GIRL_POWER),
    "prof__geo": lambda: Prof(_uid(), "img/personnal_life/professionnal_life/JobCards/prof_geo.png", Extention.GIRL_POWER),
    "stripteaseuse": lambda: Stripteaser(_uid(), "img/personnal_life/professionnal_life/JobCards/stripteaseuse.png", Extention.GIRL_POWER),
    # ── Specials ───────────────────────────────────────────────────────────────
    "cliche_accident": lambda: ClicheAccident(_uid(), "img/special_cards/cliche_accident.png", 0, Extention.GIRL_POWER),
    "cliche_flirt": lambda: ClicheFlirt(_uid(), "img/special_cards/cliche_flirt.png", 0, Extention.GIRL_POWER),
    "coup_de_foudre": lambda: CoupDeFoudre(_uid(), "img/special_cards/coup_de_foudre.png", 0, Extention.GIRL_POWER),
    "egalite_salaire": lambda: EgaliteSalaire(_uid(), "img/special_cards/egalite_salaire.png", 0, Extention.GIRL_POWER),
    "soiree_entre_fille": lambda: SoireeEntreFille(_uid(), "img/special_cards/soiree_entre_filles.png", 0, Extention.GIRL_POWER),
    "gril_power": lambda: GrilPower(_uid(), "img/special_cards/girl_power.png", 0, Extention.GIRL_POWER),
    "erreur_etiquetage": lambda: ErreurEtiquetage(_uid(), "img/special_cards/erreur_etiquetage.png", 0, Extention.GIRL_POWER),
    "redistribution_taches": lambda: RedistributionTaches(_uid(), "img/special_cards/redistribution_taches.png", 0, Extention.GIRL_POWER),
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