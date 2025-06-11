from typing import Dict
from food_data import FOODS_COLAZIONE, FOODS_PASTI, KCAL_PER_GRAM

def unit_portion(qty: float, unit_weight: float, food_name: str) -> str:
    unit_qty = qty / unit_weight
    rounded = round(unit_qty)
    if abs(unit_qty - rounded) <= 0.2:
        unit_qty = rounded
    return f"{int(unit_qty)} {food_name}" if unit_qty >= 1 else f"{round(qty)}g {food_name}"

def suggest_foods(kcal_pasto: float, pasto: str) -> Dict[str, str]:
    """
    Suggerisce alimenti per il pasto calcolando la grammatura necessaria
    per raggiungere le kcal del pasto, ignorando la suddivisione in macro.
    """
    # Se il pasto è colazione, spuntino o merenda usa FOODS_COLAZIONE, altrimenti FOODS_PASTI
    db = FOODS_COLAZIONE if pasto in ["Colazione", "Spuntino", "Merenda"] else FOODS_PASTI

    found = []
    for food, data in db.items():
        kcal_100g = data.get("kcal")
        if not kcal_100g:
            # Se manca il valore kcal, salta
            continue

        qty = (kcal_pasto / kcal_100g) * 100  # grammi necessari per raggiungere kcal_pasto

        # Se c'è il campo "unit" usiamo unit_portion, altrimenti grammi tondi a 5
        if "unit" in data:
            text = unit_portion(qty, data["unit"], food)
        else:
            # Arrotondiamo a multipli di 5 grammi
            qty_5g = max(5, round(qty / 5) * 5)
            text = f"{qty_5g}g {food}"
        found.append(text)

    return {"foods": " | ".join(found)}
