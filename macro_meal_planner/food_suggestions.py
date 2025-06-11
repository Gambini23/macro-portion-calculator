from typing import Dict
from food_data import FOODS_COLAZIONE, FOODS_PASTI
from utils import round_5g, unit_portion

KCAL_PER_GRAM = {"carbs": 4, "protein": 4, "fat": 9}

def calculate_qty_for_macro_kcal(kcal_target: float, macro_amount_per_100g: float, macro_name: str) -> float:
    kcal_per_100g_macro = macro_amount_per_100g * KCAL_PER_GRAM[macro_name]
    if kcal_per_100g_macro == 0:
        return 0
    qty = (kcal_target / kcal_per_100g_macro) * 100
    return qty

def suggest_foods(macros: Dict[str, float], pasto: str, kcal_pasto: float, split: Dict[str, float]) -> Dict[str, str]:
    db = FOODS_COLAZIONE if pasto in ["Colazione", "Spuntino", "Merenda"] else FOODS_PASTI
    suggestions = {}

    for macro, target_g in macros.items():
        kcal_macro = kcal_pasto * split[macro]  # kcal da quel macro nel pasto
        found = []
        for food, data in db.items():
            if macro in data:
                macro_per_100g = data[macro]
                qty = calculate_qty_for_macro_kcal(kcal_macro, macro_per_100g, macro)
                if qty <= 0:
                    continue
                if "unit" in data:
                    text = unit_portion(qty, data["unit"], food)
                else:
                    g = round_5g(qty)
                    if g >= 5:
                        text = f"{g}g {food}"
                    else:
                        text = "Quantità insufficiente utilizzare altri alimenti"
                found.append(text)
        suggestions[macro] = " | ".join(found)
    return suggestions
