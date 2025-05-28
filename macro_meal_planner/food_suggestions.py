from typing import Dict
from food_data import FOODS_COLAZIONE, FOODS_PASTI
from utils import round_5g, unit_portion
def suggest_foods(macros: Dict[str, float], pasto: str) -> Dict[str, str]:
    db = FOODS_COLAZIONE if pasto in ["Colazione", "Spuntino", "Merenda"] else FOODS_PASTI
    suggestions = {}

    # Se grassi sono praticamente zero o bassissimi, skippo la lista di grassi direttamente
    fat_threshold = 5  # grammi, soglia minima per mostrare alimenti grassi

    for macro, target in macros.items():
        if macro == "fat" and target < fat_threshold:
            # Quota grassi coperta da altri alimenti, niente lista
            suggestions[macro] = ""
            continue
        
        found = []
        for food, data in db.items():
            if macro in data:
                qty = (target / data[macro]) * 100
                if "unit" in data:
                    text = unit_portion(qty, data["unit"], food)
                    found.append(text)
                else:
                    g = round_5g(qty)
                    if g >= 5:
                        text = f"{g}g {food}"
                        found.append(text)
        suggestions[macro] = " | ".join(found)
    return suggestions
