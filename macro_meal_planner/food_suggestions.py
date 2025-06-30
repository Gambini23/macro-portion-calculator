from typing import Dict
from food_data import FOODS_COLAZIONE, FOODS_PASTI

def suggest_foods(kcal_pasto: float, pasto: str, split: dict, selected_foods: Dict[str, list]) -> dict:
    db = FOODS_COLAZIONE if pasto in ["Colazione", "Spuntino", "Merenda"] else FOODS_PASTI
    result = {"protein": [], "carbs": [], "fat": []}

    for macro in ["protein", "carbs", "fat"]:
        kcal_macro = kcal_pasto * split[macro]
        foods_for_macro = selected_foods.get(macro, [])

        for food in foods_for_macro:
            if food in db and macro in db[food]:
                data = db[food]
                kcal_100g = data.get("kcal", data[macro] * (9 if macro == "fat" else 4))
                grammi = (kcal_macro / kcal_100g) * 100

                if "unit" in data:
                    unit_weight = data["unit"]
                    units = grammi / unit_weight
                    units_appross = int((units * 1.2) + 0.99)
                    portion = f"{units_appross} {food}"
                else:
                    grammi_rounded = 5 * round(grammi / 5)
                    portion = f"{grammi_rounded}g {food}"

                result[macro].append(portion)

    for macro in result:
        result[macro] = " | ".join(result[macro])

    return result
