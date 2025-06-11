from typing import Dict
from food_data import FOODS_COLAZIONE, FOODS_PASTI
from utils import round_5g, unit_portion

def suggest_foods(macros: Dict[str, float], pasto: str, kcal_pasto: float, split: Dict[str, float]) -> Dict[str, str]:
    db = FOODS_COLAZIONE if pasto in ["Colazione", "Spuntino", "Merenda"] else FOODS_PASTI
    suggestions = {}

    for macro in ["carbs", "protein", "fat"]:
        kcal_macro_target = kcal_pasto * split[macro]

        found = []
        for food, data in db.items():
            if macro in data:
                carbs = data.get("carbs", 0)
                protein = data.get("protein", 0)
                fat = data.get("fat", 0)

                # kcal totali per 100g alimento
                kcal_tot_per_100g = carbs * 4 + protein * 4 + fat * 9
                if kcal_tot_per_100g == 0:
                    continue  # evita divisione per zero

                qty_g = (kcal_macro_target / kcal_tot_per_100g) * 100

                if "unit" in data:
                    text = unit_portion(qty_g, data["unit"], food)
                else:
                    g = round_5g(qty_g)
                    if g < 5:
                        continue
                    text = f"{g}g {food}"

                found.append(text)

        if not found:
            found.append("Quota non completamente coperta con alimenti disponibili")

        suggestions[macro] = " | ".join(found)

    return suggestions

