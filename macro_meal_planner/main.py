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

colA, colB, colC = st.columns(3)
with colA: perc_pro = st.slider("% kcal Proteine", 0, 100, 20)
with colB: perc_carb = st.slider("% kcal Carboidrati", 0, 100, 50)
with colC: perc_fat = st.slider("% kcal Grassi", 0, 100, 30)

with st.columns(1)[0]:
    st.markdown(
        "**Grammatura corrispondente:**  \n"
        f"Carboidrati: {round((kcal_total * (perc_carb / 100)) / 4, 1)}g  \n"
        f"Proteine: {round((kcal_total * (perc_pro / 100)) / 4, 1)}g  \n"
        f"Grassi: {round((kcal_total * (perc_fat / 100)) / 9, 1)}g"
    )

if st.button("Genera piano pasti completo"):
    split = {"carbs": perc_carb / 100, "protein": perc_pro / 100, "fat": perc_fat / 100}
    distrib = {
        "Colazione": perc_col / 100,
        "Spuntino": perc_spt / 100,
        "Pranzo": perc_prz / 100,
        "Merenda": perc_mer / 100,
        "Cena": perc_cen / 100,
    }
    pasti = {}

    for nome, perc in distrib.items():
        kcal = kcal_total * perc

        foods = suggest_foods(kcal, nome, split)
        pasti[nome] = {"kcal": kcal, "foods": foods}

        st.subheader(f"{nome}: {int(kcal)} kcal ({int(perc*100)}%)")
        for macro in ["protein", "carbs", "fat"]:
            kcal_macro = kcal * split[macro]
            st.write(f"{macro.capitalize()} (kcal): {int(kcal_macro)}")
        st.markdown("### Esempi alimenti per macro")
        for macro, items in foods.items():
            st.write(f"{macro.capitalize()}: {items}")

    pdf_path = generate_pdf(pasti, kcal_total, split, distrib)
    with open(pdf_path, "rb") as f:
        st.download_button("📄 Scarica piano pasti in PDF", f, file_name="piano_pasti.pdf")

