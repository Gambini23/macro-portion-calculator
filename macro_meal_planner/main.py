import streamlit as st
from food_suggestions import suggest_foods
from pdf_generator import generate_pdf

def calcola_bmi_bmr_tdee():
    st.header("Calcolo BMI, BMR e TDEE")

    sesso = st.selectbox("Sesso", ["Maschio", "Femmina"])
    eta = st.number_input("Età", min_value=10, max_value=100, value=30)
    peso = st.number_input("Peso (kg)", min_value=30.0, max_value=200.0, value=70.0)
    altezza = st.number_input("Altezza (cm)", min_value=120.0, max_value=220.0, value=170.0)

    attivita = st.selectbox("Livello di attività fisica", {
        "Leggero (poco movimento)": "leggero",
        "Moderato (attività 3-4 volte/sett)": "moderato",
        "Pesante (attività giornaliera)": "pesante"
    })

    # Calcolo BMI
    altezza_m = altezza / 100
    bmi = round(peso / (altezza_m ** 2), 1)

    if bmi < 18.5:
        categoria = "Sottopeso"
    elif bmi < 25:
        categoria = "Normopeso"
    elif bmi < 30:
        categoria = "Sovrappeso (I grado)"
    elif bmi < 40:
        categoria = "Obesità (II grado)"
    else:
        categoria = "Obesità grave (III grado)"

    # Calcolo BMR
    if sesso == "Femmina":
        bmr = 655.095 + (9.5634 * peso) + (1.849 * altezza) - (4.6756 * eta)
    else:
        bmr = 66.473 + (13.7156 * peso) + (5.033 * altezza) - (6.775 * eta)

    # Calcolo TDEE
    if attivita == "leggero":
        fattore = 1.42 if sesso == "Femmina" else 1.41
    elif attivita == "moderato":
        fattore = 1.56 if sesso == "Femmina" else 1.70
    else:
        fattore = 1.73 if sesso == "Femmina" else 2.01

    tdee = bmr * fattore

    st.subheader("Risultati")
    st.markdown(f"**BMI**: {bmi} ({categoria})")
    st.markdown(f"**BMR**: {int(bmr)} kcal")
    st.markdown(f"**TDEE** (fabbisogno): {int(tdee)} kcal")

    return int(tdee)


st.title("Meal Macro Planner")

# Calcolo/fissazione calorie totali
if 'raw_pasti' not in st.session_state:
    st.session_state.raw_pasti = None
if 'modified_pasti' not in st.session_state:
    st.session_state.modified_pasti = None

kcal_total = None
if st.checkbox("Calcola BMI, BMR e TDEE"):
    fabbisogno = calcola_bmi_bmr_tdee()
    kcal_total = st.number_input("Modifica o conferma le kcal", value=fabbisogno)
else:
    kcal_total = st.number_input("Inserisci manualmente le kcal giornaliere", min_value=1000, max_value=4000, value=1600)

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
        "**Grammatura corrispondente (totale giornata):**  \n"
        f"Carboidrati: {round((kcal_total * (perc_carb / 100)) / 4, 1)}g  \n"
        f"Proteine: {round((kcal_total * (perc_pro / 100)) / 4, 1)}g  \n"
        f"Grassi: {round((kcal_total * (perc_fat / 100)) / 9, 1)}g"
    )

# Generazione piano
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
    st.session_state.modified_pasti = None  # reset eventuali modifiche precedenti

# Visualizzazione e filtro (rimozione)
if st.session_state.raw_pasti:
    display_pasti = st.session_state.modified_pasti or st.session_state.raw_pasti
    st.markdown("## Revisione alimenti (togli con ❌ e poi applica modifiche)")
    new_modified = {}

    for pasto, data in display_pasti.items():
        st.subheader(f"{pasto}: {int(data['kcal'])} kcal")
        st.write(f"Carboidrati: {data['macros']['carbs']}g | Proteine: {data['macros']['protein']}g | Grassi: {data['macros']['fat']}g")

        new_foods = {}
        for macro, food_list in data["foods"].items():
            items = [item.strip() for item in food_list.split("|") if item.strip()]
            kept = []
            st.markdown(f"**{macro.capitalize()}**")
            for item in items:
                checkbox_key = f"{pasto}_{macro}_{item}"
                remove = st.checkbox(f"❌ {item}", key=checkbox_key)
                if not remove:
                    kept.append(item)
            new_foods[macro] = " | ".join(kept)
        new_modified[pasto] = {"kcal": data["kcal"], "macros": data["macros"], "foods": new_foods}

    st.session_state.modified_pasti = new_modified

    if st.button("📄 Applica modifiche e scarica PDF"):
        split = {"carbs": perc_carb / 100, "protein": perc_pro / 100, "fat": perc_fat / 100}
        distrib = {
            "Colazione": perc_col / 100,
            "Spuntino": perc_spt / 100,
            "Pranzo": perc_prz / 100,
            "Merenda": perc_mer / 100,
            "Cena": perc_cen / 100,
        }
        final_pasti = st.session_state.modified_pasti
        pdf_path = generate_pdf(final_pasti, kcal_total, split, distrib)
        with open(pdf_path, "rb") as f:
            st.download_button("📄 Scarica piano pasti in PDF", f, file_name="piano_pasti.pdf")

    
