import streamlit as st
from food_suggestions import suggest_foods
from pdf_generator import generate_pdf

def calcola_bmi_bmr_tdee():
    st.header("Calcolo BMI, BMR e TDEE")

    sesso = st.selectbox("Sesso", ["Maschio", "Femmina"])
    eta = st.number_input("Età", min_value=10, max_value=100, value=30)
    peso = st.number_input("Peso (kg)", min_value=30.0, max_value=200.0, value=70.0)
    altezza = st.number_input("Altezza (cm)", min_value=120.0, max_value=220.0, value=170.0)

    opzioni_attivita = {
        "Leggero (poco movimento)": "leggero",
        "Moderato (attività 3-4 volte/sett)": "moderato",
        "Pesante (attività giornaliera)": "pesante"
    }
    scelta = st.selectbox("Livello di attività fisica", list(opzioni_attivita.keys()))
    attivita = opzioni_attivita[scelta]

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
    else:  # Maschio
        bmr = 66.473 + (13.7156 * peso) + (5.033 * altezza) - (6.775 * eta)

    # Calcolo TDEE
    if sesso == "Femmina":
        fattori = {"leggero": 1.42, "moderato": 1.56, "pesante": 1.73}
    else:
        fattori = {"leggero": 1.41, "moderato": 1.70, "pesante": 2.01}
    
    tdee = bmr * fattori[attivita]

    st.subheader("Risultati")
    col_res1, col_res2, col_res3 = st.columns(3)
    col_res1.metric("BMI", f"{bmi}", categoria)
    col_res2.metric("BMR", f"{int(bmr)} kcal")
    col_res3.metric("TDEE", f"{int(tdee)} kcal")

    return int(tdee)

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Meal Macro Planner", layout="wide")
st.title("Meal Macro Planner")

if 'raw_pasti' not in st.session_state:
    st.session_state.raw_pasti = None
if 'modified_pasti' not in st.session_state:
    st.session_state.modified_pasti = None

# --- INPUT CALORIE ---
kcal_total = 1600
if st.checkbox("Calcola BMI, BMR e TDEE"):
    fabbisogno = calcola_bmi_bmr_tdee()
    kcal_total = st.number_input("Modifica o conferma le kcal", value=fabbisogno)
else:
    kcal_total = st.number_input("Inserisci manualmente le kcal giornaliere", min_value=1000, max_value=4000, value=1600)

st.divider()

# --- INPUT PERCENTUALI PASTI ---
st.subheader("Distribuzione Calorica per Pasto")
col1, col2, col3, col4, col5 = st.columns(5)
with col1: perc_col = st.slider("% Colazione", 0, 100, 16)
with col2: perc_spt = st.slider("% Spuntino", 0, 100, 5)
with col3: perc_prz = st.slider("% Pranzo", 0, 100, 39)
with col4: perc_mer = st.slider("% Merenda", 0, 100, 7)
with col5: perc_cen = st.slider("% Cena", 0, 100, 33)

total_perc_pasti = perc_col + perc_spt + perc_prz + perc_mer + perc_cen
if total_perc_pasti != 100:
    st.warning(f"Attenzione: la somma delle percentuali dei pasti è {total_perc_pasti}%. Dovrebbe essere 100%.")

# --- INPUT MACRONUTRIENTI ---
st.subheader("Ripartizione Macronutrienti (%)")
colA, colB, colC = st.columns(3)
with colA: perc_pro = st.slider("% kcal Proteine", 0, 100, 20)
with colB: perc_carb = st.slider("% kcal Carboidrati", 0, 100, 50)
with colC: perc_fat = st.slider("% kcal Grassi", 0, 100, 30)

if perc_pro + perc_carb + perc_fat != 100:
    st.error("La somma dei macronutrienti deve essere 100%!")

# --- VISUALIZZAZIONE MACRO TOTALI ---
g_carb_tot = round((kcal_total * (perc_carb / 100)) / 4, 1)
g_pro_tot = round((kcal_total * (perc_pro / 100)) / 4, 1)
g_fat_tot = round((kcal_total * (perc_fat / 100)) / 9, 1)

st.info(f"**Target Giornaliero:** {g_carb_tot}g Carboidrati | {g_pro_tot}g Proteine | {g_fat_tot}g Grassi")

# --- GENERAZIONE PIANO ---
if st.button("Genera piano pasti completo", type="primary"):
    split = {"carbs": perc_carb / 100, "protein": perc_pro / 100, "fat": perc_fat / 100}
    distrib = {
        "Colazione": perc_col / 100,
        "Spuntino": perc_spt / 100,
        "Pranzo": perc_prz / 100,
        "Merenda": perc_mer / 100,
        "Cena": perc_cen / 100,
    }
    
    pasti = {}
    tabella_riassuntiva = []

    for nome, perc in distrib.items():
        kcal_pasto = kcal_total * perc
        macros = {
            "protein": round((kcal_pasto * split["protein"]) / 4, 1),
            "carbs": round((kcal_pasto * split["carbs"]) / 4, 1),
            "fat": round((kcal_pasto * split["fat"]) / 9, 1),
        }
        
        tabella_riassuntiva.append({
            "Pasto": nome,
            "Calorie (kcal)": int(kcal_pasto),
            "Carbo (g)": macros["carbs"],
            "Pro (g)": macros["protein"],
            "Grassi (g)": macros["fat"]
        })

        foods = suggest_foods(kcal_pasto, nome, split)
        pasti[nome] = {"kcal": kcal_pasto, "macros": macros, "foods": foods}

    st.session_state.raw_pasti = pasti
    st.session_state.modified_pasti = None
    
    st.write("### 📈 Riepilogo Grammi per Pasto")
    st.table(tabella_riassuntiva)

# --- REVISIONE E DOWNLOAD ---
if st.session_state.raw_pasti:
    display_pasti = st.session_state.modified_pasti or st.session_state.raw_pasti
    st.divider()
    st.header("🛒 Revisione Alimenti")
    st.info("Rimuovi gli alimenti che non desideri con la ❌, poi clicca su 'Scarica PDF'")
    
    new_modified = {}

    for pasto, data in display_pasti.items():
        with st.expander(f"{pasto} - {int(data['kcal'])} kcal", expanded=True):
            st.write(f"**Macro:** C: {data['macros']['carbs']}g | P: {data['macros']['protein']}g | G: {data['macros']['fat']}g")
            
            new_foods = {}
            for macro, food_list in data["foods"].items():
                items = [item.strip() for item in food_list.split("|") if item.strip()]
                kept = []
                st.write(f"**{macro.capitalize()} suggeriti:**")
                
                # Layout a colonne per le checkbox degli alimenti
                cols_alimenti = st.columns(3)
                for idx, item in enumerate(items):
                    with cols_alimenti[idx % 3]:
                        checkbox_key = f"{pasto}_{macro}_{item}"
                        remove = st.checkbox(f"❌ {item}", key=checkbox_key)
                        if not remove:
                            kept.append(item)
                new_foods[macro] = " | ".join(kept)
            
            new_modified[pasto] = {"kcal": data["kcal"], "macros": data["macros"], "foods": new_foods}

    st.session_state.modified_pasti = new_modified

    if st.button("📄 Genera e Scarica PDF"):
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
            st.download_button("💾 Download PDF", f, file_name="piano_pasti_personalizzato.pdf")
    
