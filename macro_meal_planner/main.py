import streamlit as st
from food_suggestions import suggest_foods
from pdf_generator import generate_pdf

# ── HELPER: calcolo fisiologico ─────────────────────────────────────────────
def calcola_tdee() -> int:
    st.subheader("Calcolo BMI · BMR · TDEE")
    col1, col2 = st.columns(2)
    with col1:
        sesso  = st.selectbox("Sesso", ["Maschio", "Femmina"])
        eta    = st.number_input("Età", min_value=10, max_value=100, value=30)
    with col2:
        peso   = st.number_input("Peso (kg)",    min_value=30.0,  max_value=200.0, value=70.0)
        altezza = st.number_input("Altezza (cm)", min_value=120.0, max_value=220.0, value=170.0)

    livello = st.selectbox("Livello di attivita'", [
        "Sedentario (lavoro desk, nessun esercizio)",
        "Poco attivo (esercizio leggero 1-3 giorni/sett.)",
        "Moderatamente attivo (esercizio 3-5 giorni/sett.)",
        "Molto attivo (esercizio intenso 6-7 giorni/sett.)",
        "Estremamente attivo (atleta / lavoro fisico pesante)",
    ])
    MOLTIPLICATORI = {
        "Sedentario (lavoro desk, nessun esercizio)":           1.2,
        "Poco attivo (esercizio leggero 1-3 giorni/sett.)":    1.375,
        "Moderatamente attivo (esercizio 3-5 giorni/sett.)":   1.55,
        "Molto attivo (esercizio intenso 6-7 giorni/sett.)":   1.725,
        "Estremamente attivo (atleta / lavoro fisico pesante)": 1.9,
    }
    pal = MOLTIPLICATORI[livello]

    if sesso == "Maschio":
        bmr = (10 * peso) + (6.25 * altezza) - (5 * eta) + 5
    else:
        bmr = (10 * peso) + (6.25 * altezza) - (5 * eta) - 161

    tdee = int(bmr * pal)
    bmi  = round(peso / ((altezza / 100) ** 2), 1)
    st.info(f"**BMI:** {bmi}  |  **BMR:** {int(bmr)} kcal  |  **TDEE stimato:** {tdee} kcal  (x{pal})")
    return tdee

# ── APP ─────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Macro Master Planner", layout="wide", page_icon="📊")
st.title("📊 Meal Macro Planner")
st.caption("Pianifica i tuoi pasti, bilancia i macronutrienti e scarica il PDF personalizzato.")

# Session state
if "raw_pasti" not in st.session_state:
    st.session_state.raw_pasti = None

# ── 1. CALORIE ───────────────────────────────────────────────────────────────
with st.expander("⚙️ Impostazioni Calorie", expanded=True):
    usa_calcolo = st.checkbox("Calcola fabbisogno automaticamente (Harris-Benedict × 1.4)")
    if usa_calcolo:
        tdee_calcolato = calcola_tdee()
        kcal_total = st.number_input("Kcal obiettivo (modifica se vuoi)", min_value=800, max_value=5000, value=tdee_calcolato)
    else:
        kcal_total = st.number_input("Kcal giornaliere", min_value=800, max_value=5000, value=1800)

st.divider()

# ── 2. DISTRIBUZIONE CALORIE ─────────────────────────────────────────────────
st.subheader("1️⃣ Distribuzione % tra i pasti")
c1, c2, c3, c4, c5 = st.columns(5)
p_col = c1.slider("Colazione",  0, 100, 20)
p_spt = c2.slider("Spuntino",   0, 100,  5)
p_prz = c3.slider("Pranzo",     0, 100, 35)
p_mer = c4.slider("Merenda",    0, 100,  7)
p_cen = c5.slider("Cena",       0, 100, 33)

totale_perc = p_col + p_spt + p_prz + p_mer + p_cen
if totale_perc != 100:
    st.warning(f"⚠️ La somma delle % è **{totale_perc}%** — deve essere esattamente 100%.")

elenco_pasti = {
    "Colazione": p_col, "Spuntino": p_spt,
    "Pranzo": p_prz,    "Merenda": p_mer, "Cena": p_cen
}

st.divider()

# ── 3. MACRO PER PASTO ───────────────────────────────────────────────────────
st.subheader("2️⃣ Modulazione macro per pasto")

