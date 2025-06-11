from typing import Dict
from food_data import FOODS_COLAZIONE, FOODS_PASTI

def suggest_foods(kcal_pasto: float, pasto: str, split: dict) -> dict:
    db = FOODS_COLAZIONE if pasto in ["Colazione", "Spuntino", "Merenda"] else FOODS_PASTI
    result = {"protein": [], "carbs": [], "fat": []}

    for macro in ["protein", "carbs", "fat"]:
        kcal_macro = kcal_pasto * split[macro]

        for food, data in db.items():
            if macro in data:
                kcal_100g = data.get("kcal", data[macro] * (9 if macro == "fat" else 4))
                # Calcolo grammi necessari
                grammi = (kcal_macro / kcal_100g) * 100

                if "unit" in data:
                    unit_weight = data["unit"]
                    # Numero di unità, arrotondato con approssimazione 20%
                    units = grammi / unit_weight
                    units_appross = int((units * 1.2) + 0.99)  # arrotonda sempre verso l'alto
                    if units_appross == 1:
                        portion = f"{units_appross} {food[:-1]}"  # es. "1 Uovo" senza plurale
                    else:
                        portion = f"{units_appross} {food}"
                else:
                    # Arrotonda grammi al multiplo di 5 più vicino
                    grammi_rounded = 5 * round(grammi / 5)
                    portion = f"{grammi_rounded}g {food}"

                result[macro].append(portion)

    for macro in result:
        result[macro] = " | ".join(result[macro])

    return result
