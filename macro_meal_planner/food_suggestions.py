from typing import Dict
from food_data import FOODS_COLAZIONE, FOODS_PASTI, KCAL_PER_GRAM

def unit_portion(qty: float, unit_weight: float, food_name: str) -> str:
    unit_qty = qty / unit_weight
    rounded = round(unit_qty)
    if abs(unit_qty - rounded) <= 0.2:
        unit_qty = rounded
    if unit_qty >= 1:
        return f"{int(unit_qty)} {food_name}"
    else:
        return f"{round(qty)}g {food_name}"

def suggest_foods(macros_kcal: Dict[str, float], pasto: str) -> Dict[str, str]:
    """
    macros_kcal: kcal da coprire per macro, es {"protein": 200, "carbs": 500, "fat": 300}
    pasto: nome pasto (es. "Colazione", "Pranzo", ecc)
    
    Ritorna dict con stringhe di alimenti+grammature per ogni macro
    """
    db = FOODS_COLAZIONE if pasto in ["Colazione", "Spuntino", "Merenda"] else FOODS_PASTI

    result = {"carbs": [], "protein": [], "fat": []}

    for macro in ["carbs", "protein", "fat"]:
        kcal_to_cover = macros_kcal.get(macro, 0)
        if kcal_to_cover <= 0:
            continue

        # Filtra alimenti che contengono quel macro
        foods_macro = {food: data for food, data in db.items() if macro in data}

        for food, data in foods_macro.items():
            kcal_macro_100g = data[macro] * KCAL_PER_GRAM[macro]
            if kcal_macro_100g == 0:
                continue

            # Calcola grammi per raggiungere kcal_to_cover
            qty = (kcal_to_cover / kcal_macro_100g) * 100

            if "unit" in data:
                txt = unit_portion(qty, data["unit"], food)
            else:
                # arrotondo a multipli di 5g per praticità, minimo 5g
                qty_5g = max(5, round(qty / 5) * 5)
                txt = f"{qty_5g}g {food}"

            result[macro].append(txt)

    # Unisco le liste in stringhe con separatore pipe
    return {macro: " | ".join(items) for macro, items in result.items()}

