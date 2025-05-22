# macro_meal_planner.py

import streamlit as st
from typing import Dict, List
from fpdf import FPDF
import tempfile

NutrientData = Dict[str, float]

KCAL_PER_GRAM = {"carbs": 4, "protein": 4, "fat": 9}

FOODS_COLAZIONE = {
    "Cornflakes": {"carbs": 84, "kcal": 370},
    "Pane integrale": {"carbs": 40, "kcal": 230},
    "Fiocchi d'avena": {"carbs": 60, "kcal": 370},
    "Yogurt greco": {"protein": 10, "kcal": 60},
    "Uova": {"protein": 13, "kcal": 143},
    "Albume": {"protein": 10, "kcal": 50},
    "Burro di arachidi": {"fat": 50, "kcal": 600},
    "Mandorle": {"fat": 49, "kcal": 600},
    "Cioccolato fondente": {"fat": 35, "kcal": 550},
}

FOODS_PASTI = {
    "Pasta integrale": {"carbs": 70, "kcal": 350},
    "Riso": {"carbs": 78, "kcal": 360},
    "Cous cous": {"carbs": 72, "kcal": 350},
    "Patate crude": {"carbs": 17, "kcal": 80},
    "Gnocchi di patate": {"carbs": 30, "kcal": 150},
    "Pane integrale": {"carbs": 40, "kcal": 230},
    "Carne bianca": {"protein": 22, "kcal": 120},
    "Carne rossa": {"protein": 26, "kcal": 180},
    "Pesce bianco": {"protein": 20, "kcal": 100},
    "Pesce grasso": {"protein": 20, "kcal": 200},
    "Tofu": {"protein": 10, "kcal": 120},
    "Bresaola": {"protein": 32, "kcal": 151},
    "Olio EVO": {"fat": 100, "kcal": 900},
    "Mandorle": {"fat": 49, "kcal": 600}
}

def compute_macros(kcal: float, split: Dict[str, float]) -> Dict[str, float]:
    return {
        macro: round((kcal * perc) / KCAL_PER_GRAM[macro], 1)
        for macro, perc in split.items()
    }

def suggest_foods(macros: Dict[str, float], pasto: str) -> Dict[str, str]:
    db = FOODS_COLAZIONE if pasto == "Colazione" or "Spuntino" or "Merenda" else FOODS_PASTI
    suggestions = {}
    for macro, target in macros.items():
        found = []
        for food, data in db.items():
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
    pdf.set_font("Arial", 'B', 14)

    for pasto, data in pasti.items():
        pdf.cell(0, 10, txt=f"{pasto.upper()} ({int(data['kcal'])} kcal)", ln=True)
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, txt=f"Carboidrati: {data['macros']['carbs']}g", ln=True)
        pdf.cell(0, 10, txt=f"Proteine: {data['macros']['protein']}g", ln=True)
        pdf.cell(0, 10, txt=f"Grassi: {data['macros']['fat']}g", ln=True)
        pdf.ln()
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, txt="Esempi alimenti:", ln=True)
        pdf.set_font("Arial", '', 12)
        for macro, items in data['foods'].items():
            pdf.multi_cell(0, 10, f"{macro.capitalize()}: {items}")
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 14)

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
        foods = suggest_foods(macros, nome)
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


