from typing import Dict
from food_data import FOODS_COLAZIONE, FOODS_PASTI
from utils import round_5g, unit_portion

def suggest_foods(kcal_target: float, pasto: str) -> Dict[str, str]:
    db = FOODS_COLAZIONE if pasto in ["Colazione", "Spuntino", "Merenda"] else FOODS_PASTI
    suggestions = {}
    found = []
    for food, data in db.items():
        # Calcola kcal per 100g
        kcal_per_100g = data.get("carbs", 0) * 4 + data.get("protein", 0) * 4 + data.get("fat", 0) * 9
        if kcal_per_100g == 0:
            continue
        qty = (kcal_target / kcal_per_100g) * 100  # grammi necessari per arrivare a kcal_target
        if "unit" in data:
            text = unit_portion(qty, data["unit"], food)
        else:
            g = round_5g(qty)
            if g < 5:
                continue  # evita porzioni troppo piccole
            text = f"{g}g {food}"
        found.append(text)
    suggestions["kcal"] = " | ".join(found)
    return suggestions
