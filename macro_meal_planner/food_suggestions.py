from typing import Dict
from food_data import FOODS_COLAZIONE, FOODS_PASTI
from utils import round_5g, unit_portion

def suggest_foods(macros: Dict[str, float], pasto: str, kcal_pasto: float, split: Dict[str, float]) -> Dict[str, str]:
    """
    Suggerisce TUTTI gli alimenti per ciascun macro con grammature calcolate per coprire la quota kcal.
    """
    db = FOODS_COLAZIONE if pasto in ["Colazione", "Spuntino", "Merenda"] else FOODS_PASTI
    suggestions = {}

    for macro, ratio in split.items():
        # kcal totali da coprire per questo macro nel pasto
        kcal_target = kcal_pasto * ratio

        found = []
        for food, data in db.items():
            if macro in data:
                # kcal per 100g di questo macro
                kcal_per_100g = data[macro] * (4 if macro != "fat" else 9)
                qty_g = (kcal_target / kcal_per_100g) * 100

                if "unit" in data:
                    text = unit_portion(qty_g, data["unit"], food)
                else:
                    g = round_5g(qty_g)
                    if g < 5:
                        # Ignora quantità troppo piccole
                        continue
                    text = f"{g}g {food}"

                found.append(text)
        if not found:
            found.append("Quota non completamente coperta con alimenti disponibili")

        suggestions[macro] = " | ".join(found)
    return suggestions

