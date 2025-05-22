# macro_meal_planner.py

import streamlit as st
from typing import Dict, List
from fpdf import FPDF
import tempfile

NutrientData = Dict[str, float]

KCAL_PER_GRAM = {"carbs": 4, "protein": 4, "fat": 9}

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

def compute_macros(kcal: float, split: Dict[str, float]) -> Dict[str, float]:
    return {
        macro: round((kcal * perc) / KCAL_PER_GRAM[macro], 1)
        for macro, perc in split.items()
    }

def suggest_foods(macros: Dict[str, float]) -> Dict[str, str]:
    suggestions = {}
    for macro, target in macros.items():
        found = []
        for food, data in FOODS.items():
            if macro in data:
                qty = round((target / data[macro]) * 100, 1)
                found.append(f"{qty}g {food}")
            if len(found) >= 3:
                break
        suggestions[macro] = " | ".join(found)
    return suggestions

def generate_pdf(pasti: Dict[str, Dict]) -> str:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for pasto, data in pasti.items():
        pdf.cell(200, 10, txt=f"Pasto: {pasto} ({int(data['kcal'])} kcal)", ln=True)
        pdf.cell(200, 10, txt=f"Carboidrati: {data['macros']['carbs']}g", ln=True)
        pdf.cell(200, 10, txt=f"Proteine: {data['macros']['protein']}g", ln=True)
        pdf.cell(200, 10, txt=f"Grassi: {data['macros']['fat']}g", ln=True)
        pdf.ln()
        pdf.cell(200, 10, txt="Esempi alimenti:", ln=True)
        for macro, items in data['foods'].items():
            pdf.multi_cell(0, 10, f"{macro.capitalize()}: {items}")
        pdf.ln(5)

    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 8, """
Il presente consiglio alimentare ha esclusivamente finalità informative.
Non costituisce una prescrizione medica o dietetica personalizzata.
Per una valutazione nutrizionale professionale, rivolgersi a un nutrizionista o medico.
""")

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(tmp.name)
    return tmp.name

st.title("Meal Macro Planner")

kcal_total = st.number_input("Kcal giornaliere", min_value=1000, max_value=4000, value=1600)
col1, col2, col3, col4, col5 = st.columns(5)

with col1: perc_col = st.slider("% Colazione", 0, 100, 16)
with col2: perc_spt = st.slider("% Spuntino", 0, 100, 5)
with col3: perc_prz = st.slider("% Pranzo", 0, 100, 39)
with col4: perc_mer = st.slider("% Merenda", 0, 100, 7)
with col5: perc_cen = st.slider("% Cena", 0, 100, 33)

colA, colB, colC = st.columns(3)
with colA: perc_pro = st.slider("% kcal Proteine", 0, 100, 20)
with colB: perc_carb = st.slider("% kcal Carboidrati", 0, 100, 50)
with colC: perc_fat = st.slider("% kcal Grassi", 0, 100, 30)

if st.button("Genera piano pasti completo"):
    split = {"carbs": perc_carb/100, "protein": perc_pro/100, "fat": perc_fat/100}
    pasti = {}

    for nome, perc in zip(["Colazione", "Spuntino", "Pranzo", "Merenda", "Cena"], [perc_col, perc_spt, perc_prz, perc_mer, perc_cen]):
        kcal = kcal_total * (perc / 100)
        macros = compute_macros(kcal, split)
        foods = suggest_foods(macros)
        pasti[nome] = {"kcal": kcal, "macros": macros, "foods": foods}

        st.subheader(f"{nome}: {int(kcal)} kcal")
        st.write(f"Carboidrati: {macros['carbs']}g")
        st.write(f"Proteine: {macros['protein']}g")
        st.write(f"Grassi: {macros['fat']}g")
        st.markdown("### Esempi alimenti")
        for macro, items in foods.items():
            st.write(f"**{macro.capitalize()}**: {items}")

    pdf_path = generate_pdf(pasti)
    with open(pdf_path, "rb") as f:
        st.download_button("📄 Scarica piano pasti in PDF", f, file_name="piano_pasti.pdf")

