import asyncio
import websockets
import json
import uuid
from typing import Dict, List, Optional
from cards import *
from players import *
from deck import deck
from game import game

class GameServer:
    def __init__(self):
        self.games: Dict[str, game] = {}
        self.clients: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.client_to_game: Dict[str, str] = {}
        self.client_to_player: Dict[str, str] = {}
        
    async def register_client(self, websocket, client_id: str):
        """Enregistrer un nouveau client"""
        self.clients[client_id] = websocket
        await self.send_message(websocket, {
            "type": "connection_confirmed",
            "client_id": client_id
        })
        
    async def unregister_client(self, client_id: str):
        """Désenregistrer un client"""
        if client_id in self.clients:
            # Retirer le joueur du jeu s'il était dans un jeu
            if client_id in self.client_to_game:
                game_id = self.client_to_game[client_id]
                player_name = self.client_to_player.get(client_id)
                if player_name and game_id in self.games:
                    self.games[game_id].remove_player(player_name)
                    await self.broadcast_game_state(game_id)
                del self.client_to_game[client_id]
            
            if client_id in self.client_to_player:
                del self.client_to_player[client_id]
            del self.clients[client_id]

    async def create_game(self, client_id: str) -> str:
        """Créer une nouvelle partie"""
        game_id = str(uuid.uuid4())[:8]
        self.games[game_id] = game()
        await self.send_message(self.clients[client_id], {
            "type": "game_created",
            "game_id": game_id
        })
        return game_id

    async def join_game(self, client_id: str, game_id: str, player_name: str):
        """Rejoindre une partie existante"""
        if game_id not in self.games:
            await self.send_message(self.clients[client_id], {
                "type": "error",
                "message": "Partie inexistante"
            })
            return
            
        game_instance = self.games[game_id]
        if len(game_instance.players) >= 5:
            await self.send_message(self.clients[client_id], {
                "type": "error",
                "message": "Partie pleine (maximum 5 joueurs)"
            })
            return
            
        # Vérifier si le nom est déjà pris
        for player in game_instance.players:
            if player.get_name == player_name:
                await self.send_message(self.clients[client_id], {
                    "type": "error",
                    "message": "Ce nom est déjà pris"
                })
                return
        
        game_instance.new_player(player_name)
        self.client_to_game[client_id] = game_id
        self.client_to_player[client_id] = player_name
        
        await self.send_message(self.clients[client_id], {
            "type": "joined_game",
            "game_id": game_id,
            "player_name": player_name
        })
        
        await self.broadcast_game_state(game_id)

    async def take_card_from_deck(self, client_id: str):
        """Piocher une carte du deck principal"""
        if client_id not in self.client_to_game:
            return
            
        game_id = self.client_to_game[client_id]
        player_name = self.client_to_player[client_id]
        game_instance = self.games[game_id]
        player = game_instance.get_players_by_name(player_name)
        
        if player:
            game_instance.take_card(game_instance.deck, player)
            await self.broadcast_game_state(game_id)

    async def play_card(self, client_id: str, card_index: int):
        """Jouer une carte de la main vers le plateau"""
        if client_id not in self.client_to_game:
            return
            
        game_id = self.client_to_game[client_id]
        player_name = self.client_to_player[client_id]
        game_instance = self.games[game_id]
        player = game_instance.get_players_by_name(player_name)
        
        if player and 0 <= card_index < len(player.hand):
            card = player.hand[card_index]
            player.add_card_to_board(card)
            await self.broadcast_game_state(game_id)

    def serialize_card(self, card: Cards) -> dict:
        """Sérialiser une carte pour l'envoi JSON"""
        return {
            "picture": card.picture,
            "smile": card.smile,
            "type": card.__class__.__name__,
            "place": getattr(card, 'place', None)  # Pour les cartes flirt
        }

    def serialize_player(self, player: players) -> dict:
        """Sérialiser un joueur pour l'envoi JSON"""
        return {
            "name": player.get_name,
            "hand_count": len(player.hand),
            "board": [self.serialize_card(card) for card in player.board]
        }

    def serialize_game_state(self, game_id: str) -> dict:
        """Sérialiser l'état complet du jeu"""
        game_instance = self.games[game_id]
        return {
            "type": "game_state",
            "game_id": game_id,
            "players": [self.serialize_player(player) for player in game_instance.players],
            "deck_count": len(game_instance.deck.values),
            "discard_count": len(game_instance.discard.values),
            "current_player_idx": game_instance.current_player_idx
        }

    async def send_player_hand(self, client_id: str):
        """Envoyer la main du joueur (information privée)"""
        if client_id not in self.client_to_game:
            return
            
        game_id = self.client_to_game[client_id]
        player_name = self.client_to_player[client_id]
        game_instance = self.games[game_id]
        player = game_instance.get_players_by_name(player_name)
        
        if player:
            await self.send_message(self.clients[client_id], {
                "type": "player_hand",
                "hand": [self.serialize_card(card) for card in player.hand]
            })

    async def broadcast_game_state(self, game_id: str):
        """Diffuser l'état du jeu à tous les joueurs de cette partie"""
        if game_id not in self.games:
            return
            
        game_state = self.serialize_game_state(game_id)
        
        # Envoyer l'état public à tous les joueurs de cette partie
        for client_id, client_game_id in self.client_to_game.items():
            if client_game_id == game_id and client_id in self.clients:
                await self.send_message(self.clients[client_id], game_state)
                # Envoyer aussi la main privée de chaque joueur
                await self.send_player_hand(client_id)

    async def send_message(self, websocket, message: dict):
        """Envoyer un message JSON à un client"""
        try:
            await websocket.send(json.dumps(message))
        except websockets.exceptions.ConnectionClosed:
            pass

    async def handle_message(self, websocket, message: dict, client_id: str):
        """Traiter un message reçu d'un client"""
        message_type = message.get("type")
        
        if message_type == "create_game":
            await self.create_game(client_id)
            
        elif message_type == "join_game":
            game_id = message.get("game_id")
            player_name = message.get("player_name")
            await self.join_game(client_id, game_id, player_name)
            
        elif message_type == "take_card":
            await self.take_card_from_deck(client_id)
            
        elif message_type == "play_card":
            card_index = message.get("card_index")
            await self.play_card(client_id, card_index)
            
        elif message_type == "get_game_state":
            if client_id in self.client_to_game:
                game_id = self.client_to_game[client_id]
                await self.broadcast_game_state(game_id)

    async def handle_client(self, websocket):
        """Gérer une connexion client"""
        client_id = str(uuid.uuid4())
        await self.register_client(websocket, client_id)
        
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.handle_message(websocket, data, client_id)
                except json.JSONDecodeError:
                    await self.send_message(websocket, {
                        "type": "error",
                        "message": "Message JSON invalide"
                    })
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister_client(client_id)

# Serveur principal
async def main():
    server = GameServer()
    print("Serveur de jeu de cartes démarré sur ws://localhost:8765")
    await websockets.serve(server.handle_client, "localhost", 8765)
    await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())