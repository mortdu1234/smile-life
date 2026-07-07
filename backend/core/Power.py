from enum import Enum

class Power(Enum):
    """Enum des différents pouvoirs"""
    NO_FIRE = "no_fire" # ne peux pas recevoir de licenciement
    FIRST_HOUSE_FREE = "first_house_free" # la première maison posée est gratuite
    NO_DIVORCE = "no_divorce" # ne peux pas recevoir de divorce
    NO_TAX = "no_tax" # ne peux pas recevoir de taxe
    HAS_BEEN_BANDIT = "has_been_bandit" # ce joueur a été bandit dans la partie
    CAN_BE_PRICED = "can_be_priced" # peut recevoir un grand prix d'excellence
    NO_MALADIE = "no_maladie" # ne peux pas recevoir de maladie
    INFINITE_STUDY = "infinite_study" # peut étudier a l'infini
    NO_ACCIDENT = "no_accident" # ne peux pas recevoir d'accident
    NO_GOUROU = "no_gourou" # ne peux pas avoir de gourou dans la partie
    NO_ATTENTAT = "no_attentat" # ne peux pas y avoir un attentat dans la partie
    TRAVEL_FREE = "travel_free" # les voyages sont gratuits
    NO_BANDIT = "no_bandit" # ne peux pas avoir de bandit dans la partie
    INFINITE_FLIRT = "infinite_flirt" # peut flirter a l'infini
    NO_REDOUBLEMENT = "no_redoublement" # ne peux pas recevoir de redoublement
    NO_BURNOUT  = "no_burnout" # ne peux pas recevoir de carte burnout
    MAX_HAND_CARD_6 = "max_hand_card_6" # peut avoir jusqu'a 6 cartes en main
    MAX_HAND_CARD_5 = "max_hand_card_5" # peut avoir jusqu'a 5 cartes en main
    GYNOCRATIE = "gynocratie" # les smiles des enfants garçons sont divisés par 2
    PHALOCRATIE = "phalocratie" # les smiles des enfants filles sont divisés par 2
    JOB_MAX_STUDY_5 = "job_max_study_5" # le joueur peut avoir un job avec un niveau d'étude maximum de 5
    JOB_MAX_STUDY_4 = "job_max_study_4" # le joueur peut avoir un job avec un niveau d'étude maximum de 4
    CHILDREN_PROTECTED = "children_protected" # les enfants du joueur sont protégés de tous les malus