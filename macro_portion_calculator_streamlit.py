import streamlit as st
from typing import List, Dict

NutrientData = Dict[str, float]

TARGET_CHO = 28
CORNFLAKES_CHO_PER_100G = 84
CORNFLAKES_KCAL_PER_100G = 370
BASE_PORTION_GRAMS = TARGET_CHO / CORNFLAKES_CHO_PER_100G * 100
BASE_KCAL = BASE_PORTION_GRAMS * CORNFLAKES_KCAL_PER_100G / 100

FOODS = {
    "Cornflakes": {"carbs": 84, "kcal": 370},
    "Pane integrale": {"carbs": 40, "kcal": 230},
    "Frutta (media)": {"carbs": 12, "kcal": 50},
    "Fiocchi/Farina d'avena": {"carbs": 60, "kcal": 370},
    "Weetabix (formelle)": {"carbs": 67, "kcal": 360},
    "Gallette di riso": {"carbs": 80, "kcal": 380},
    "Yogurt greco": {"protein": 10, "kcal": 60},
    "Yogurt magro": {"protein": 5, "kcal": 40},
    "Kefir": {"protein": 3.5, "kcal": 50},
    "Uova intere": {"protein": 13, "kcal": 143, "weight": 60},
    "Albume": {"protein": 10, "kcal": 50},
    "Proteine in polvere": {"protein": 85, "kcal": 360},
    "Bresaola": {"protein": 32, "kcal": 151},
    "Prosciutto cotto": {"protein": 20, "kcal": 145},
    "Prosciutto crudo": {"protein": 25, "kcal": 250},
    "Parmigiano": {"protein": 33, "kcal": 400},
    "Cioccolato fondente": {"fat": 35, "kcal": 550},
    "Mandorle": {"fat": 49, "kcal": 600},
    "Noci": {"fat": 65, "kcal": 700},
    "Mix frutta secca": {"fat": 55, "kcal": 650},
    "Burro di arachidi": {"fat": 50, "kcal": 600},
    "Pasta integrale": {"carbs": 70, "kcal": 350},
    "Riso": {"carbs": 78, "kcal": 360},
    "Cous cous": {"carbs": 72, "kcal": 350},
    "Piadina confezionata": {"carbs": 45, "kcal": 300},
    "Patate crude": {"carbs": 17, "kcal": 80},
    "Gnocchi di patate": {"carbs": 30, "kcal": 150},
    "Carne bianca": {"protein": 22, "kcal": 120},
    "Carne rossa": {"protein": 26, "kcal": 180},
    "Pesce bianco": {"protein": 20, "kcal": 100},
    "Pesce azzurro": {"protein": 22, "kcal": 120},
    "Pesce grasso": {"protein": 20, "kcal": 200},
    "Formaggi magri": {"protein": 15, "kcal": 170},
    "Affettati magri": {"protein": 30, "kcal": 140},
    "Tofu al naturale": {"protein": 10, "kcal": 120},
    "Tonno al naturale": {"protein": 25, "kcal": 120},
    "Olio extravergine di oliva": {"fat": 100, "kcal": 900},
    "Mix cereali/legumi": {"carbs": 55, "protein": 20, "kcal": 350},
}

def calculate_portions(food_db: Dict[str, NutrientData], target_nutrient: str, target_value: float) -> List[Dict[str, float]]:
    result = []
    for food, data in food_db.items():
        if target_nutrient not in data:
            continue
        food_entry = {"Alimento": food}
        food_entry[f"{target_value}g {target_nutrient}"] = round((target_value / data[target_nutrient]) * 100, 1)
        food_entry["123 kcal (g)"] = round((BASE_KCAL / data["kcal"]) * 100, 1)
        result.append(food_entry)
    return result

st.title("Calcolatore porzioni alimentari")

nutrient = st.selectbox("Scegli il macronutriente", ["carbs", "protein", "fat"])
value = st.number_input("Inserisci il valore target in grammi", min_value=1.0, step=1.0, value=28.0)

if st.button("Calcola porzioni"):
    results = calculate_portions(FOODS, nutrient, value)
    st.dataframe(results)
    st.success("Tabella generata con successo!")
