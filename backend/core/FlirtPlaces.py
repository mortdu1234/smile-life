from enum import Enum

class FlirtPlaces(Enum):
    BAR = "bar"
    BOITE_DE_NUIT = "boite de nuit"
    CINEMA = "cinema"
    INTERNET = "internet"
    PARC = "parc"
    RESTAURANT = "restaurant"
    THEATRE = "theatre"
    ZOO = "zoo"
    HOTEL = "hotel"
    CAMPING = "camping"

    def __str__(self) -> str:
        return self.value