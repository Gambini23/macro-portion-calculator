from typing import Dict
def suggest_foods(kcal_pasto: float, pasto: str) -> Dict[str, str]:
    """
    Per ogni macro, lista alimenti con grammatura che porta alla quota kcal_pasto totale,
    senza suddivisione per macro.
    """
    db = FOODS_COLAZIONE if pasto in ["Colazione", "Spuntino", "Merenda"] else FOODS_PASTI
    suggestions = {}
    for macro in ["carbs", "protein", "fat"]:
        found = []
        for food, data in db.items():
            if macro in data:
                kcal_100g = data.get("calories", data[macro] * KCAL_PER_GRAM[macro])
                # Grammatura per raggiungere kcal_pasto (totale kcal del pasto)
                qty = (kcal_pasto / kcal_100g) * 100
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
