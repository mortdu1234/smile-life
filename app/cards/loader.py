"""
Loader de cartes — instancie les cartes depuis data/cards.json.
"""
import inspect
from pathlib import Path

from app.cards.base.card import Card
from app.cards.registry import get_card_class

DATA_FILE = Path(__file__).parent.parent.parent / "data" / "cards.json"


import json, re, copy
from typing import List, Dict

def load_cards(deck_config: Dict[str, int] | None = None) -> List:
    """
    Charge les cartes depuis data/cards.json.

    deck_config : dict { card_id: count } envoyé par le formulaire lobby.
                  Si None, utilise les counts par défaut de cards.json.
                  Si un card_id est absent de deck_config, la carte est ignorée.
                  Si count == 0, la carte est ignorée.
    """
    from app.cards.registry import CARD_REGISTRY

    DATA_PATH = "data/cards.json"

    with open(DATA_PATH, encoding="utf-8") as f:
        raw = f.read()

    # Supprimer les commentaires // non-standard
    raw = re.sub(r"//.*", "", raw)
    data = json.loads(raw)

    # Agréger les entrées par card_id pour avoir les données de chaque variante
    # (plusieurs entrées peuvent avoir le même card_id, ex. flirt avec locations différentes)
    # On groupe par card_id et on distribue le count sur chaque variante
    from collections import defaultdict
    variants: Dict[str, list] = defaultdict(list)
    for entry in data:
        variants[entry["card_id"]].append(entry)

    cards = []

    for card_id, entries in variants.items():
        cls = CARD_REGISTRY.get(card_id)
        if cls is None:
            continue

        # Déterminer le count total à utiliser
        if deck_config is not None:
            total_count = deck_config.get(card_id, 0)
            if total_count == 0:
                continue
        else:
            total_count = sum(e.get("count", 1) for e in entries)

        # Distribuer le count sur les variantes proportionnellement
        # Si on réduit : on coupe les dernières variantes en premier
        # Si on augmente : on duplique les variantes existantes
        remaining = total_count
        variant_cycle = entries * (total_count // len(entries) + 1)  # assez de variantes
        variant_idx = 0

        while remaining > 0:
            entry = copy.copy(variant_cycle[variant_idx % len(variant_cycle)])
            variant_idx += 1
            remaining -= 1

            kwargs = {k: v for k, v in entry.items() if k not in ("card_id", "count")}
            if "image" in kwargs:
                kwargs["image_path"] = kwargs.pop("image")

            try:
                cards.append(cls(**kwargs))
            except TypeError:
                # Ignorer les paramètres inconnus
                import inspect
                sig = inspect.signature(cls.__init__)
                valid = set(sig.parameters.keys()) - {"self"}
                filtered = {k: v for k, v in kwargs.items() if k in valid}
                cards.append(cls(**filtered))

    return cards


def _instantiate(cls: type, entry: dict) -> Card:
    """
    Instancie une carte en passant les paramètres du JSON au constructeur.
    - "image" est automatiquement renommé en "image_path"
    - Les clés non reconnues dans le constructeur sont ignorées silencieusement.
    """
    normalized = dict(entry)

    # Renommage image → image_path (convention des constructeurs)
    if "image" in normalized and "image_path" not in normalized:
        normalized["image_path"] = normalized.pop("image")

    sig = inspect.signature(cls.__init__)
    params = {
        k: v for k, v in normalized.items()
        if k in sig.parameters and k != "self"
    }
    return cls(**params)