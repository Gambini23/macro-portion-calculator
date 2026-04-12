import streamlit as st
from food_suggestions import suggest_foods
from pdf_generator import generate_pdf

# --- FUNZIONE CALCOLO FISIOLOGICO ---
def calcola_bmi_bmr_tdee():
    st.header("Calcolo BMI, BMR e TDEE")
    col_fis1, col_fis2 = st.columns(2)
    with col_fis1:
        sesso = st.selectbox("Sesso", ["Maschio", "Femmina"])
        eta = st.number_input("Età", min_value=10, max_value=100, value=30)
    with col_fis2:
        peso = st.number_input("Peso (kg)", min_value=30.0, max_value=200.0, value=70.0)
        altezza = st.number_input("Altezza (cm)", min_value=120.0, max_value=220.0, value=170.0)

    opzioni_attivita = {
        "Leggero (poco movimento)": "leggero",
        "Moderato (attività 3-4 volte/sett)": "moderato",
        "Pesante (attività giornaliera)": "pesante"
    }
    scelta = st.selectbox("Livello di attività fisica", list(opzioni_attivita.keys()))
    attivita = opzioni_attivita[scelta]

    altezza_m = altezza / 100
    bmi = round(peso / (altezza_m ** 2), 1)
    
    if sesso == "Femmina":
        bmr = 655.095 + (9.5634 * peso) + (1.849 * altezza) - (4.6756 * eta)
        fattore = {"leggero": 1.42, "moderato": 1.56, "pesante": 1.73}[attivita]
    else:
        bmr = 66.473 + (13.7156 * peso) + (5.033 * altezza) - (6.775 * eta)
        fattore = {"leggero": 1.41, "moderato": 1.70, "pesante": 2.01}[attivita]

    tdee = bmr * fattore
    st.info(f"**BMI**: {bmi} | **BMR**: {int(bmr)} kcal | **TDEE**: {int(tdee)} kcal")
    return int(tdee)

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Custom Macro Planner", layout="wide")
st.title("Meal Macro Planner Personalizzato")

if 'raw_pasti' not in st.session_state:
    st.session_state.raw_pasti = None

# --- 1. SETTING CALORIE TOTALI ---
if st.checkbox("Calcola fabbisogno (BMI/TDEE)"):
    kcal_total = st.number_input("Kcal confermate:", value=calcola_bmi_bmr_tdee())
else:
    kcal_total = st.number_input("Inserisci kcal giornaliere", min_value=800, max_value=5000, value=1600)

st.divider()

# --- 2. RIPARTIZIONE CALORICA PASTI ---
st.subheader("1️⃣ Distribuisci le Calorie tra i pasti")
c1, c2, c3, c4, c5 = st.columns(5)
p_col = c1.slider("% Colazione", 0, 100, 20)
p_spt = c2.slider("% Spuntino", 0, 100, 10)
p_prz = c3.slider("% Pranzo", 0, 100, 35)
p_mer = c4.slider("% Merenda", 0, 100, 10)
p_cen = c5.slider("% Cena", 0, 100, 25)

if (p_col + p_spt + p_prz + p_mer + p_cen) != 100:
    st.warning(f"La somma delle calorie è {p_col+p_spt+p_prz+p_mer+p_cen}%. Regola gli slider per arrivare a 100%.")

st.divider()

# --- 3. CONFIGURAZIONE MACRO SINGOLI PASTI ---
st.subheader("2️⃣ Configura i Macro per ogni singolo pasto")
st.caption("Imposta la % di Carboidrati, Proteine e Grassi specifica per ogni momento della giornata.")

elenco_pasti = {
    "Colazione": p_col, "Spuntino": p_spt, "Pranzo": p_prz, "Merenda": p_mer, "Cena": p_cen
}

macro_config = {}

for nome_pasto, perc_kcal in elenco_pasti.items():
    if perc_kcal > 0:
        with st.expander(f"Configura {nome_pasto} ({int(kcal_total * perc_kcal / 100)} kcal)", expanded=True):
            col_a, col_b, col_c = st.columns(3)
            c = col_a.slider(f"% Carboidrati {nome_pasto}", 0, 100, 50, key=f"c_{nome_pasto}")
            p = col_b.slider(f"% Proteine {nome_pasto}", 0, 100, 20, key=f"p_{nome_pasto}")
            f = col_c.slider(f"% Grassi {nome_pasto}", 0, 100, 30, key=f"f_{nome_pasto}")
            
            if (c + p + f) != 100:
                st.error(f"Errore {nome_pasto}: la somma deve fare 100% (attuale: {c+p+f}%)")
            
            macro_config[nome_pasto] = {"carbs": c/100, "protein": p/100, "fat": f/100}

st.divider()

# --- 4. GENERAZIONE E CALCOLO ---
if st.button("Genera Piano con Macro Differenziati", type="primary"):
    pasti_generati = {}
    riepilogo_dati = []
    
    for nome, perc_pasto in elenco_pasti.items():
        if perc_pasto > 0:
            kcal_pasto = kcal_total * (perc_pasto / 100)
            m = macro_config[nome]
            
            g_carbs = round((kcal_pasto * m["carbs"]) / 4, 1)
            g_proto = round((kcal_pasto * m["protein"]) / 4, 1)
            g_fat = round((kcal_pasto * m["fat"]) / 9, 1)
            
            riepilogo_dati.append({
                "Pasto": nome,
                "Kcal": int(kcal_pasto),
                "Carbo (g)": g_carbs,
                "Proteine (g)": g_proto,
                "Grassi (g)": g_fat
            })
            
            # Chiamata alla funzione esterna per gli alimenti
            foods = suggest_foods(kcal_pasto, nome, m)
            pasti_generati[nome] = {
                "kcal": kcal_pasto, 
                "macros": {"carbs": g_carbs, "protein": g_proto, "fat": g_fat},
                "foods": foods
            }
    
    st.session_state.raw_pasti = pasti_generati
    st.write("### 📊 Grammature Calcolate per Pasto")
    st.table(riepilogo_dati)

# --- 5. REVISIONE E PDF ---
if st.session_state.raw_pasti:
    st.header("📝 Revisione Alimenti e Download")
    # Qui puoi mantenere la logica delle checkbox che avevi prima per filtrare i cibi
    # e poi chiamare generate_pdf...
    if st.button("Genera PDF Finale"):
        st.success("PDF in fase di generazione...")
        # Nota: dovrai passare i nuovi macro differenziati alla funzione generate_pdf
