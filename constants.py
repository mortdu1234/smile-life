from flask import Flask, request
from flask_socketio import SocketIO, emit
from card_classes import *
import os

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete_ici_changez_la'
socketio = SocketIO(app, cors_allowed_origins="*")

# Configuration pour servir les images
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'ressources')

# Stockage des parties et des joueurs connectés
games = {}
player_sessions = {}  # {session_id: {game_id, player_id}}


def get_game_state_for_player(game: Game , player_id):
    """Retourne l'état du jeu adapté pour un joueur spécifique"""
    print("[start] : get_game_state_for_player")
    game_state = game.to_dict()
    
    # Remplacer le deck complet par juste le nombre de cartes
    game_state['deck_count'] = len(game.deck)
    game_state.pop('deck', None)  # Retirer la liste complète du deck
    
    # Ajouter la dernière carte défaussée si elle existe
    if len(game.discard) > 0:
        game_state["last_discard"] = game.discard[-1].to_dict()
    else:
        game_state['last_discard'] = None

    return game_state

def apply_hardship_effect(game: Game, hardship_card, target_player, attacker_player):
    """Applique l'effet d'une carte malus sur un joueur cible"""
    print("[start] : apply_hardship_effect")
    hardship_type = hardship_card.hardship_type
    
    # Vérifier les immunités
    job = target_player.get_job()
    if job:
        immunities = {
            'accident': ['no_accident'],
            'maladie': ['no_illness', 'no_illness_extra_study'],
            'attentat': ['no_attentat'],
            'divorce': ['no_divorce'],
            'licenciement': ['no_fire_tax'],
            'impot': ['no_fire_tax']
        }
        
        if hardship_type in immunities:
            if job.power in immunities[hardship_type]:
                return False, f"{target_player.name} est protégé par son métier ({job.job_name})"
    
    print(hardship_type)
    # Appliquer les effets
    if hardship_type == 'accident':
        target_player.skip_turns = 1
        target_player.received_hardships.append(hardship_type)
        return True, f"{target_player.name} doit passer 1 tour"
    
    elif hardship_type == 'burnout':
        job_card = target_player.get_job() 
        if not job_card:
            return False, f"{target_player.name} n'a pas de métier"
        target_player.skip_turns = 1
        target_player.received_hardships.append(hardship_type)
        return True, f"{target_player.name} doit passer 1 tour"
    
    elif hardship_type == 'divorce':
        marriage_cards = [c for c in target_player.played["vie personnelle"] if isinstance(c, MarriageCard)]
        if marriage_cards:
            marriage_to_remove = marriage_cards[-1]
            target_player.remove_card_from_played(marriage_to_remove)
            game.discard.append(marriage_to_remove)
            
            adultery_cards = [c for c in target_player.played["vie personnelle"] if isinstance(c, AdulteryCard)]
            if adultery_cards:
                adultery = adultery_cards[0]
                target_player.remove_card_from_played(adultery)
                game.discard.append(adultery)
                
                children_cards = [c for c in target_player.played["vie personnelle"] if isinstance(c, ChildCard)]
                for child in children_cards:
                    target_player.remove_card_from_played(child)
                    game.discard.append(child)
                
                adultery_flirts = [c for c in target_player.played["cartes spéciales"] if isinstance(c, FlirtCard)]
                for flirt in adultery_flirts:
                    target_player.remove_card_from_played(flirt)
                    game.discard.append(flirt)
                
                target_player.received_hardships.append(hardship_type)
                return True, f"{target_player.name} a divorcé et perdu son adultère, ses enfants et ses flirts adultères"
            
            target_player.received_hardships.append(hardship_type)
            return True, f"{target_player.name} a divorcé"
        return False, f"{target_player.name} n'est pas marié"
    
    elif hardship_type == 'tax':
        job_card = target_player.get_job() 
        if not job_card:
            return False, f"{target_player.name} n'a pas de métier"
        salary_cards = [c for c in target_player.played["vie professionnelle"] if isinstance(c, SalaryCard)]
        print(f"salary_cards : {salary_cards}")
        if salary_cards:
            card_to_remove = salary_cards[-1]
            target_player.remove_card_from_played(card_to_remove)
            game.discard.append(card_to_remove)
            target_player.received_hardships.append(hardship_type)
            return True, f"{target_player.name} a perdu 1 salaire"
        return False, f"{target_player.name} n'a pas de salaire"
    
    elif hardship_type == 'licenciement':
        job_card = target_player.get_job() 
        if job_card:
            if job_card.job_name == "chercheur":
                handle_loose_chercheur_job()

            target_player.remove_card_from_played(job_card)
            game.discard.append(job_card)
            target_player.received_hardships.append(hardship_type)
            return True, f"{target_player.name} a été licencié"
        return False, f"{target_player.name} n'a pas de métier"
    
    elif hardship_type == 'maladie':
        target_player.skip_turns = 1
        target_player.received_hardships.append(hardship_type)
        return True, f"{target_player.name} est malade (passe 1 tour)"
    
    elif hardship_type == 'redoublement':
        job_card = target_player.get_job() 
        if job_card:
            return False, f"{target_player.name} a un métier"
        study_cards = [c for c in target_player.played["vie professionnelle"] if isinstance(c, StudyCard)]
        if study_cards:
            card_to_remove = study_cards[-1]
            target_player.remove_card_from_played(card_to_remove)
            game.discard.append(card_to_remove)
            target_player.received_hardships.append(hardship_type)
            return True, f"{target_player.name} a perdu une étude"
        return False, f"{target_player.name} n'a pas d'études à perdre"
    
    elif hardship_type == 'prison':
        target_player.skip_turns = 3
        target_player.received_hardships.append(hardship_type)
        return True, f"{target_player.name} est en prison pour 3 tours"
    
    elif hardship_type == 'attentat':
        print(game)
        players: list[Player] = game.players
        for p in players:
            print(f"recup enfant : {p.name}")
            children_cards = [c for c in p.played["vie personnelle"] if isinstance(c, ChildCard)]
            total_children_removed = len(children_cards)
            print(f"nombre d'enfant en moins : {total_children_removed}")
            for child in children_cards:
                p.remove_card_from_played(child)
                game.discard.append(child)
            

        attacker_player.received_hardships.append(hardship_type)
            
        if total_children_removed > 0:
            return True, f"Attentat ! des enfant(s)"
        else:
            return True, f"Attentat ! n'avait pas d'enfant"
    
    return True, f"Malus {hardship_type} appliqué à {target_player.name}"

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
    
    game = games[game_id]
    return player_id, game, game_id