tot_carbo_g = tot_prote_g = tot_grass_g = 0.0
config_finale_macro = {}

col_sliders, col_dash = st.columns([0.6, 0.4])

with col_sliders:
    for nome, perc in elenco_pasti.items():
        if perc <= 0:
            continue
        kcal_pasto = kcal_total * (perc / 100)
        with st.expander(f"**{nome}** - {int(kcal_pasto)} kcal ({perc}%)", expanded=True):
            ca, pr, gr = st.columns(3)
            c_p = ca.slider("% Carbo",   0, 100, 50, key=f"c_{nome}")
            p_p = pr.slider("% Proteine", 0, 100, 20, key=f"p_{nome}")
            g_p = gr.slider("% Grassi",  0, 100, 30, key=f"g_{nome}")

            g_c   = (kcal_pasto * (c_p / 100)) / 4
            g_p_g = (kcal_pasto * (p_p / 100)) / 4
            g_f   = (kcal_pasto * (g_p / 100)) / 9

            st.markdown(
                f"→ :orange[**{g_c:.1f}g** Carbo]  "
                f":blue[**{g_p_g:.1f}g** Proteine]  "
                f":green[**{g_f:.1f}g** Grassi]"
            )

            somma = c_p + p_p + g_p
            if somma != 100:
                st.error(f"Somma macro: {somma}% — deve fare 100%")

            tot_carbo_g += g_c
            tot_prote_g += g_p_g
            tot_grass_g += g_f

            config_finale_macro[nome] = {
                "split":  {"carbs": c_p / 100, "protein": p_p / 100, "fat": g_p / 100},
                "grammi": (g_c, g_p_g, g_f),
            }

with col_dash:
    st.markdown("### Riepilogo Giornaliero")
    kcal_check = (tot_carbo_g * 4) + (tot_prote_g * 4) + (tot_grass_g * 9)
    st.metric("🟠 Carboidrati",  f"{round(tot_carbo_g, 1)} g")
    st.metric("🔵 Proteine",     f"{round(tot_prote_g, 1)} g")
    st.metric("🟢 Grassi",       f"{round(tot_grass_g, 1)} g")
    st.caption(f"Calorie calcolate: **{int(kcal_check)} kcal**")

st.divider()

# ── 4. TESTI PDF ─────────────────────────────────────────────────────────────
st.subheader("3️⃣ Testi personalizzabili nel PDF")
with st.expander("✏️ Modifica consigli e disclaimer"):
    default_consigli = """Metodi di cottura consigliati:
- Preferisci vapore, forno, friggitrice ad aria, griglia, padella antiaderente, cotture a bassa temperatura o sottovuoto.

Acqua e idratazione:
- Almeno 1 litro ogni 1000 kcal assunte, più acqua in caso di allenamenti o caldo.
- No a bevande zuccherate o gassate.

Olio extravergine d'oliva:
- Solo a crudo, evita la cottura per non alterare i grassi.

Sale e sodio:
- Max 5 g al giorno. Usa spezie, erbe, limone o aceto come alternativa.

Spezie ed erbe aromatiche:
- Libero utilizzo. Ricche di benefici, nessuna caloria.

Verdure:
- Sempre a pranzo e cena. Quantità: doppia rispetto alle proteine.
- Varia colori e tipi. Alterna crudo/cotto.

Alimenti da limitare o evitare:
- Cibi ultra-processati, zuccheri aggiunti, alcolici, grassi trans.

Buone abitudini:
- Mangia lentamente, non saltare pasti, pesa le porzioni.
- Bilancia ogni pasto con fonti di proteine, carboidrati e grassi."""

    default_discl = """Il presente consiglio alimentare ha esclusivamente finalità informative ed esemplificative.
Le combinazioni alimentari, le frequenze settimanali e le porzioni suggerite sono pensate per offrire un orientamento generale sulla distribuzione dei macronutrienti e non costituiscono in alcun modo una prescrizione o una somministrazione dietetica personalizzata.
Le indicazioni contenute nel documento non tengono conto di eventuali allergie, intolleranze alimentari, patologie pregresse o condizioni cliniche specifiche, e pertanto non devono essere utilizzate come sostitutive del parere professionale di figure sanitarie abilitate, quali medici dietologi, biologi nutrizionisti o dietisti.
Le dosi riportate sono state inserite a scopo didattico per fornire un esempio pratico riferito a un soggetto sano, con finalità puramente illustrative in ambito sportivo e educativo.
L'autore declina ogni responsabilità derivante da un uso improprio o non conforme delle informazioni contenute nel documento. Per una valutazione alimentare personalizzata, si raccomanda di rivolgersi a professionisti abilitati."""

    testo_consigli = st.text_area("Consigli alimentari:", value=default_consigli, height=200)
    testo_discl    = st.text_area("Disclaimer:",          value=default_discl,    height=150)

