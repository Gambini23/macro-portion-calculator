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
    
    bmr = (10 * peso) + (6.25 * altezza) - (5 * eta) + (5 if sesso == "Maschio" else -161)
    tdee = bmr * 1.4
    st.info(f"**BMR**: {int(bmr)} kcal | **TDEE stimato**: {int(tdee)} kcal")
    return int(tdee)

st.set_page_config(page_title="Macro Master Planner", layout="wide")
st.title("Meal Macro Planner Personalizzato 📊")

if 'raw_pasti' not in st.session_state: st.session_state.raw_pasti = None
if 'modified_pasti' not in st.session_state: st.session_state.modified_pasti = None

# --- INPUT CALORIE ---
if st.checkbox("Calcola fabbisogno"):
    kcal_total = st.number_input("Kcal Obiettivo:", value=calcola_bmi_bmr_tdee())
else:
    kcal_total = st.number_input("Inserisci kcal giornaliere", min_value=800, max_value=5000, value=1600)

st.divider()

# --- DISTRIBUZIONE CALORIE ---
st.subheader("1️⃣ Distribuzione % delle Calorie tra i pasti")
c1, c2, c3, c4, c5 = st.columns(5)
p_col = c1.slider("% Colazione", 0, 100, 20)
p_spt = c2.slider("% Spuntino", 0, 100, 5)
p_prz = c3.slider("% Pranzo", 0, 100, 35)
p_mer = c4.slider("% Merenda", 0, 100, 7)
p_cen = c5.slider("% Cena", 0, 100, 33)

elenco_pasti = {"Colazione": p_col, "Spuntino": p_spt, "Pranzo": p_prz, "Merenda": p_mer, "Cena": p_cen}

st.divider()

# --- MODULAZIONE MACRO LIVE ---
st.subheader("2️⃣ Modula i Macro e controlla i Totali")
tot_carbo_g, tot_prote_g, tot_grass_g = 0.0, 0.0, 0.0
config_finale_macro = {}

col_sliders, col_dashboard = st.columns([0.6, 0.4])

with col_sliders:
    for nome, perc in elenco_pasti.items():
        if perc > 0:
            kcal_pasto = kcal_total * (perc / 100)
            with st.expander(f"Modifica {nome} ({int(kcal_pasto)} kcal)", expanded=True):
                ca, pr, gr = st.columns(3)
                c_p = ca.slider(f"% Carb", 0, 100, 50, key=f"c_{nome}")
                p_p = pr.slider(f"% Prot", 0, 100, 20, key=f"p_{nome}")
                g_p = gr.slider(f"% Gras", 0, 100, 30, key=f"g_{nome}")
                g_c, g_p_gr, g_f = (kcal_pasto*(c_p/100))/4, (kcal_pasto*(p_p/100))/4, (kcal_pasto*(g_p/100))/9
                tot_carbo_g += g_c; tot_prote_g += g_p_gr; tot_grass_g += g_f
                config_finale_macro[nome] = {"split": {"carbs": c_p/100, "protein": p_p/100, "fat": g_p/100}, "grammi": (g_c, g_p_gr, g_f)}

with col_dashboard:
    st.metric("Carboidrati Totali", f"{round(tot_carbo_g, 1)} g")
    st.metric("Proteine Totali", f"{round(tot_prote_g, 1)} g")
    st.metric("Grassi Totali", f"{round(tot_grass_g, 1)} g")

st.divider()

# --- DISCLAIMER MODIFICABILE ---
st.subheader("3️⃣ Personalizza Disclaimer (Terza Pagina)")
disclaimer_default = """Il presente consiglio alimentare ha esclusivamente finalità informative ed esemplificative... [Il resto del tuo testo originale]"""

# Area di testo pre-compilata ma modificabile
testo_disclaimer_utente = st.text_area("Puoi modificare il testo che apparirà nell'ultima pagina del PDF:", value=disclaimer_default, height=200)

st.divider()

# --- GENERAZIONE ---
if st.button("Genera Piano Alimenti", type="primary"):
    pasti_struttura = {}
    for nome, perc in elenco_pasti.items():
        if perc > 0:
            kcal_p = kcal_total * (perc / 100)
            m = config_finale_macro[nome]
            foods = suggest_foods(kcal_p, nome, m["split"])
            pasti_struttura[nome] = {"kcal": kcal_p, "macros": {"carbs": round(m["grammi"][0],1), "protein": round(m["grammi"][1],1), "fat": round(m["grammi"][2],1)}, "foods": foods, "split": m["split"]}
    st.session_state.raw_pasti = pasti_struttura

if st.session_state.raw_pasti:
    st.header("🛒 Revisione e Download")
    # ... (logica checkbox omessa per brevità, rimane uguale a prima)
    
    if st.button("📄 Scarica PDF Finale"):
        kcal_fatte = (tot_carbo_g * 4) + (tot_prote_g * 4) + (tot_grass_g * 9)
        split_medio = {"carbs": (tot_carbo_g * 4) / kcal_fatte, "protein": (tot_prote_g * 4) / kcal_fatte, "fat": (tot_grass_g * 9) / kcal_fatte} if kcal_fatte > 0 else {"carbs": 0.5, "protein": 0.2, "fat": 0.3}
        dist_pdf = {k: v/100 for k, v in elenco_pasti.items()}
        
        # AGGIUNTA: Passiamo il testo del disclaimer modificato alla funzione
        path = generate_pdf(st.session_state.raw_pasti, kcal_total, split_medio, dist_pdf, disclaimer_custom=testo_disclaimer_utente)
        
        with open(path, "rb") as f:
            st.download_button("💾 Download PDF", f, file_name="piano_pasti.pdf")
