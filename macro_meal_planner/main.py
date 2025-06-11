import streamlit as st
from macros import compute_macros
from food_suggestions import suggest_foods
from pdf_generator import generate_pdf

def kcal_percent_to_grams(percentuali, tot_kcal):
    kcal_per_g = {'carbs': 4, 'protein': 4, 'fat': 9}
    grams = {}
    for macro, percent in percentuali.items():
        grams[macro] = round((percent / 100) * tot_kcal / kcal_per_g[macro], 1)
    return grams

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

split_percent = {'carbs': perc_carb, 'protein': perc_pro, 'fat': perc_fat}
grams_total = kcal_percent_to_grams(split_percent, kcal_total)

with st.columns(1)[0]:
    st.markdown(
        "**Grammatura corrispondente ai macronutrienti (su tutto il giorno):**  \n"
        f"Carboidrati: {grams_total['carbs']}g  \n"
        f"Proteine: {grams_total['protein']}g  \n"
        f"Grassi: {grams_total['fat']}g"
    )

if st.button("Genera piano pasti completo"):
    split = {"carbs": perc_carb/100, "protein": perc_pro/100, "fat": perc_fat/100}
    distrib = {"Colazione": perc_col/100, "Spuntino": perc_spt/100, "Pranzo": perc_prz/100, "Merenda": perc_mer/100, "Cena": perc_cen/100}
    pasti = {}

    for nome, perc in distrib.items():
        kcal = kcal_total * perc
        macros = compute_macros(kcal, split)
        foods = suggest_foods(macros, nome)
        pasti[nome] = {"kcal": kcal, "macros": macros, "foods": foods}

        grams_pasto = kcal_percent_to_grams(split_percent, kcal)
        
        st.subheader(f"{nome}: {int(kcal)} kcal ({int(perc*100)}%)")
        st.write(f"Carboidrati: {macros['carbs']}g (Teorici: {grams_pasto['carbs']}g)")
        st.write(f"Proteine: {macros['protein']}g (Teorici: {grams_pasto['protein']}g)")
        st.write(f"Grassi: {macros['fat']}g (Teorici: {grams_pasto['fat']}g)")
        
        st.markdown("### Esempi alimenti")
        for macro, items in foods.items():
            if macro == "fat" and items.strip() == "":
                st.write(f"**Grassi**: Quota coperta da altri alimenti")
            else:
                st.write(f"**{macro.capitalize()}**: {items}")

    pdf_path = generate_pdf(pasti, kcal_total, split, distrib)
    with open(pdf_path, "rb") as f:
        st.download_button("📄 Scarica piano pasti in PDF", f, file_name="piano_pasti.pdf")