@socketio.on('pick_card')
def give_card(data):
    """Donner une carte au joueur"""
    print("[start]: give_card")
    source = data.get('source', 'deck')
    player_id, game, game_id = check_game()

    player = game.players[player_id]
    
    if source == 'deck':
        if not game.deck:
            scores = [(p.name, p.calculate_smiles(), p.id) for p in game.players if p.connected]
            scores.sort(key=lambda x: x[1], reverse=True)
            print("[appel] : game_over")
            socketio.emit('game_over', {'scores': scores}, room=game_id)
            return
        
        card = game.deck.pop()
        player.hand.append(card)
        
        print(f"Joueur {player_id} a pris dans le deck, reste {len(game.deck)} cartes")
        update_all_player(game, "")

def next_player(game: Game):
    """Passe au joueur suivant"""
    print("[start]: next_player")
    if not (game.pending_special and game.pending_special.get('type') == 'arc_en_ciel'):
        print("Tour terminé, passage au joueur suivant")
        game.phase = 'draw'
        game.change_current_player()

def update_all_player(game, message):
    print("[start]: update_all_player")
    for p in game.players:
        if p.connected:
            print("[appel] : game_updated")
            socketio.emit('game_updated', {
                'game': get_game_state_for_player(game, p.id),
                'message': message
            }, room=p.session_id)

def get_card_by_id(card_id, deck: list[Card]):
    """récupère une carte dans le deck par son id"""
    print("[start]: get_card_by_id")
    researched_card = None
    for card in deck:
        if card.id == card_id:
            researched_card = card
            break

    if not researched_card:
        emit('error', {'message': 'Carte non trouvée'})
    return researched_card