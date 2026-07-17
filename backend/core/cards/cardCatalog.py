"""
Catalogue statique des cartes.
Fournit id, label lisible et catégorie pour chaque entrée du registre.
Utilisé par le frontend (overlay de composition de deck).
"""
from __future__ import annotations

from collections import OrderedDict

TYPE1_ORDER = ["Base", "Extension simple", "Girl-Power", "Apocalypse", "Fantastique"]

CATALOG: list[dict] = [
    #########################################################################################
    # ── Fantastique ──────────────────────────────────────────────────────────────
    #########################################################################################
    {"id": "roles_ange", "label": "Ange", "category": ["Fantastique", "Roles"]},
    {"id": "roles_vampire", "label": "Vampire", "category": ["Fantastique", "Roles"]},
    {"id": "roles_sorciere", "label": "Sorcière", "category": ["Fantastique", "Roles"]},
    {"id": "roles_sirene", "label": "Sirène", "category": ["Fantastique", "Roles"]},
    {"id": "roles_mutant", "label": "Mutant", "category": ["Fantastique", "Roles"]},
    {"id": "roles_magicien", "label": "Magicien", "category": ["Fantastique", "Roles"]},
    {"id": "roles_loupgarou", "label": "Loup-Garou", "category": ["Fantastique", "Roles"]},
    {"id": "roles_fee", "label": "Fée", "category": ["Fantastique", "Roles"]},
    {"id": "roles_demon", "label": "Démon", "category": ["Fantastique", "Roles"]},
    {"id": "roles_chasseur", "label": "Chasseur", "category": ["Fantastique", "Roles"]},
        

    {"id": "malefice__alcatras", "label": "Alcatras", "category": ["Fantastique", "Maléfices"]},
    {"id": "malefice__sacrapas", "label": "Sacrapas", "category": ["Fantastique", "Maléfices"]},
    {"id": "malefice__restataplas", "label": "Restataplas", "category": ["Fantastique", "Maléfices"]},
    {"id": "malefice__minus_miserablis", "label": "Minus Miserablis", "category": ["Fantastique", "Maléfices"]},
    {"id": "malefice__maxus_miserablis", "label": "Maxus Miserablis", "category": ["Fantastique", "Maléfices"]},
    {"id": "malefice__mano_negra", "label": "Mano Negra", "category": ["Fantastique", "Maléfices"]},
    {"id": "malefice__desenchantement", "label": "Désenchantement", "category": ["Fantastique", "Maléfices"]},
    {"id": "malefice__cas_burnas", "label": "Cas Burnas", "category": ["Fantastique", "Maléfices"]},
    {"id": "malefice__bis_repetitas", "label": "Bis Repetitas", "category": ["Fantastique", "Maléfices"]},
    {"id": "malefice__aveuglement", "label": "Aveuglement", "category": ["Fantastique", "Maléfices"]},
    # ── Objet Magique ──────────────────────────────────────────────────────────────   
    {"id": "objet_magique__amulette", "label": "Amulette", "category": ["Fantastique", "Objets Magiques"]},
    {"id": "objet_magique__anneau_de_pouvoir", "label": "Anneau de Pouvoir", "category": ["Fantastique", "Objets Magiques"]},
    {"id": "objet_magique__baguette_magique", "label": "Baguette Magique", "category": ["Fantastique", "Objets Magiques"]},
    {"id": "objet_magique__balai", "label": "Balai", "category": ["Fantastique", "Objets Magiques"]},
    {"id": "objet_magique__boule_de_cristal", "label": "Boule de Cristal", "category": ["Fantastique", "Objets Magiques"]},
    {"id": "objet_magique__miroir", "label": "Miroir", "category": ["Fantastique", "Objets Magiques"]},
    {"id": "objet_magique__lasso_magique", "label": "Lasso Magique", "category": ["Fantastique", "Objets Magiques"]},
    {"id": "objet_magique__lampe_magique", "label": "Lampe Magique", "category": ["Fantastique", "Objets Magiques"]},
    {"id": "objet_magique__grimoire", "label": "Grimoire", "category": ["Fantastique", "Objets Magiques"]},
    {"id": "objet_magique__flute_enchantee", "label": "Flûte Enchantée", "category": ["Fantastique", "Objets Magiques"]},
    {"id": "objet_magique__chaudron", "label": "Chaudron", "category": ["Fantastique", "Objets Magiques"]},
    {"id": "objet_magique__cape_invisible", "label": "Cape Invisible", "category": ["Fantastique", "Objets Magiques"]},
    # ── Ephemeride ──────────────────────────────────────────────────────────────
    {"id": "ephemeride__eclipse",  "label": "eclipse",       "category": ["Fantastique", "Ephemeride"]},
    {"id": "ephemeride__equinoxe",  "label": "equinoxe",       "category": ["Fantastique", "Ephemeride"]},
    {"id": "ephemeride__lune_bleu",  "label": "lune_bleu",       "category": ["Fantastique", "Ephemeride"]},
    {"id": "ephemeride__lune_rouge",  "label": "lune_rouge",       "category": ["Fantastique", "Ephemeride"]},
    {"id": "ephemeride__pleine_lune",  "label": "pleine_lune",       "category": ["Fantastique", "Ephemeride"]},
    # ── Potions ────────────────────────────────────────────────────────────────
    {"id": "potion__amour_eternel",  "label": "Potion Amour Eternel",       "category": ["Fantastique", "Potion"]},
    {"id": "potion__argent",  "label": "Potion Argent",       "category": ["Fantastique", "Potion"]},
    {"id": "potion__chance",  "label": "Potion Chance",       "category": ["Fantastique", "Potion"]},
    {"id": "potion__epousaille",  "label": "Potion Epousaille",       "category": ["Fantastique", "Potion"]},
    {"id": "potion__excellence",  "label": "Potion Excellence",       "category": ["Fantastique", "Potion"]},
    {"id": "potion__fertilite",  "label": "Potion Fertilité",       "category": ["Fantastique", "Potion"]},
    {"id": "potion__interim",  "label": "Potion Interim",       "category": ["Fantastique", "Potion"]},
    {"id": "potion__resurrection",  "label": "Potion Résurrection",       "category": ["Fantastique", "Potion"]},
    {"id": "potion__ristournelle",  "label": "Potion Ristournelle",       "category": ["Fantastique", "Potion"]},
    {"id": "potion__savoir",  "label": "Potion Savoir",       "category": ["Fantastique", "Potion"]},
    {"id": "potion__vitalite",  "label": "Potion Vitalite",       "category": ["Fantastique", "Potion"]},
        
    # ── Enfants ───────────────────────────────────────────────────────────────
    {"id": "peter",      "label": "Peter",                 "category": ["Fantastique", "Enfants"]},
    {"id": "merlin",      "label": "Merlin",                 "category": ["Fantastique", "Enfants"]},
    {"id": "buffy",      "label": "Buffy",                 "category": ["Fantastique", "Enfants"]},
    # ── Animaux ───────────────────────────────────────────────────────────────
    {"id": "phoenix",      "label": "Phoenix",                  "category": ["Fantastique", "Animaux"]},
    {"id": "rat",      "label": "Rat",                          "category": ["Fantastique", "Animaux"]},
    {"id": "hibou",      "label": "Hibou",                      "category": ["Fantastique", "Animaux"]},
    {"id": "chauve_sourie",      "label": "Chauve Sourie",                 "category": ["Fantastique", "Animaux"]},
    # ── Acquisitions ──────────────────────────────────────────────────────────
    {"id": "travel__transylvanie",  "label": "Transylvanie",        "category": ["Fantastique", "Acquisitions"]},
    {"id": "travel__ecosse",  "label": "Ecosse",        "category": ["Fantastique", "Acquisitions"]},
    {"id": "travel__atlantide",  "label": "Atlantide",        "category": ["Fantastique", "Acquisitions"]},
    {"id": "travel__salem",  "label": "Salem",        "category": ["Fantastique", "Acquisitions"]},
    # ── Épreuves ──────────────────────────────────────────────────────────────
    # ── Flirts ────────────────────────────────────────────────────────────────
    # ── Métiers ───────────────────────────────────────────────────────────────   
    # ── Autres ────────────────────────────────────────────────────────────────
    # ── Spéciales ─────────────────────────────────────────────────────────────
    #########################################################################################
    # ── Base ──────────────────────────────────────────────────────────────
    #########################################################################################    
    # ── Salaires ──────────────────────────────────────────────────────────────
    {"id": "salary__1",  "label": "Salaire niv. 1",       "category": ["Base", "Salaires"]},
    {"id": "salary__2",  "label": "Salaire niv. 2",       "category": ["Base", "Salaires"]},
    {"id": "salary__3",  "label": "Salaire niv. 3",       "category": ["Base", "Salaires"]},
    {"id": "salary__4",  "label": "Salaire niv. 4",       "category": ["Base", "Salaires"]},
    # ── Études ────────────────────────────────────────────────────────────────
    {"id": "study__1",   "label": "Étude niv. 1",         "category": ["Base", "Études"]},
    {"id": "study__2",   "label": "Étude niv. 2",         "category": ["Base", "Études"]},
    # ── Enfants ───────────────────────────────────────────────────────────────
    {"id": "diana",      "label": "Diana",                 "category": ["Base", "Enfants"]},
    {"id": "harry",      "label": "Harry",                 "category": ["Base", "Enfants"]},
    {"id": "hermione",   "label": "Hermione",              "category": ["Base", "Enfants"]},
    {"id": "lara",       "label": "Lara",                  "category": ["Base", "Enfants"]},
    {"id": "leia",       "label": "Leia",                  "category": ["Base", "Enfants"]},
    {"id": "luigi",      "label": "Luigi",                 "category": ["Base", "Enfants"]},
    {"id": "mario",      "label": "Mario",                 "category": ["Base", "Enfants"]},
    {"id": "luke",       "label": "Luke",                  "category": ["Base", "Enfants"]},
    {"id": "zelda",      "label": "Zelda",                 "category": ["Base", "Enfants"]},
    {"id": "rocky",      "label": "Rocky",                 "category": ["Base", "Enfants"]},
    # ── Animaux ───────────────────────────────────────────────────────────────
    {"id": "chien",      "label": "Chien",                 "category": ["Base", "Animaux"]},
    {"id": "chat",       "label": "Chat",                  "category": ["Base", "Animaux"]},
    {"id": "lapin",      "label": "Lapin",                 "category": ["Base", "Animaux"]},
    {"id": "poussin",    "label": "Poussin",               "category": ["Base", "Animaux"]},
    {"id": "licorne",    "label": "Licorne",               "category": ["Base", "Animaux"]},
    # ── Acquisitions ──────────────────────────────────────────────────────────
    {"id": "house__1",          "label": "Maison niv. 1",  "category": ["Base", "Acquisitions"]},
    {"id": "house__2",          "label": "Maison niv. 2",  "category": ["Base", "Acquisitions"]},
    {"id": "house__3",          "label": "Maison niv. 3",  "category": ["Base", "Acquisitions"]},
    {"id": "travel__le_caire",  "label": "Le Caire",        "category": ["Base", "Acquisitions"]},
    {"id": "travel__londre",    "label": "Londres",         "category": ["Base", "Acquisitions"]},
    {"id": "travel__new_york",  "label": "New York",        "category": ["Base", "Acquisitions"]},
    {"id": "travel__rio",       "label": "Rio",             "category": ["Base", "Acquisitions"]},
    {"id": "travel__sydney",    "label": "Sydney",          "category": ["Base", "Acquisitions"]},
    # ── Épreuves ──────────────────────────────────────────────────────────────
    {"id": "accident",      "label": "Accident",            "category": ["Base", "Épreuves"]},
    {"id": "maladie",       "label": "Maladie",             "category": ["Base", "Épreuves"]},
    {"id": "tax",           "label": "Impôts",              "category": ["Base", "Épreuves"]},
    {"id": "burnout",       "label": "Burn-out",            "category": ["Base", "Épreuves"]},
    {"id": "divorce",       "label": "Divorce",             "category": ["Base", "Épreuves"]},
    {"id": "licenciement",  "label": "Licenciement",        "category": ["Base", "Épreuves"]},
    {"id": "redoublement",  "label": "Redoublement",        "category": ["Base", "Épreuves"]},
    {"id": "prison",        "label": "Prison",              "category": ["Base", "Épreuves"]},
    {"id": "attentat",      "label": "Attentat",            "category": ["Base", "Épreuves"]},
    # ── Flirts ────────────────────────────────────────────────────────────────
    {"id": "flirt__bar",               "label": "Flirt – Bar",         "category": ["Base", "Flirts & Mariages"]},
    {"id": "flirt__boite_de_nuit",     "label": "Flirt – Boîte",       "category": ["Base", "Flirts & Mariages"]},
    {"id": "flirt__cinema",            "label": "Flirt – Cinéma",      "category": ["Base", "Flirts & Mariages"]},
    {"id": "flirt__internet",          "label": "Flirt – Internet",    "category": ["Base", "Flirts & Mariages"]},
    {"id": "flirt__parc",              "label": "Flirt – Parc",        "category": ["Base", "Flirts & Mariages"]},
    {"id": "flirt__restaurant",        "label": "Flirt – Restaurant",  "category": ["Base", "Flirts & Mariages"]},
    {"id": "flirt__theatre",           "label": "Flirt – Théâtre",     "category": ["Base", "Flirts & Mariages"]},
    {"id": "flirt__zoo",               "label": "Flirt – Zoo",         "category": ["Base", "Flirts & Mariages"]},
    {"id": "flirt_with_child__hotel",  "label": "Flirt enfant – Hôtel",       "category": ["Base", "Flirts & Mariages"]},
    {"id": "flirt_with_child__camping","label": "Flirt enfant – Camping",     "category": ["Base", "Flirts & Mariages"]},
    {"id": "adultery",                 "label": "Adultère",            "category": ["Base", "Flirts & Mariages"]},
    {"id": "marriage__corps_nuds",     "label": "Mariage Corps Nus",   "category": ["Base", "Flirts & Mariages"]},
    {"id": "marriage__fourqueux",      "label": "Mariage Fourqueux",   "category": ["Base", "Flirts & Mariages"]},
    {"id": "marriage__montcuq",        "label": "Mariage Montcuq",     "category": ["Base", "Flirts & Mariages"]},
    {"id": "marriage__monteton",       "label": "Mariage Monteton",    "category": ["Base", "Flirts & Mariages"]},
    {"id": "marriage__sainte_vierge",  "label": "Mariage Sainte-Vierge","category": ["Base", "Flirts & Mariages"]},
    {"id": "marriage__bourg_la_reine",  "label": "Mariage Bourg-la-reine","category": ["Base", "Flirts & Mariages"]},
    # ── Métiers ───────────────────────────────────────────────────────────────
    {"id": "serveur",          "label": "Serveur",             "category": ["Base", "Métiers"]},
    {"id": "garagiste",        "label": "Garagiste",           "category": ["Base", "Métiers"]},
    {"id": "plombier",         "label": "Plombier",            "category": ["Base", "Métiers"]},
    {"id": "bandit",           "label": "Bandit",              "category": ["Base", "Métiers"]},
    {"id": "ecrivain",         "label": "Écrivain",            "category": ["Base", "Métiers"]},
    {"id": "pharmacien",       "label": "Pharmacien",          "category": ["Base", "Métiers"]},
    {"id": "architecte",       "label": "Architecte",          "category": ["Base", "Métiers"]},
    {"id": "militaire",        "label": "Militaire",           "category": ["Base", "Métiers"]},
    {"id": "medium",           "label": "Médium",              "category": ["Base", "Métiers"]},
    {"id": "journaliste",      "label": "Journaliste",         "category": ["Base", "Métiers"]},
    {"id": "chef_des_achats",  "label": "Chef des Achats",     "category": ["Base", "Métiers"]},
    {"id": "medecin",          "label": "Médecin",             "category": ["Base", "Métiers"]},
    {"id": "chirurgien",       "label": "Chirurgien",          "category": ["Base", "Métiers"]},
    {"id": "pilote",           "label": "Pilote de Ligne",     "category": ["Base", "Métiers"]},
    {"id": "astronaute",       "label": "Astronaute",          "category": ["Base", "Métiers"]},
    {"id": "avocat",           "label": "Avocat",              "category": ["Base", "Métiers"]},
    {"id": "barman",           "label": "Barman",              "category": ["Base", "Métiers"]},
    {"id": "chef_des_ventes",  "label": "Chef des Ventes",     "category": ["Base", "Métiers"]},
    {"id": "chercheur",        "label": "Chercheur",           "category": ["Base", "Métiers"]},
    {"id": "gourou",           "label": "Gourou",              "category": ["Base", "Métiers"]},
    {"id": "grand_prof",       "label": "Grand Professeur",    "category": ["Base", "Métiers"]},
    {"id": "designer",         "label": "Designer",            "category": ["Base", "Métiers"]},
    {"id": "jardinier",        "label": "Jardinier",           "category": ["Base", "Métiers"]},
    {"id": "pizzaiolo",        "label": "Pizzaïolo",           "category": ["Base", "Métiers"]},
    {"id": "policier",         "label": "Policier",            "category": ["Base", "Métiers"]},
    {"id": "prof__maths",      "label": "Prof de Maths",       "category": ["Base", "Métiers"]},
    {"id": "prof__francais",   "label": "Prof de Français",    "category": ["Base", "Métiers"]},
    {"id": "prof__anglais",    "label": "Prof d'Anglais",      "category": ["Base", "Métiers"]},
    {"id": "prof__histoire",   "label": "Prof d'Histoire",     "category": ["Base", "Métiers"]},
    {"id": "stripteaser",      "label": "Stripteaser",         "category": ["Base", "Métiers"]},
    # ── Autres ────────────────────────────────────────────────────────────────
    {"id": "legion",           "label": "Légion d'Honneur",    "category": ["Base", "Autres"]},
    {"id": "prix",             "label": "Prix",                "category": ["Base", "Autres"]},
    # ── Spéciales ─────────────────────────────────────────────────────────────
    {"id": "casino",           "label": "Casino",              "category": ["Base", "Spéciales"]},
    {"id": "arc_en_ciel",      "label": "Arc-en-ciel",         "category": ["Base", "Spéciales"]},
    {"id": "chance",           "label": "Chance",              "category": ["Base", "Spéciales"]},
    {"id": "etoile_filante",   "label": "Étoile Filante",      "category": ["Base", "Spéciales"]},
    {"id": "anniversaire",     "label": "Anniversaire",        "category": ["Base", "Spéciales"]},
    {"id": "tsunami",          "label": "Tsunami",             "category": ["Base", "Spéciales"]},
    {"id": "vengeance",        "label": "Vengeance",           "category": ["Base", "Spéciales"]},
    {"id": "piston",           "label": "Piston",              "category": ["Base", "Spéciales"]},
    {"id": "heritage",         "label": "Héritage",            "category": ["Base", "Spéciales"]},
    {"id": "troc",             "label": "Troc",                "category": ["Base", "Spéciales"]},
    #########################################################################################
    # ── Girl Power ──────────────────────────────────────────────────────────────
    #########################################################################################
    # ── Salaires ──────────────────────────────────────────────────────────────
    # ── Études ────────────────────────────────────────────────────────────────
    # ── Enfants ───────────────────────────────────────────────────────────────
    {"id": "olympe",     "label": "Olympe",                "category": ["Girl-Power", "Enfants"]},
    {"id": "simone",     "label": "Simone",                "category": ["Girl-Power", "Enfants"]},
    {"id": "angela",     "label": "Angela",                "category": ["Girl-Power", "Enfants"]},
    {"id": "beatrix",     "label": "Beatrix",                "category": ["Girl-Power", "Enfants"]},
    {"id": "daenerys",     "label": "Daenerys",                "category": ["Girl-Power", "Enfants"]},
    {"id": "louise",     "label": "Louise",                "category": ["Girl-Power", "Enfants"]}, 
    # ── Animaux ───────────────────────────────────────────────────────────────
    {"id": "crapaud",    "label": "Crapaud",               "category": ["Girl-Power", "Animaux"]},
    {"id": "dragon",    "label": "Dragon",               "category": ["Girl-Power", "Animaux"]},
    # ── Acquisitions ──────────────────────────────────────────────────────────
    {"id": "concert",  "label": "Concert",        "category": ["Girl-Power", "Acquisitions"]},
    {"id": "nounou",  "label": "Nounou",        "category": ["Girl-Power", "Acquisitions"]},
    {"id": "sabre",  "label": "Sabre",        "category": ["Girl-Power", "Acquisitions"]},

    # ── Épreuves ──────────────────────────────────────────────────────────────
    {"id": "charge_mentale",      "label": "Charge Mentale",            "category": ["Girl-Power", "Épreuves"]},
    {"id": "taches_menageres",      "label": "Tâches Ménagères",            "category": ["Girl-Power", "Épreuves"]},
    {"id": "porc",      "label": "Porc",            "category": ["Girl-Power", "Épreuves"]},
    {"id": "phalocratie",      "label": "Phalocratie",            "category": ["Girl-Power", "Épreuves"]},
    {"id": "gynocratie",      "label": "Gynocratie",            "category": ["Girl-Power", "Épreuves"]},
    {"id": "plafond_de_verre",      "label": "Plafond de Verre",            "category": ["Girl-Power", "Épreuves"]},
    # ── Flirts ────────────────────────────────────────────────────────────────
    {"id": "flirt__manif",               "label": "Flirt – manif",         "category": ["Girl-Power", "Flirts & Mariages"]},
    {"id": "flirt_with_child__bibliotheque",  "label": "Flirt enfant – bibliotheque",       "category": ["Girl-Power", "Flirts & Mariages"]},    
    # ── Métiers ───────────────────────────────────────────────────────────────
    {"id": "serveuse",          "label": "Serveure",             "category": ["Girl-Power", "Métiers"]},
    {"id": "garagiste_f",        "label": "Garagiste(f)",           "category": ["Girl-Power", "Métiers"]},
    {"id": "plombiere",         "label": "Plombière",            "category": ["Girl-Power", "Métiers"]},
    {"id": "bandit_f",           "label": "Bandit(f)",              "category": ["Girl-Power", "Métiers"]},
    {"id": "ecrivaine",         "label": "Écrivaine",            "category": ["Girl-Power", "Métiers"]},
    {"id": "pharmacienne",       "label": "Pharmacienne",          "category": ["Girl-Power", "Métiers"]},
    {"id": "architecte_f",       "label": "Architecte(f)",          "category": ["Girl-Power", "Métiers"]},
    {"id": "militaire_f",        "label": "Militaire(f)",           "category": ["Girl-Power", "Métiers"]},
    {"id": "voyante",           "label": "Voyante",              "category": ["Girl-Power", "Métiers"]},
    {"id": "journaliste_f",      "label": "Journaliste(f)",         "category": ["Girl-Power", "Métiers"]},
    {"id": "cheffe_des_achats",  "label": "Cheffe des Achats",     "category": ["Girl-Power", "Métiers"]},
    {"id": "medecin_f",          "label": "Médecin(f)",             "category": ["Girl-Power", "Métiers"]},
    {"id": "chirurgienne",       "label": "Chirurgienne",          "category": ["Girl-Power", "Métiers"]},
    {"id": "pilote_de_ligne_f",           "label": "Pilote de Ligne(f)",     "category": ["Girl-Power", "Métiers"]},
    {"id": "astronaute_f",       "label": "Astronaute(f)",          "category": ["Girl-Power", "Métiers"]},
    {"id": "avocate",           "label": "Avocate",              "category": ["Girl-Power", "Métiers"]},
    {"id": "barmaid",           "label": "Barmaid",              "category": ["Girl-Power", "Métiers"]},
    {"id": "cheffe_des_ventes",  "label": "Cheffe des Ventes",     "category": ["Girl-Power", "Métiers"]},
    {"id": "chercheuse",        "label": "Chercheuse",           "category": ["Girl-Power", "Métiers"]},
    {"id": "gourou_f",           "label": "Gourou(f)",              "category": ["Girl-Power", "Métiers"]},
    {"id": "grande_prof",       "label": "Grande Professeure",    "category": ["Girl-Power", "Métiers"]},
    {"id": "designeuse",         "label": "Designeuse",            "category": ["Girl-Power", "Métiers"]},
    {"id": "jardiniere",        "label": "Jardinière",           "category": ["Girl-Power", "Métiers"]},
    {"id": "pizzaiola",        "label": "Pizzaïola",           "category": ["Girl-Power", "Métiers"]},
    {"id": "policiere",         "label": "Policière",            "category": ["Girl-Power", "Métiers"]},
    {"id": "prof__chimie",      "label": "Prof de Chimie",       "category": ["Girl-Power", "Métiers"]},
    {"id": "prof__musique",   "label": "Prof de Musique",    "category": ["Girl-Power", "Métiers"]},
    {"id": "prof__philo",    "label": "Prof de Philo",      "category": ["Girl-Power", "Métiers"]},
    {"id": "prof__geo",        "label": "Prof de Géo",         "category": ["Girl-Power", "Métiers"]},
    {"id": "stripteaseuse",      "label": "Stripteaseuse",         "category": ["Girl-Power", "Métiers"]},   
    # ── Autres ────────────────────────────────────────────────────────────────
    # ── Spéciales ─────────────────────────────────────────────────────────────
    {"id": "cliche_accident",             "label": "Cliché Accident",                "category": ["Girl-Power", "Spéciales"]},
    {"id": "cliche_flirt",             "label": "Cliché Flirt",                "category": ["Girl-Power", "Spéciales"]},
    {"id": "coup_de_foudre",             "label": "Coup De Foudre",                "category": ["Girl-Power", "Spéciales"]},
    {"id": "egalite_salaire",             "label": "Egalité des Salaires",                "category": ["Girl-Power", "Spéciales"]},
    {"id": "soiree_entre_fille",             "label": "Soirée entre Filles",                "category": ["Girl-Power", "Spéciales"]},
    {"id": "girl_power",             "label": "Girl Power",                "category": ["Girl-Power", "Spéciales"]},
    {"id": "erreur_etiquetage",             "label": "Erreur Etiquetage",                "category": ["Girl-Power", "Spéciales"]},
    {"id": "redistribution_taches",             "label": "Redistribution des Taches",                "category": ["Girl-Power", "Spéciales"]},

    #########################################################################################
    # ── Trash ──────────────────────────────────────────────────────────────
    #########################################################################################
    # ── Salaires ──────────────────────────────────────────────────────────────
    # ── Études ────────────────────────────────────────────────────────────────
    # ── Enfants ───────────────────────────────────────────────────────────────
    # ── Animaux ───────────────────────────────────────────────────────────────
    # ── Acquisitions ──────────────────────────────────────────────────────────
    # ── Épreuves ──────────────────────────────────────────────────────────────
    # ── Flirts ────────────────────────────────────────────────────────────────
    # ── Métiers ───────────────────────────────────────────────────────────────   
    # ── Autres ────────────────────────────────────────────────────────────────
    # ── Spéciales ─────────────────────────────────────────────────────────────
    #########################################################################################
    # ── Vie de Luxe ──────────────────────────────────────────────────────────────
    #########################################################################################
    # ── Salaires ──────────────────────────────────────────────────────────────
    # ── Études ────────────────────────────────────────────────────────────────
    # ── Enfants ───────────────────────────────────────────────────────────────
    # ── Animaux ───────────────────────────────────────────────────────────────
    # ── Acquisitions ──────────────────────────────────────────────────────────
    # ── Épreuves ──────────────────────────────────────────────────────────────
    # ── Flirts ────────────────────────────────────────────────────────────────
    # ── Métiers ───────────────────────────────────────────────────────────────   
    # ── Autres ────────────────────────────────────────────────────────────────
    # ── Spéciales ─────────────────────────────────────────────────────────────
    #########################################################################################
    # ── Apocalypses ──────────────────────────────────────────────────────────────
    #########################################################################################
    # ── Salaires ──────────────────────────────────────────────────────────────
    # ── Études ────────────────────────────────────────────────────────────────
    # ── Enfants ───────────────────────────────────────────────────────────────
    # ── Animaux ───────────────────────────────────────────────────────────────
    # ── Acquisitions ──────────────────────────────────────────────────────────
    # ── Épreuves ──────────────────────────────────────────────────────────────
    # ── Flirts ────────────────────────────────────────────────────────────────
    # ── Métiers ───────────────────────────────────────────────────────────────   
    # ── Autres ────────────────────────────────────────────────────────────────
    # ── Spéciales ─────────────────────────────────────────────────────────────
    #########################################################################################
    # ── Autres ──────────────────────────────────────────────────────────────
    #########################################################################################
    # ── Salaires ──────────────────────────────────────────────────────────────
    # ── Études ────────────────────────────────────────────────────────────────
    # ── Enfants ───────────────────────────────────────────────────────────────
    # ── Animaux ───────────────────────────────────────────────────────────────
    # ── Acquisitions ──────────────────────────────────────────────────────────
    # ── Épreuves ──────────────────────────────────────────────────────────────
    # ── Flirts ────────────────────────────────────────────────────────────────
    # ── Métiers ───────────────────────────────────────────────────────────────   
    # ── Autres ────────────────────────────────────────────────────────────────
    # ── Spéciales ─────────────────────────────────────────────────────────────

]

def get_catalog() -> list[dict]:
    """Retourne la liste complète des cartes avec id, label, category."""
    return CATALOG


def get_catalog_by_category() -> dict[str, list[dict]]:
    """Retourne le catalogue regroupé par catégorie (ordre d'insertion conservé)."""
    result: dict[str, list[dict]] = OrderedDict()
    for card in CATALOG:
        t2 = card["category"][1]  # ← était card["category"], qui est une liste
        result.setdefault(t2, []).append(card)
    return result

def get_catalog_nested() -> dict[str, dict[str, list[dict]]]:
    """Retourne le catalogue groupé par type1 (extension) puis type2 (catégorie).
    Structure : { type1: { type2: [cards] } }
    """
    result: dict[str, dict[str, list[dict]]] = OrderedDict()
    for t1 in TYPE1_ORDER:
        result[t1] = OrderedDict()

    for card in CATALOG:
        t1, t2 = card["category"][0], card["category"][1]
        if t1 not in result:
            result[t1] = OrderedDict()
        result[t1].setdefault(t2, []).append(card)

    # Supprimer les type1 vides (extensions sans cartes encore)
    return OrderedDict((k, v) for k, v in result.items() if v)