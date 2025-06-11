import streamlit as st
from food_suggestions import suggest_foods
from pdf_generator import generate_pdf

st.title("Meal Macro Planner")

# Input kcal totali e percentuali pasti
kcal_total = st.number_input("Kcal giornaliere", min_value=1000, max_value=4000, value=1600)
col1, col2, col3, col4, col5 = st.columns(5)
with col1: perc_col = st.slider("% Colazione", 0, 100, 16)
with col2: perc_spt = st.slider("% Spuntino", 0, 100, 5)
with col3: perc_prz = st.slider("% Pranzo", 0, 100, 39)
with col4: perc_mer = st.slider("% Merenda", 0, 100, 7)
with col5: perc_cen = st.slider("% Cena", 0, 100, 33)

# Input percentuali macro kcal
colA, colB, colC = st.columns(3)
with colA: perc_pro = st.slider("% kcal Proteine", 0, 100, 20)
with colB: perc_carb = st.slider("% kcal Carboidrati", 0, 100, 50)
with colC: perc_fat = st.slider("% kcal Grassi", 0, 100, 30)

# Qui mostro la grammatura corrispondente delle macro totali
with st.columns(1)[0]:
    st.markdown(
        "**Grammatura corrispondente (totale giornaliera):**  \n"
        f"Carboidrati: {round((kcal_total * (perc_carb / 100)) / 4, 1)} g  \n"
        f"Proteine: {round((kcal_total * (perc_pro / 100)) / 4, 1)} g  \n"
        f"Grassi: {round((kcal_total * (perc_fat / 100)) / 9, 1)} g"
    )

# Controlli percentuali pasti e macro
if round(perc_col + perc_spt + perc_prz + perc_mer + perc_cen) != 100:
    st.error("La somma delle percentuali dei pasti deve essere 100%")
    st.stop()

if round(perc_pro + perc_carb + perc_fat) != 100:
    st.error("La somma delle percentuali dei macronutrienti deve essere 100%")
    st.stop()

if st.button("Genera piano pasti completo"):

    distrib = {
        "Colazione": perc_col / 100,
        "Spuntino": perc_spt / 100,
        "Pranzo": perc_prz / 100,
        "Merenda": perc_mer / 100,
        "Cena": perc_cen / 100,
    }

    macro_percent = {
        "protein": perc_pro / 100,
        "carbs": perc_carb / 100,
        "fat": perc_fat / 100,
    }

    pasti = {}

    for nome, perc in distrib.items():
        kcal_pasto = kcal_total * perc
        # Calcolo kcal per macro in quel pasto
        macros_kcal = {m: kcal_pasto * perc_m for m, perc_m in macro_percent.items()}

        # Suggerisci alimenti con grammature per raggiungere le kcal per macro
        foods = suggest_foods(macros_kcal, nome)

        pasti[nome] = {
            "kcal": kcal_pasto,
            "macros_kcal": macros_kcal,
            "foods": foods,
        }

        st.subheader(f"{nome}: {int(kcal_pasto)} kcal ({int(perc*100)}%)")
        st.write(f"Proteine (kcal): {int(macros_kcal['protein'])}")
        st.write(f"Carboidrati (kcal): {int(macros_kcal['carbs'])}")
        st.write(f"Grassi (kcal): {int(macros_kcal['fat'])}")

        st.markdown("### Esempi alimenti per macro")
        for macro in ["protein", "carbs", "fat"]:
            if foods.get(macro):
                st.write(f"**{macro.capitalize()}**: {foods[macro]}")

    pdf_path = generate_pdf(pasti, kcal_total, macro_percent, distrib)
    with open(pdf_path, "rb") as f:
        st.download_button("📄 Scarica piano pasti in PDF", f, file_name="piano_pasti.pdf")
