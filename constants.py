from flask import Flask, request
from flask_socketio import SocketIO, emit
from card_classes import *
import os

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete_ici_changez_la'
socketio = SocketIO(app, cors_allowed_origins="*",  async_mode='threading')

# Configuration pour servir les images
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'ressources')

# Stockage des parties et des joueurs connectés
games = {}
player_sessions = {}  # {session_id: {game_id, player_id}}
card_builders = {
    # --- MÉTIERS ---
    "architecte": lambda: ArchitecteJob("architecte", 3, 4, "personnal_life/professionnal_life/JobCards/architecte.png"),
    "astronaute": lambda: AstronauteJob("astronaute", 4, 6, "personnal_life/professionnal_life/JobCards/astronaute.png"),
    "avocat": lambda: AvocatJob("avocat", 3, 4, "personnal_life/professionnal_life/JobCards/avocat.png"),
    "bandit": lambda: BanditJob("bandit", 4, 0, "personnal_life/professionnal_life/JobCards/bandit.png"),
    "barman": lambda: BarmanJob("barman", 1, 0, "personnal_life/professionnal_life/JobCards/barman.png"),
    "chef_des_ventes": lambda: ChefDesVentesJob("chef des ventes", 3, 3, "personnal_life/professionnal_life/JobCards/chef_des_ventes.png"),
    "chef_des_achats": lambda: ChefDesAchatsJob("chef des achats", 3, 3, "personnal_life/professionnal_life/JobCards/chef_des_achats.png"),
    "chercheur": lambda: ChercheurJob("chercheur", 2, 6, "personnal_life/professionnal_life/JobCards/chercheur.png"),
    "chirurgien": lambda: ChirurgienJob("chirurgien", 4, 6, "personnal_life/professionnal_life/JobCards/chirurgien.png"),
    "designer": lambda: DesignerJob("designer", 3, 4, "personnal_life/professionnal_life/JobCards/designer.png"),
    "ecrivain": lambda: EcrivainJob("ecrivain", 1, 0, "personnal_life/professionnal_life/JobCards/ecrivain.png"),
    "garagiste": lambda: GaragisteJob("garagiste", 2, 1, "personnal_life/professionnal_life/JobCards/garagiste.png"),
    "gourou": lambda: GourouJob("gourou", 3, 0, "personnal_life/professionnal_life/JobCards/gourou.png"),
    "jardinier": lambda: JardinierJob("jardinier", 1, 1, "personnal_life/professionnal_life/JobCards/jardinier.png"),
    "journaliste": lambda: JournalisteJob("journaliste", 2, 3, "personnal_life/professionnal_life/JobCards/journaliste.png"),
    "medecin": lambda: MedecinJob("médecin", 4, 6, "personnal_life/professionnal_life/JobCards/medecin.png"),
    "medium": lambda: MediumJob("médium", 1, 0, "personnal_life/professionnal_life/JobCards/medium.png"),
    "militaire": lambda: MilitaireJob("militaire", 1, 0, "personnal_life/professionnal_life/JobCards/militaire.png"),
    "pharmacien": lambda: PharmacienJob("pharmacien", 3, 5, "personnal_life/professionnal_life/JobCards/pharmacien.png"),
    "pilote_de_ligne": lambda: PiloteDeLigneJob("pilote de ligne", 4, 5, "personnal_life/professionnal_life/JobCards/pilote_de_ligne.png"),
    "pizzaiolo": lambda: PizzaioloJob("pizzaiolo", 2, 0, "personnal_life/professionnal_life/JobCards/pizzaiolo.png"),
    "plombier": lambda: PlombierJob("plombier", 1, 1, "personnal_life/professionnal_life/JobCards/plombier.png"),
    "policier": lambda: PolicierJob("policier", 1, 1, "personnal_life/professionnal_life/JobCards/policier.png"),
    "prof_anglais": lambda: ProfJob("prof anglais", 2, 2, "personnal_life/professionnal_life/JobCards/prof_anglais.png"),
    "prof_francais": lambda: ProfJob("prof francais", 2, 2, "personnal_life/professionnal_life/JobCards/prof_francais.png"),
    "prof_histoire": lambda: ProfJob("prof histoire", 2, 2, "personnal_life/professionnal_life/JobCards/prof_histoire.png"),
    "prof_maths": lambda: ProfJob("prof maths", 2, 2, "personnal_life/professionnal_life/JobCards/prof_maths.png"),
    "serveur": lambda: ServeurJob("serveur", 1, 0, "personnal_life/professionnal_life/JobCards/serveur.png"),
    "stripteaser": lambda: StripTeaserJob("stripteaser", 1, 0, "personnal_life/professionnal_life/JobCards/stripteaser.png"),
    "grand_prof": lambda: GrandProfJob("grand prof", 3, "personnal_life/professionnal_life/JobCards/grand_prof.png"),

    # --- ÉTUDES ---
    "study_simple": lambda: StudyCard('simple', 1, "personnal_life/professionnal_life/StudyCards/study1.png"),
    "study_double": lambda: StudyCard('double', 2, "personnal_life/professionnal_life/StudyCards/study2.png"),

    # --- SALAIRES ---
    "salary_1": lambda: SalaryCard(1, "personnal_life/professionnal_life/SalaryCards/salary1.png"),
    "salary_2": lambda: SalaryCard(2, "personnal_life/professionnal_life/SalaryCards/salary2.png"),
    "salary_3": lambda: SalaryCard(3, "personnal_life/professionnal_life/SalaryCards/salary3.png"),
    "salary_4": lambda: SalaryCard(4, "personnal_life/professionnal_life/SalaryCards/salary4.png"),

    # --- FLIRTS ---
    "flirt_bar": lambda: FlirtCard("bar", "personnal_life/flirts/bar.png"),
    "flirt_boite_de_nuit": lambda: FlirtCard("boite de nuit", "personnal_life/flirts/boite_de_nuit.png"),
    "flirt_cinema": lambda: FlirtCard("cinema", "personnal_life/flirts/cinema.png"),
    "flirt_internet": lambda: FlirtCard("internet", "personnal_life/flirts/internet.png"),
    "flirt_parc": lambda: FlirtCard("parc", "personnal_life/flirts/parc.png"),
    "flirt_restaurant": lambda: FlirtCard("restaurant", "personnal_life/flirts/restaurant.png"),
    "flirt_theatre": lambda: FlirtCard("theatre", "personnal_life/flirts/theatre.png"),
    "flirt_zoo": lambda: FlirtCard("zoo", "personnal_life/flirts/zoo.png"),

    # --- FLIRTS AVEC ENFANT ---
    "flirt_child_camping": lambda: FlirtWithChildCard("camping", "personnal_life/flirts/camping.png"),
    "flirt_child_hotel": lambda: FlirtWithChildCard("hotel", "personnal_life/flirts/hotel.png"),

    # --- MARIAGES ---
    "mariage_corps_nuds": lambda: MarriageCard("corps-nuds", "personnal_life/mariages/mariage_corps_nuds.png"),
    "mariage_montcuq": lambda: MarriageCard("montcuq", "personnal_life/mariages/mariage_montcuq.png"),
    "mariage_monteton": lambda: MarriageCard("monteton", "personnal_life/mariages/mariage_monteton.png"),
    "mariage_sainte_vierge": lambda: MarriageCard("sainte-vierge", "personnal_life/mariages/mariage_sainte_vierge.png"),
    "mariage_fourqueux": lambda: MarriageCard("fourqueux", "personnal_life/mariages/mariage_fourqueux.png"),

    # --- ADULTÈRE ---
    "adultere": lambda: AdulteryCard("personnal_life/mariages/adultere.png"),

    # --- ENFANTS ---
    "child_diana": lambda: DianaChild("diana", "personnal_life/children/diana.png"),
    "child_harry": lambda: HarryChild("harry", "personnal_life/children/harry.png"),
    "child_hermione": lambda: HermioneChild("hermione", "personnal_life/children/hermione.png"),
    "child_lara": lambda: LaraChild("lara", "personnal_life/children/lara.png"),
    "child_leia": lambda: LeiaChild("leia", "personnal_life/children/leia.png"),
    "child_luigi": lambda: LuigiChild("luigi", "personnal_life/children/luigi.png"),
    "child_luke": lambda: LukeChild("luke", "personnal_life/children/luke.png"),
    "child_mario": lambda: MarioChild("mario", "personnal_life/children/mario.png"),
    "child_rocky": lambda: RockyChild("rocky", "personnal_life/children/rocky.png"),
    "child_zelda": lambda: ZeldaChild("zelda", "personnal_life/children/zelda.png"),

    # --- ANIMAUX ---
    "animal_chat": lambda: AnimalCard("chat", 1, "aquisition_cards/animals/chat.png"),
    "animal_chien": lambda: AnimalCard("chien", 1, "aquisition_cards/animals/chien.png"),
    "animal_lapin": lambda: AnimalCard("lapin", 1, "aquisition_cards/animals/lapin.png"),
    "animal_licorne": lambda: AnimalCard("licorne", 3, "aquisition_cards/animals/licorne.png"),
    "animal_poussin": lambda: AnimalCard("poussin", 1, "aquisition_cards/animals/poussin.png"),

    # --- MAISONS ---
    "house_petite": lambda: HouseCard('petite', 6, 1, "aquisition_cards/houses/maison1.png"),
    "house_moyenne": lambda: HouseCard('moyenne', 8, 2, "aquisition_cards/houses/maison2.png"),
    "house_grande": lambda: HouseCard('grande', 10, 3, "aquisition_cards/houses/maison3.png"),

    # --- VOYAGES ---
    "trip_le_caire": lambda: TravelCard("aquisition_cards/trip/le_caire.png"),
    "trip_londres": lambda: TravelCard("aquisition_cards/trip/londres.png"),
    "trip_new_york": lambda: TravelCard("aquisition_cards/trip/new_york.png"),
    "trip_rio": lambda: TravelCard("aquisition_cards/trip/rio.png"),
    "trip_sydney": lambda: TravelCard("aquisition_cards/trip/sydney.png"),

    # --- CARTES SPÉCIALES ---
    "troc": lambda: TrocCard("special_cards/troc.png"),
    "tsunami": lambda: TsunamiCard("special_cards/tsunami.png"),
    "heritage": lambda: HeritageCard("special_cards/heritage.png", 3),
    "super_heritage": lambda: HeritageCard("special_cards/super_heritage.png", 5),
    "piston": lambda: PistonCard("special_cards/piston.png"),
    "anniversaire": lambda: AnniversaireCard("special_cards/anniversaire.png"),
    "casino": lambda: CasinoCard("special_cards/casino.png"),
    "chance": lambda: ChanceCard("special_cards/chance.png"),
    "etoile_filante": lambda: EtoileFilanteCard("special_cards/etoile_filante.png"),
    "vengeance": lambda: VengeanceCard("special_cards/vengeance.png"),
    "arc_en_ciel": lambda: ArcEnCielCard("special_cards/arc_en_ciel.png"),

    # --- COUPS DURS ---
    "accident": lambda: AccidentCard("hardship_cards/accident.png"),
    "burnout": lambda: BurnOutCard("hardship_cards/burnout.png"),
    "divorce": lambda: DivorceCard("hardship_cards/divorce.png"),
    "tax": lambda: TaxCard("hardship_cards/tax.png"),
    "licenciement": lambda: LicenciementCard("hardship_cards/licenciement.png"),
    "maladie": lambda: MaladieCard("hardship_cards/maladie.png"),
    "redoublement": lambda: RedoublementCard("hardship_cards/redoublement.png"),
    "prison": lambda: PrisonCard("hardship_cards/prison.png"),
    "attentat": lambda: AttentatCard("hardship_cards/attentat.png"),

    # --- AUTRES ---
    "legion": lambda: LegionCard(3, "personnal_life/professionnal_life/legion.png"),
    "price": lambda: PriceCard(4, "personnal_life/professionnal_life/price.png"),

    ###################################################################################
    # --- EXTENTIONS CLASSIQUE ---   
    ###################################################################################         
    # --- MÉTIERS ---
    "prof_education_sexuelle": lambda: ProfJob("prof education sexuelle", 2, 2, "personnal_life/professionnal_life/JobCards/prof_education_sexuelle.png"),
    "youtubeur": lambda: YoutuberJob("youtubeur", 4, 0, "personnal_life/professionnal_life/JobCards/youtubeur.png"),
    "coiffeur": lambda: CoiffeurJob("coiffeur", 1, 1, "personnal_life/professionnal_life/JobCards/coiffeur.png"),
    "deejay": lambda: DeejayJob("deejay", 2, 0, "personnal_life/professionnal_life/JobCards/deejay.png"),

    # --- ÉTUDES ---

    # --- SALAIRES ---

    # --- FLIRTS ---

    # --- FLIRTS AVEC ENFANT ---

    # --- MARIAGES ---

    # --- ADULTÈRE ---

    # --- ENFANTS ---

    # --- ANIMAUX ---

    # --- MAISONS ---

    # --- VOYAGES ---

    # --- CARTES SPÉCIALES ---
    "muguet": lambda: MuguetCard("special_cards/muguet.png"),

    # --- COUPS DURS ---

    # --- AUTRES ---

    ###################################################################################        
    # --- EXTENTIONS GRIL POWER ---            
    ###################################################################################
    # --- MÉTIERS ---
    "architecte_f": lambda: ArchitecteJob("architecte", 3, 4, "personnal_life/professionnal_life/JobCards/architecte_f.png"),
    "astronaute_f": lambda: AstronauteJob("astronaute", 4, 6, "personnal_life/professionnal_life/JobCards/astronaute_f.png"),
    "avocate": lambda: AvocatJob("avocat", 3, 4, "personnal_life/professionnal_life/JobCards/avocate.png"),
    "bandit_f": lambda: BanditJob("bandit", 4, 0, "personnal_life/professionnal_life/JobCards/bandit_f.png"),
    "barmaid": lambda: BarmanJob("barmaid", 1, 0, "personnal_life/professionnal_life/JobCards/barmaid.png"),
    "cheffe_des_ventes": lambda: ChefDesVentesJob("cheffe des ventes", 3, 3, "personnal_life/professionnal_life/JobCards/cheffe_des_ventes.png"),
    "cheffe_des_achats": lambda: ChefDesAchatsJob("cheffe des achats", 3, 3, "personnal_life/professionnal_life/JobCards/cheffe_des_achats.png"),
    "chercheuse": lambda: ChercheurJob("chercheuse", 2, 6, "personnal_life/professionnal_life/JobCards/chercheuse.png"),
    "chirurgienne": lambda: ChirurgienJob("chirurgienne", 4, 6, "personnal_life/professionnal_life/JobCards/chirurgienne.png"),
    "designeuse": lambda: DesignerJob("designeuse", 3, 4, "personnal_life/professionnal_life/JobCards/designeuse.png"),
    "ecrivaine": lambda: EcrivainJob("ecrivaine", 1, 0, "personnal_life/professionnal_life/JobCards/ecrivaine.png"),
    "garagiste_f": lambda: GaragisteJob("garagiste", 2, 1, "personnal_life/professionnal_life/JobCards/garagiste_f.png"),
    "gourou_f": lambda: GourouJob("gourou", 3, 0, "personnal_life/professionnal_life/JobCards/gourou_f.png"),
    "jardiniere": lambda: JardinierJob("jardiniere", 1, 1, "personnal_life/professionnal_life/JobCards/jardiniere.png"),
    "journaliste_f": lambda: JournalisteJob("journaliste", 2, 3, "personnal_life/professionnal_life/JobCards/journaliste_f.png"),
    "medecin_f": lambda: MedecinJob("médecin", 4, 6, "personnal_life/professionnal_life/JobCards/medecin_f.png"),
    "voyante": lambda: MediumJob("voyante", 1, 0, "personnal_life/professionnal_life/JobCards/voyante.png"),
    "militaire_f": lambda: MilitaireJob("militaire", 1, 0, "personnal_life/professionnal_life/JobCards/militaire_f.png"),
    "pharmacienne": lambda: PharmacienJob("pharmacienne", 3, 5, "personnal_life/professionnal_life/JobCards/pharmacienne.png"),
    "pilote_de_ligne_f": lambda: PiloteDeLigneJob("pilote de ligne", 4, 5, "personnal_life/professionnal_life/JobCards/pilote_de_ligne_f.png"),
    "pizzaiola": lambda: PizzaioloJob("pizzaiola", 2, 0, "personnal_life/professionnal_life/JobCards/pizzaiola.png"),
    "plombiere": lambda: PlombierJob("plombiere", 1, 1, "personnal_life/professionnal_life/JobCards/plombiere.png"),
    "policiere": lambda: PolicierJob("policiere", 1, 1, "personnal_life/professionnal_life/JobCards/policiere.png"),
    "prof_de_chimie": lambda: ProfJob("prof de chimie", 2, 2, "personnal_life/professionnal_life/JobCards/prof_de_chimie.png"),
    "prof_de_geo": lambda: ProfJob("prof de geo", 2, 2, "personnal_life/professionnal_life/JobCards/prof_de_geo.png"),
    "prof_de_musique": lambda: ProfJob("prof musique", 2, 2, "personnal_life/professionnal_life/JobCards/prof_de_musique.png"),
    "prof_de_philo": lambda: ProfJob("prof philo", 2, 2, "personnal_life/professionnal_life/JobCards/prof_de_philo.png"),
    "serveuse": lambda: ServeurJob("serveuse", 1, 0, "personnal_life/professionnal_life/JobCards/serveuse.png"),
    "stripteaseuse": lambda: StripTeaserJob("stripteaseuse", 1, 0, "personnal_life/professionnal_life/JobCards/stripteaseuse.png"),
    "grand_prof_f": lambda: GrandProfJob("grand prof", 3, "personnal_life/professionnal_life/JobCards/grand_prof_f.png"),
    
    # --- ÉTUDES ---

    # --- SALAIRES ---

    # --- FLIRTS ---
    "flirt_manif": lambda: FlirtCard("manif", "personnal_life/flirts/manif.png"),

    # --- FLIRTS AVEC ENFANT ---
    "flirt_child_bibliotheque": lambda: FlirtWithChildCard("bibliotheque", "personnal_life/flirts/bibliotheque.png"),
    # --- MARIAGES ---

    # --- ADULTÈRE ---

    # --- ENFANTS ---
    "child_angela": lambda: AngelaChild("angela", "personnal_life/children/angela.png"),
    "child_beatrix": lambda: BeatrixChild("beatrix", "personnal_life/children/beatrix.png"),
    "child_daenerys": lambda: DaenerysChild("daenerys", "personnal_life/children/daenerys.png"),
    "child_louise": lambda: LouiseChild("louise", "personnal_life/children/louise.png"),
    "child_olympe": lambda: OlympeChild("olympe", "personnal_life/children/olympe.png"),
    "child_simone": lambda: SimoneChild("simone", "personnal_life/children/simone.png"),
    
    # --- ANIMAUX ---
    "animal_crapaud": lambda: AnimalCard("crapaud", 1, "aquisition_cards/animals/crapaud.png"),
    "animal_dragon": lambda: DragonAnimal("dragon", 1, "aquisition_cards/animals/dragon.png"),
    # --- AQUISITION ---
    "ticket_concert": lambda: ConcertTicket(1, 1, "aquisition_cards/other/place_de_concert.png"),
    "sabre": lambda: SabreCard(1, 1, "aquisition_cards/other/sabre.png"),
    "nounou": lambda: NounouCard(4, 1, "aquisition_cards/other/nounou.png"),

    # --- CARTES SPÉCIALES ---
    "girl_power": lambda: GirlPowerCard("special_cards/girl_power.png"),
    "soiree_entre_filles": lambda: SoireeEntreFilleCard("special_cards/soiree_entre_filles.png"),
    "coup_de_foudre": lambda: CoupDeFoudreCard("special_cards/coup_de_foudre.png"),
    "erreur_detiquetage": lambda: ErreurDetiquetageCard("special_cards/erreur_detiquetage.png"),
    "cliche_metier": lambda: ClicheMetier("special_cards/cliche_metier.png"),
    "cliche_flirt": lambda: ClicheFlirt("special_cards/cliche_flirt.png"),
    "cliche_accident": lambda: ClicheAccident("special_cards/cliche_accident.png"),
    "egalite_de_salaire": lambda: EgaliteDesSalaireCard("special_cards/egalite_de_salaire.png"),
    "redistribution_des_taches": lambda: RedistributionDesTachesCard("special_cards/redistribution_des_taches.png"),

    # --- COUPS DURS ---
    "charge_mentale": lambda: ChargeMentalHardhip("hardship_cards/charge_mentale.png"),
    "gynocratie": lambda: GynocratieHardship("hardship_cards/gynocratie.png"),
    "phallocratie": lambda: PhalocratieHardship("hardship_cards/phallocratie.png"),
    "plafond_de_verre": lambda: PlafondDeVerreHardship("hardship_cards/plafond_de_verre.png"),
    "porc": lambda: PorcHardship("hardship_cards/porc.png"),
    "taches_menageres": lambda: TachesMenageresHardship("hardship_cards/taches_menageres.png"),

    # --- AUTRES ---

    ###################################################################################
    # --- EXTENTIONS LUXE ---            
    ###################################################################################
    # --- MÉTIERS ---

    # --- ÉTUDES ---

    # --- SALAIRES ---

    # --- FLIRTS ---

    # --- FLIRTS AVEC ENFANT ---

    # --- MARIAGES ---

    # --- ADULTÈRE ---

    # --- ENFANTS ---

    # --- ANIMAUX ---

    # --- MAISONS ---

    # --- VOYAGES ---

    # --- CARTES SPÉCIALES ---
    
    # --- COUPS DURS ---

    # --- AUTRES ---

    ###################################################################################
    # --- EXTENTIONS FANTASTIQUE ---            
    ###################################################################################
    # --- MÉTIERS ---

    # --- ÉTUDES ---

    # --- SALAIRES ---

    # --- FLIRTS ---

    # --- FLIRTS AVEC ENFANT ---

    # --- MARIAGES ---

    # --- ADULTÈRE ---

    # --- ENFANTS ---

    # --- ANIMAUX ---

    # --- MAISONS ---

    # --- VOYAGES ---

    # --- CARTES SPÉCIALES ---
    
    # --- COUPS DURS ---

    # --- AUTRES ---

    ###################################################################################
    # --- EXTENTIONS TRASH ---            
    ###################################################################################
    # --- MÉTIERS ---

    # --- ÉTUDES ---

    # --- SALAIRES ---

    # --- FLIRTS ---

    # --- FLIRTS AVEC ENFANT ---

    # --- MARIAGES ---

    # --- ADULTÈRE ---

    # --- ENFANTS ---

    # --- ANIMAUX ---

    # --- MAISONS ---

    # --- VOYAGES ---

    # --- CARTES SPÉCIALES ---
    
    # --- COUPS DURS ---

    # --- AUTRES ---

    ###################################################################################
    # --- EXTENTIONS APOCALYPSE ---            
    ###################################################################################
    # --- MÉTIERS ---

    # --- ÉTUDES ---

    # --- SALAIRES ---

    # --- FLIRTS ---

    # --- FLIRTS AVEC ENFANT ---

    # --- MARIAGES ---

    # --- ADULTÈRE ---

    # --- ENFANTS ---

    # --- ANIMAUX ---

    # --- MAISONS ---

    # --- VOYAGES ---

    # --- CARTES SPÉCIALES ---
    
    # --- COUPS DURS ---

    # --- AUTRES ---
}



