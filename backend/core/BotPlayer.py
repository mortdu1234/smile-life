from backend.userIo.interface import UserIO

from .Player import Player

class BotPlayer(Player):
    def __init__(self, name: str, id: int, interface: UserIO):
        super().__init__(name, id, interface)