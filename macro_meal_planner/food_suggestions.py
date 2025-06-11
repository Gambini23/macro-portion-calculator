from typing import Dict
from food_data import FOODS_COLAZIONE, FOODS_PASTI
from utils import round_5g, unit_portion

# kcal per grammo macros
KCAL_PER_GRAM = {"carbs": 4, "protein": 4, "fat": 9}

def suggest_foods(macros: Dict[str, float], pasto: str, kcal_pasto: float) -> Dict[str, str]:
    db = FOODS_COLAZIONE if pasto in ["Colazione", "Spuntino", "Merenda"] else FOODS_PASTI
    suggestions = {}
    for macro, target_grams in macros.items():
        found = []
        for food, data in db.items():
            if macro in data:
                # kcal dell'alimento per 100g
                kcal_per_100g = data.get("calories", data[macro] * KCAL_PER_GRAM[macro])
                # Calcolo la quantità in grammi necessaria per raggiungere i target kcal del macro
                # kcal da coprire per questo macro = target_grams * kcal_per_gram (es. 20g protein * 4kcal)
                kcal_macro = target_grams * KCAL_PER_GRAM[macro]
                # Grammi alimento necessari = kcal_macro / (kcal per 1g alimento)
                qty = (kcal_macro / kcal_per_100g) * 100

                if "unit" in data:
                    text = unit_portion(qty, data["unit"], food)
                else:
                    g = round_5g(qty)
                    if g >= 5:
                        text = f"{g}g {food}"
                    else:
                        text = "Quantità insufficiente, usa altri alimenti"
                found.append(text)
        suggestions[macro] = " | ".join(found)
    return suggestions
