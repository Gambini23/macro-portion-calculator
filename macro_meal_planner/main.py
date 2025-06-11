import streamlit as st
from food_suggestions import suggest_foods
from pdf_generator import generate_pdf

st.title("Meal Macro Planner")

kcal_total = st.number_input("Kcal giornaliere", min_value=1000, max_value=4000, value=1600)
col1, col2, col3, col4, col5 = st.columns(5)

with col1: perc_col = st.slider("% Colazione", 0, 100, 16)
with col2: perc_spt = st.slider("% Spuntino", 0, 100, 5)
with col3: perc_prz = st.slider("% Pranzo", 0, 100, 39)
with col4: perc_mer = st.slider("% Merenda", 0, 100, 7)
with col5: perc_cen = st.slider("% Cena", 0, 100, 33)

if st.button("Genera piano pasti completo"):
    distrib = {
        "Colazione": perc_col / 100,
        "Spuntino": perc_spt / 100,
        "Pranzo": perc_prz / 100,
        "Merenda": perc_mer / 100,
        "Cena": perc_cen / 100
    }
    pasti = {}

    for nome, perc in distrib.items():
        kcal = kcal_total * perc
        foods = suggest_foods(kcal, nome)  # solo kcal e pasto
        pasti[nome] = {"kcal": kcal, "foods": foods}

        st.subheader(f"{nome}: {int(kcal)} kcal ({int(perc * 100)}%)")
        st.markdown("### Esempi alimenti")
        st.write(foods["kcal"])

    pdf_path = generate_pdf(pasti, kcal_total, distrib)
    with open(pdf_path, "rb") as f:
        st.download_button("📄 Scarica piano pasti in PDF", f, file_name="piano_pasti.pdf")