class CardFactory:
    """Factory pour créer les cartes"""
    @classmethod
    def create_custom_deck(cls, config: dict) -> List['Card']:
        """Crée un deck basé sur une configuration personnalisée"""
        deck = []
        
        # Mapping des IDs vers les fonctions de création
        for card_id, count in config.items():
            if card_id in card_builders:
                for _ in range(count):
                    deck.append(card_builders[card_id]())
        
        return deck

def get_game_state_for_player(game: 'Game' , player_id):
    """Retourne l'état du jeu adapté pour un joueur spécifique"""
    print("[start] : get_game_state_for_player")
    game_state = game.to_dict()
    print(game_state)

    return game_state

def check_game():
    print("[start]: check_game")
    session_info = player_sessions.get(request.sid)
    
    if not session_info:
        emit('error', {'message': 'Session non trouvée'})
        return
    
    game_id = session_info['game_id']
    player_id = session_info['player_id']
    
    if game_id not in games:
        emit('error', {'message': 'Partie non trouvée'})
        return
    
    game: 'Game' = games[game_id]
    return game.current_player, game, game_id

def update_all_player(game: 'Game', message):
    """Fonction legacy - redirige vers la méthode de la classe Game"""
    print("[start]: update_all_player (legacy)")
    game.broadcast_update(message)


def get_card_by_id(card_id, deck: list['Card']):
    """récupère une carte dans le deck par son id"""
    print("[start]: get_card_by_id")
    researched_card = None
    for card in deck:
        if card.id == card_id:
            researched_card = card
            break

    if not researched_card:
        emit('error', {'message': 'Carte non trouvée', "debug": "get_card_by_id"})
    return researched_card