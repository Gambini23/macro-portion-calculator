from typing import Dict
from food_data import FOODS_COLAZIONE, FOODS_PASTI
from utils import round_5g, unit_portion
def suggest_foods(macros: Dict[str, float], pasto: str) -> Dict[str, str]:
    db = FOODS_COLAZIONE if pasto in ["Colazione", "Spuntino", "Merenda"] else FOODS_PASTI
    suggestions = {}
    
    for macro, target in macros.items():
        found = []
        for food, data in db.items():
            if macro in data:
                qty = (target / data[macro]) * 100
                if "unit" in data:
                    text = unit_portion(qty, data["unit"], food)
                    if not text.startswith("Quantità insufficente"):
                        found.append(text)
                else:
                    g = round_5g(qty)
                    if g >= 5:
                        found.append(f"{g}g {food}")
        suggestions[macro] = " | ".join(found)
    
    return suggestions
