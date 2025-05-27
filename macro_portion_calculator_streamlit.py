# macro_meal_planner.py

import streamlit as st
from typing import Dict, List
from fpdf import FPDF
import tempfile
import math
import os

FOODS_COLAZIONE = {
    "Cornflakes": {"carbs": 84, "kcal": 370},
    "Pane integrale": {"carbs": 40, "kcal": 230},
    "Fiocchi d'avena": {"carbs": 60, "kcal": 370},
    "Yogurt greco": {"protein": 10, "kcal": 60},
    "Uova": {"protein": 13, "kcal": 143, "unit": 60},
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
    "Olio EVO": {"fat": 100, "kcal": 900}
}

KCAL_PER_GRAM = {"carbs": 4, "protein": 4, "fat": 9}

def compute_macros(kcal: float, split: Dict[str, float]) -> Dict[str, float]:
    adjusted_split = split.copy()
    adjusted_split["fat"] *= 0.5
    return {
        macro: round((kcal * perc) / KCAL_PER_GRAM[macro], 1)
        for macro, perc in adjusted_split.items()
    }

def round_5g(val: float) -> int:
    return int(5 * round(val / 5))

def egg_portion(grams: float) -> str:
    if grams <= 70:
        return "1 uovo"
    elif grams <= 130:
        return "2 uova"
    else:
        return f"{round_5g(grams)}g Uova"

def suggest_foods(macros: Dict[str, float], pasto: str) -> Dict[str, str]:
    db = FOODS_COLAZIONE if pasto in ["Colazione", "Spuntino", "Merenda"] else FOODS_PASTI
    suggestions = {}
    for macro, target in macros.items():
        found = []
        for food, data in db.items():
            if macro in data:
                qty = (target / data[macro]) * 100
                if food == "Uova" and "unit" in data:
                    text = egg_portion(qty)
                else:
                    text = f"{round_5g(qty)}g {food}"
                found.append(text)
            if len(found) >= 3:
                break
        suggestions[macro] = " | ".join(found)
    return suggestions

def generate_pdf(pasti: Dict[str, Dict], kcal_total: float, split: Dict[str, float], distrib: Dict[str, float]) -> str:
    disclaimer = ("""
DISCLAIMER
Il presente consiglio alimentare ha esclusivamente finalità informative ed esemplificative.
Le combinazioni alimentari, le frequenze settimanali e le porzioni suggerite sono pensate
per offrire un orientamento generale sulla distribuzione dei macronutrienti e non
costituiscono in alcun modo una prescrizione o una somministrazione dietetica
personalizzata.
Le indicazioni contenute nel documento non tengono conto di eventuali allergie,
intolleranze alimentari, patologie pregresse o condizioni cliniche specifiche, e pertanto
non devono essere utilizzate come sostitutive del parere professionale di figure sanitarie
abilitate, quali medici dietologi, biologi nutrizionisti o dietisti.
Le dosi riportate sono state inserite a scopo didattico per fornire un esempio pratico
riferito a un soggetto sano, di sesso ed età definiti, con finalità puramente illustrative in
ambito sportivo e educativo.
Le indicazioni nutrizionali qui esposte si basano su conoscenze acquisite tramite
formazione in nutrizione sportiva, certificata presso Accademia Italiana Fitness e Sport
Science Lab, nonché sugli attuali studi universitari in corso presso il corso di laurea in
Scienze dell'Alimentazione e Gastronomia (Classe L-26) dell’Università Telematica San
Raffaele.
L’autore declina ogni responsabilità derivante da un uso improprio o non conforme delle
informazioni contenute nel documento. Per una valutazione alimentare personalizzata, si
raccomanda di rivolgersi a professionisti abilitati ai sensi della normativa vigente.
""")
    pdf = FPDF()
    pdf.add_font('DejaVu', 'B', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', uni=True)
    pdf.add_font('DejaVu', '', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', uni=True)
    pdf.add_page()
    pdf.set_font("DejaVu", 'B', 14)
    pdf.cell(0, 10, txt=f"PIANO PASTI - {int(kcal_total)} kcal giornaliere", ln=True)
    pdf.ln(4)
    pdf.set_font("DejaVu", '', 11)
    pdf.cell(0, 10, txt=f"Distribuzione macronutrienti: Carboidrati {int(split['carbs']*100)}% | Proteine {int(split['protein']*100)}% | Grassi {int(split['fat']*50)}% (ridotto)", ln=True)
    pdf.ln(5)

    for pasto, data in pasti.items():
        pdf.set_font("DejaVu", 'B', 13)
        pdf.cell(0, 10, txt=f"{pasto.upper()} ({int(distrib[pasto]*100)}% = {int(data['kcal'])} kcal)", ln=True)
        pdf.set_font("DejaVu", '', 11)
        pdf.cell(0, 10, txt=f"Carboidrati: {data['macros']['carbs']}g", ln=True)
        pdf.cell(0, 10, txt=f"Proteine: {data['macros']['protein']}g", ln=True)
        pdf.cell(0, 10, txt=f"Grassi: {data['macros']['fat']}g", ln=True)
        pdf.ln(2)
        pdf.set_font("DejaVu", 'B', 12)
        pdf.cell(0, 10, txt="Esempi alimenti:", ln=True)
        pdf.set_font("DejaVu", '', 11)
        for macro, items in data['foods'].items():
            pdf.multi_cell(0, 8, f"{macro.capitalize()}: {items}")
        pdf.ln(5)

    pdf.add_page()
    pdf.set_font("DejaVu", 'B', 12)
    pdf.multi_cell(0, 10, disclaimer)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(tmp.name, "F")
    return tmp.name
  
# STREAMLIT UI
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
    distrib = {"Colazione": perc_col/100, "Spuntino": perc_spt/100, "Pranzo": perc_prz/100, "Merenda": perc_mer/100, "Cena": perc_cen/100}
    pasti = {}

    for nome, perc in distrib.items():
        kcal = kcal_total * perc
        macros = compute_macros(kcal, split)
        foods = suggest_foods(macros, nome)
        pasti[nome] = {"kcal": kcal, "macros": macros, "foods": foods}

        st.subheader(f"{nome}: {int(kcal)} kcal ({int(perc*100)}%)")
        st.write(f"Carboidrati: {macros['carbs']}g")
        st.write(f"Proteine: {macros['protein']}g")
        st.write(f"Grassi: {macros['fat']}g")
        st.markdown("### Esempi alimenti")
        for macro, items in foods.items():
            st.write(f"**{macro.capitalize()}**: {items}")

    pdf_path = generate_pdf(pasti, kcal_total, split, distrib)
    with open(pdf_path, "rb") as f:
        st.download_button("📄 Scarica piano pasti in PDF", f, file_name="piano_pasti.pdf")