st.divider()

# ── 5. GENERA LISTA ──────────────────────────────────────────────────────────
errori = any(
    (config_finale_macro.get(n, {}).get("split", {}).get("carbs", 0) * 100 +
     config_finale_macro.get(n, {}).get("split", {}).get("protein", 0) * 100 +
     config_finale_macro.get(n, {}).get("split", {}).get("fat", 0) * 100) != 100
    for n, p in elenco_pasti.items() if p > 0 and n in config_finale_macro
)

if st.button("🚀 GENERA LISTA ALIMENTI", type="primary", disabled=(totale_perc != 100 or errori)):
    pasti_struttura = {}
    for nome, perc in elenco_pasti.items():
        if perc <= 0:
            continue
        kcal_p = kcal_total * (perc / 100)
        m = config_finale_macro[nome]
        foods = suggest_foods(kcal_p, nome, m["split"])
        pasti_struttura[nome] = {
            "kcal":   kcal_p,
            "macros": {
                "carbs":   round(m["grammi"][0], 1),
                "protein": round(m["grammi"][1], 1),
                "fat":     round(m["grammi"][2], 1),
            },
            "foods": foods,
            "split": m["split"],
        }
    st.session_state.raw_pasti = pasti_struttura
    st.success("✅ Lista generata! Scorri in basso per la revisione.")

# ── 6. REVISIONE E PDF ───────────────────────────────────────────────────────
if st.session_state.raw_pasti:
    st.divider()
    st.header("🛒 Revisione Alimenti")
    st.caption("Deseleziona gli alimenti che NON vuoi includere nel PDF.")

    MACRO_LABELS = {"protein": "Proteine", "carbs": "Carboidrati", "fat": "Grassi"}
    pasti_per_pdf = {}

    for pasto, data in st.session_state.raw_pasti.items():
        with st.expander(f"**{pasto}** - {int(data['kcal'])} kcal", expanded=True):
            alimenti_filtrati = {}
            for m_type, f_list in data["foods"].items():
                items = [i.strip() for i in f_list.split("|") if i.strip()]
                if not items:
                    alimenti_filtrati[m_type] = ""
                    continue
                label = MACRO_LABELS.get(m_type, m_type.capitalize())
                st.markdown(f"**{label}**")
                kept = []
                cols = st.columns(3)
                for idx, item in enumerate(items):
                    with cols[idx % 3]:
                        if st.checkbox(item, value=True, key=f"rev_{pasto}_{m_type}_{item}"):
                            kept.append(item)
                alimenti_filtrati[m_type] = " | ".join(kept)
            pasti_per_pdf[pasto] = {**data, "foods": alimenti_filtrati}

    st.divider()
    if st.button("📄 CREA PDF FINALE", type="primary"):
        kcal_tot = (tot_carbo_g * 4) + (tot_prote_g * 4) + (tot_grass_g * 9)
        if kcal_tot > 0:
            split_m = {
                "carbs":   (tot_carbo_g * 4) / kcal_tot,
                "protein": (tot_prote_g * 4) / kcal_tot,
                "fat":     (tot_grass_g * 9) / kcal_tot,
            }
        else:
            split_m = {"carbs": 0.5, "protein": 0.2, "fat": 0.3}

        path = generate_pdf(
            pasti_per_pdf,
            kcal_total,
            split_m,
            {k: v / 100 for k, v in elenco_pasti.items()},
            disclaimer_custom=testo_discl,
            consigli_custom=testo_consigli,
        )

        with open(path, "rb") as f:
            st.download_button(
                label="💾 SCARICA PDF",
                data=f,
                file_name="piano_pasti.pdf",
                mime="application/pdf",
            )
        st.success("✅ PDF pronto!")
