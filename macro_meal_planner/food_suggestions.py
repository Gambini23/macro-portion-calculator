from typing import Dict
from food_data import FOODS_COLAZIONE, FOODS_PASTI
from utils import round_5g, egg_portion

def suggest_foods(macros: Dict[str, float], pasto: str) -> Dict[str, str]:
    db = FOODS_COLAZIONE if pasto in ["Colazione", "Spuntino", "Merenda"] else FOODS_PASTI
    suggestions = {}
    for macro, target in macros.items():
        found = []
        for food, data in db.items():
            if macro in data:
                qty = (target / data[macro]) * 100
                if food == "Uova" and "unit" in data:
                    text = egg_portion(qty)
                else:
                    g = round_5g(qty)
                    text = f"{g}g {food}" if g >= 5 else "Quantità già coperta da altri alimenti"
                found.append(text)
            if len(found) >= 3:
                break
        suggestions[macro] = " | ".join(found)
    return suggestions