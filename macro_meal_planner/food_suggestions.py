from typing import Dict
from food_data import FOODS_COLAZIONE, FOODS_PASTI
from utils import round_5g, unit_portion

def suggest_foods(macros: Dict[str, float], pasto: str) -> Dict[str, str]:
    """
    Suggerisce alimenti con grammature calcolate per coprire il fabbisogno kcal del macro nel pasto.
    """
    db = FOODS_COLAZIONE if pasto in ["Colazione", "Spuntino", "Merenda"] else FOODS_PASTI
    suggestions = {}

    for macro, target_g in macros.items():
        # kcal da coprire per questo macro
        if macro == "carbs" or macro == "protein":
            kcal_target = target_g * 4
        elif macro == "fat":
            kcal_target = target_g * 9
        else:
            kcal_target = 0

        found = []
        kcal_covered = 0
        for food, data in db.items():
            if macro in data and kcal_covered < kcal_target:
                kcal_per_100g = data[macro] * 4 if macro != "fat" else data[macro] * 9
                qty_g = (kcal_target - kcal_covered) / kcal_per_100g * 100

                if "unit" in data:
                    # Calcola quantità in unità (arrotondato)
                    text = unit_portion(qty_g, data["unit"], food)
                else:
                    qty_g_rounded = round_5g(qty_g)
                    if qty_g_rounded < 5:
                        continue  # troppo poco, passa al prossimo
                    text = f"{qty_g_rounded}g {food}"

                found.append(text)
                kcal_covered += (qty_g / 100) * kcal_per_100g

                if len(found) >= 3:
                    break
        if kcal_covered < kcal_target:
            found.append("Quota non completamente coperta con alimenti disponibili")

        suggestions[macro] = " | ".join(found)
    return suggestions
