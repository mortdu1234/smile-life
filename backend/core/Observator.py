
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..userIo.interface import UserIO

class Observator:
    interface: "UserIO"
    def __init__(self, interface:"UserIO") -> None:
        self.interface = interface
        