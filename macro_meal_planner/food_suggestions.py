from typing import Dict
from food_data import FOODS_COLAZIONE, FOODS_PASTI

# kcal per grammo di ogni macro
KCAL_PER_GRAM = {
    "carbs": 4,
    "protein": 4,
    "fat": 9,
}

def suggest_foods(kcal_pasto: float, pasto: str) -> Dict[str, str]:
    """
    Suggerisce alimenti per raggiungere le kcal del pasto.
    Calcola la grammatura in base alle kcal di ogni alimento.
    Restituisce un dict con macro come chiave e stringa di alimenti e grammature come valore.
    """
    db = FOODS_COLAZIONE if pasto in ["Colazione", "Spuntino", "Merenda"] else FOODS_PASTI

    suggestions = {"carbs": [], "protein": [], "fat": []}

    # Ciclo su ogni alimento nel DB
    for food, data in db.items():
        # Ogni alimento ha macro e calorie per 100g, oppure calcoliamo con macro * kcal/g
        calories_100g = data.get("calories")
        if calories_100g is None:
            # Se non c'è campo calories, calcoliamo
            calories_100g = 0
            for macro in ["carbs", "protein", "fat"]:
                if macro in data:
                    calories_100g += data[macro] * KCAL_PER_GRAM[macro]

        # Per ogni macro presente nell'alimento
        for macro in ["carbs", "protein", "fat"]:
            if macro in data:
                # Quante kcal di questo macro per 100g?
                kcal_macro_100g = data[macro] * KCAL_PER_GRAM[macro]
                # Quante kcal totali arrivano da questo alimento? (usiamo calories_100g)
                # Calcolo la frazione kcal_macro rispetto al totale kcal 100g
                if calories_100g == 0:
                    # Evito divisione per zero
                    continue
                frac_macro = kcal_macro_100g / calories_100g

                # Obiettivo kcal del macro nel pasto
                kcal_macro_target = kcal_pasto * frac_macro

                # Grammatura per raggiungere kcal macro target
                qty_g = kcal_macro_target / (data[macro] * KCAL_PER_GRAM[macro]) * 100

                # Arrotondo a multipli di 5g per chiarezza (funzione semplice)
                qty_g_rounded = max(5, round(qty_g / 5) * 5)

                # Solo se quantità significativa (>= 5g) la mostro
                if qty_g_rounded >= 5:
                    suggestions[macro].append(f"{qty_g_rounded}g {food}")

    # Convertiamo le liste in stringhe separate da pipe
    result = {}
    for macro in suggestions:
        if suggestions[macro]:
            result[macro] = " | ".join(suggestions[macro])
        else:
            result[macro] = ""

    return result
