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
        print(f"######## TESTING######### : ", card_id.split("__")[0])
        cls = _resolve_class(CARD_REGISTRY, card_id.split("__")[0])
        if cls is None:
            print(f"[loader] ⚠️  card_id sans correspondance dans le registre : '{card_id}' — ignoré")
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
            except TypeError as e:
                # Filtrer les paramètres non reconnus par le constructeur
                sig = inspect.signature(cls.__init__)
                valid = set(sig.parameters.keys()) - {"self"}
                filtered = {k: v for k, v in kwargs.items() if k in valid}
                try:
                    cards.append(cls(**filtered))
                except TypeError as e2:
                    print(f"[loader] ❌ Impossible d'instancier '{card_id}' ({cls.__name__}) : {e2}")

    return cards


# Note : la fonction _instantiate ci-dessous est conservée uniquement comme référence.
# Le chargement réel utilise la logique inline dans load_cards().


def _resolve_class(registry: dict, card_id: str):
    """
    Résout la classe correspondant à un card_id en essayant plusieurs formes :

    1. Correspondance exacte           : "flirt_bar"    → registry["flirt_bar"]
    2. Sans chiffres finaux            : "study1"       → registry["study"]
    3. Préfixe avant le premier "_"    : "flirt_bar"    → registry["flirt"]
    4. Préfixe avant le deuxième "_"   : "flirt_with_child_hotel" → registry["flirt_with"]
       (pour les cas comme flirt_with_child_*)

    Retourne None si aucune forme ne correspond.
    """
    # 1. Exact
    if card_id in registry:
        return registry[card_id]

    # 2. Strip trailing digits  (study1 → study, salary4 → salary, house2 → house)
    base_no_digits = re.sub(r"\d+$", "", card_id)
    if base_no_digits and base_no_digits != card_id and base_no_digits in registry:
        return registry[base_no_digits]

    # 3. Préfixe avant le 1er underscore  (flirt_bar → flirt, travel_rio → travel)
    if "_" in card_id:
        prefix1 = card_id.split("_")[0]
        if prefix1 in registry:
            return registry[prefix1]

    # 4. Préfixe avant le 2ème underscore  (flirt_with_child_hotel → flirt_with)
    parts = card_id.split("_")
    if len(parts) >= 3:
        prefix2 = "_".join(parts[:2])
        if prefix2 in registry:
            return registry[prefix2]

    return None