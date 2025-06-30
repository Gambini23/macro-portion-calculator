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

st.markdown(
    f"**Grammatura corrispondente (totale giornata):**  ")
st.markdown(
    f"Carboidrati: {round((kcal_total * (perc_carb / 100)) / 4, 1)}g  ")
st.markdown(
    f"Proteine: {round((kcal_total * (perc_pro / 100)) / 4, 1)}g  ")
st.markdown(
    f"Grassi: {round((kcal_total * (perc_fat / 100)) / 9, 1)}g")

if 'raw_pasti' not in st.session_state:
    st.session_state.raw_pasti = None

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
        macros = {
            "protein": round((kcal * split["protein"]) / 4, 1),
            "carbs": round((kcal * split["carbs"]) / 4, 1),
            "fat": round((kcal * split["fat"]) / 9, 1),
        }
        foods = suggest_foods(kcal, nome, split)

        pasti[nome] = {"kcal": kcal, "macros": macros, "foods": foods}

    st.session_state.raw_pasti = pasti

if st.session_state.raw_pasti:
    modified_pasti = {}

    for pasto, data in st.session_state.raw_pasti.items():
        st.subheader(f"{pasto}: {int(data['kcal'])} kcal")
        st.write(f"Carboidrati: {data['macros']['carbs']}g | Proteine: {data['macros']['protein']}g | Grassi: {data['macros']['fat']}g")

        new_foods = {}
        for macro, food_list in data['foods'].items():
            items = [item.strip() for item in food_list.split('|') if item.strip()]
            kept_items = []
            st.markdown(f"**{macro.capitalize()}**")
            for item in items:
                if not st.checkbox(f"❌ {item}", key=f"{pasto}_{macro}_{item}"):
                    kept_items.append(item)
            new_foods[macro] = " | ".join(kept_items)

        modified_pasti[pasto] = {
            "kcal": data['kcal'],
            "macros": data['macros'],
            "foods": new_foods
        }

    if st.button("📄 Applica modifiche e scarica PDF"):
        split = {"carbs": perc_carb / 100, "protein": perc_pro / 100, "fat": perc_fat / 100}
        distrib = {
            "Colazione": perc_col / 100,
            "Spuntino": perc_spt / 100,
            "Pranzo": perc_prz / 100,
            "Merenda": perc_mer / 100,
            "Cena": perc_cen / 100,
        }
        pdf_path = generate_pdf(modified_pasti, kcal_total, split, distrib)
        with open(pdf_path, "rb") as f:
            st.download_button("📄 Scarica piano pasti in PDF", f, file_name="piano_pasti.pdf")

