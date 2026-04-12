import streamlit as st
from food_suggestions import suggest_foods
from pdf_generator import generate_pdf

# --- 1. FUNZIONE CALCOLO FISIOLOGICO ---
def calcola_bmi_bmr_tdee():
    st.header("Calcolo BMI, BMR e TDEE")
    col_fis1, col_fis2 = st.columns(2)
    with col_fis1:
        sesso = st.selectbox("Sesso", ["Maschio", "Femmina"])
        eta = st.number_input("Età", min_value=10, max_value=100, value=30)
    with col_fis2:
        peso = st.number_input("Peso (kg)", min_value=30.0, max_value=200.0, value=70.0)
        altezza = st.number_input("Altezza (cm)", min_value=120.0, max_value=220.0, value=170.0)

    # Formula Mifflin-St Jeor
    if sesso == "Maschio":
        bmr = (10 * peso) + (6.25 * altezza) - (5 * eta) + 5
    else:
        bmr = (10 * peso) + (6.25 * altezza) - (5 * eta) - 161
    
    tdee = bmr * 1.4  # Moltiplicatore standard attività leggera
    st.info(f"**BMI**: {round(peso/((altezza/100)**2),1)} | **BMR**: {int(bmr)} kcal | **TDEE**: {int(tdee)} kcal")
    return int(tdee)

# --- 2. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Macro Master Planner", layout="wide")
st.title("Meal Macro Planner Personalizzato 📊")

if 'raw_pasti' not in st.session_state:
    st.session_state.raw_pasti = None
if 'modified_pasti' not in st.session_state:
    st.session_state.modified_pasti = None

# --- 3. INPUT CALORIE TOTALI ---
if st.checkbox("Calcola fabbisogno automatico"):
    kcal_total = st.number_input("Kcal Obiettivo:", value=calcola_bmi_bmr_tdee())
else:
    kcal_total = st.number_input("Inserisci manualmente le kcal giornaliere", min_value=800, max_value=5000, value=1600)

st.divider()

# --- 4. DISTRIBUZIONE CALORIE PER PASTO ---
st.subheader("1️⃣ Distribuzione % delle Calorie tra i pasti")
c1, c2, c3, c4, c5 = st.columns(5)
p_col = c1.slider("% Colazione", 0, 100, 20)
p_spt = c2.slider("% Spuntino", 0, 100, 5)
p_prz = c3.slider("% Pranzo", 0, 100, 35)
p_mer = c4.slider("% Merenda", 0, 100, 7)
p_cen = c5.slider("% Cena", 0, 100, 33)

elenco_pasti = {"Colazione": p_col, "Spuntino": p_spt, "Pranzo": p_prz, "Merenda": p_mer, "Cena": p_cen}
totale_perc = sum(elenco_pasti.values())

if totale_perc != 100:
    st.warning(f"Attenzione: la somma delle calorie è {totale_perc}%. Regola gli slider per arrivare a 100%.")

st.divider()

# --- 5. MODULAZIONE MACRO LIVE (Il cuore del problema di Marco) ---
st.subheader("2️⃣ Modula i Macro per pasto e controlla i Totali Giornalieri")

# Inizializziamo i contatori per i totali della giornata
tot_carbo_g = 0.0
tot_prote_g = 0.0
tot_grass_g = 0.0
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
                
                # Calcolo grammi istantaneo per il pasto
                g_c = (kcal_pasto * (c_p/100)) / 4
                g_p_gr = (kcal_pasto * (p_p/100)) / 4
                g_f = (kcal_pasto * (g_p/100)) / 9
                
                # Somma ai totali giornalieri
                tot_carbo_g += g_c
                tot_prote_g += g_p_gr
                tot_grass_g += g_f
                
                config_finale_macro[nome] = {"split": {"carbs": c_p/100, "protein": p_p/100, "fat": g_p/100}, "grammi": (g_c, g_p_gr, g_f)}
                st.caption(f"Grammi {nome}: C: {g_c:.1f}g | P: {g_p_gr:.1f}g | G: {g_f:.1f}g")

with col_dashboard:
    st.markdown("### 📈 Totali Giornalieri Live")
    st.info("Questi valori si aggiornano mentre muovi i cursori dei singoli pasti.")
    
    st.metric("Carboidrati Totali", f"{round(tot_carbo_g, 1)} g")
    st.metric("Proteine Totali", f"{round(tot_prote_g, 1)} g")
    st.metric("Grassi Totali", f"{round(tot_grass_g, 1)} g")
    
    st.write("---")
    # Calcolo % reale sulla giornata
    kcal_fatte = (tot_carbo_g * 4) + (tot_prote_g * 4) + (tot_grass_g * 9)
    if kcal_fatte > 0:
        p_c_real = int((tot_carbo_g * 4 / kcal_fatte) * 100)
        p_p_real = int((tot_prote_g * 4 / kcal_fatte) * 100)
        p_g_real = int((tot_grass_g * 9 / kcal_fatte) * 100)
        st.write(f"**Ripartizione Giornaliera Reale:**")
        st.write(f"Carboidrati: {p_c_real}% | Proteine: {p_p_real}% | Grassi: {p_g_real}%")

st.divider()

# --- 6. GENERAZIONE E REVISIONE ---
if st.button("Genera Piano Alimenti", type="primary"):
    pasti_struttura = {}
    for nome, perc in elenco_pasti.items():
        if perc > 0:
            kcal_p = kcal_total * (perc / 100)
            m = config_finale_macro[nome]
            # Otteniamo i cibi suggeriti
            foods = suggest_foods(kcal_p, nome, m["split"])
            pasti_struttura[nome] = {
                "kcal": kcal_p,
                "macros": {"carbs": round(m["grammi"][0],1), "protein": round(m["grammi"][1],1), "fat": round(m["grammi"][2],1)},
                "foods": foods,
                "split": m["split"]
            }
    st.session_state.raw_pasti = pasti_struttura
    st.session_state.modified_pasti = None

if st.session_state.raw_pasti:
    st.header("🛒 Revisione Alimenti")
    display_pasti = st.session_state.modified_pasti if st.session_state.modified_pasti else st.session_state.raw_pasti
    new_modified = {}

    for pasto, data in display_pasti.items():
        with st.expander(f"Seleziona cibi per {pasto}", expanded=True):
            st.write(f"Target: C:{data['macros']['carbs']}g | P:{data['macros']['protein']}g | G:{data['macros']['fat']}g")
            pasto_foods = {}
            for m_type, f_list in data["foods"].items():
                items = [i.strip() for i in f_list.split("|") if i.strip()]
                kept = []
                st.markdown(f"**{m_type.capitalize()}**")
                cols = st.columns(3)
                for idx, item in enumerate(items):
                    with cols[idx % 3]:
                        if st.checkbox(item, value=True, key=f"check_{pasto}_{m_type}_{item}"):
                            kept.append(item)
                pasto_foods[m_type] = " | ".join(kept)
            
            new_modified[pasto] = {
                "kcal": data["kcal"], "macros": data["macros"], 
                "foods": pasto_foods, "split": data["split"]
            }
    
    st.session_state.modified_pasti = new_modified

    if st.button("📄 Genera e Scarica PDF"):
        # Distribuzione calorie per il PDF
        dist_pdf = {k: v/100 for k, v in elenco_pasti.items()}
        # Nota: passiamo None come split generale perché ora usiamo quelli dei singoli pasti
        path = generate_pdf(st.session_state.modified_pasti, kcal_total, None, dist_pdf)
        with open(path, "rb") as f:
            st.download_button("💾 Scarica PDF Finale", f, file_name="piano_pasti.pdf")
