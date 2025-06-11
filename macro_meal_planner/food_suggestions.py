from typing import Dict
from food_data import FOODS_COLAZIONE, FOODS_PASTI

def suggest_foods(kcal_pasto: float, pasto: str, split: Dict[str, float]) -> Dict[str, str]:
    """
    Per ogni macro calcola la grammatura degli alimenti per coprire kcal macro.
    Restituisce dict con macro: stringa elenco alimenti con grammatura.
    """
    db = FOODS_COLAZIONE if pasto in ["Colazione", "Spuntino", "Merenda"] else FOODS_PASTI

    result = {"protein": [], "carbs": [], "fat": []}

    for macro in ["protein", "carbs", "fat"]:
        kcal_macro = kcal_pasto * split[macro]

        for food, data in db.items():
            if macro in data:
                kcal_100g = data.get("kcal", data[macro] * (9 if macro == "fat" else 4))

                grammi = kcal_macro / kcal_100g * 100
                grammi = round(grammi, 1)

                if "unit" in data:
                    unit_weight = data["unit"]
                    units = grammi / unit_weight
                    units = round(units, 1)
                    portion = f"{units} unità" if units >= 0.1 else f"{grammi}g"
                else:
                    portion = f"{grammi}g"

                result[macro].append(f"{portion} {food}")

    for macro in result:
        result[macro] = " | ".join(result[macro])

    return result

