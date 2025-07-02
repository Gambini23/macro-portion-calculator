from fpdf import FPDF
import tempfile

def generate_pdf(pasti, kcal_total, split, distrib):
    disclaimer = """
Il presente consiglio alimentare ha esclusivamente finalità informative ed esemplificative.
Le combinazioni alimentari, le frequenze settimanali e le porzioni suggerite sono pensate
per offrire un orientamento generale sulla distribuzione dei macronutrienti e non
costituiscono in alcun modo una prescrizione o una somministrazione dietetica
personalizzata.
Le indicazioni contenute nel documento non tengono conto di eventuali allergie,
intolleranze alimentari, patologie pregresse o condizioni cliniche specifiche, e pertanto
non devono essere utilizzate come sostitutive del parere professionale di figure sanitarie
abilitate, quali medici dietologi, biologi nutrizionisti o dietisti.
Le dosi riportate sono state inserite a scopo didattico per fornire un esempio pratico
riferito a un soggetto sano, di sesso ed età definiti, con finalità puramente illustrative in
ambito sportivo e educativo.
Le indicazioni nutrizionali qui esposte si basano su conoscenze acquisite tramite
formazione in nutrizione sportiva, certificata presso Accademia Italiana Fitness e Sport
Science Lab, nonché sugli attuali studi universitari in corso presso il corso di laurea in
Scienze dell'Alimentazione e Gastronomia (Classe L-26) dell’Università Telematica San
Raffaele.
L’autore declina ogni responsabilità derivante da un uso improprio o non conforme delle
informazioni contenute nel documento. Per una valutazione alimentare personalizzata, si
raccomanda di rivolgersi a professionisti abilitati ai sensi della normativa vigente."""
    linee_guida = """
LINEE GUIDA GENERALI DA SEGUIRE A TAVOLA

Metodi di cottura consigliati:
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
- Bilancia ogni pasto con fonti di proteine, carboidrati e grassi.
- Prepara con cura, evita improvvisazioni.
"""
    

    pdf = FPDF()
    pdf.add_font('DejaVu', 'B', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', uni=True)
    pdf.add_font('DejaVu', '', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', uni=True)
    pdf.add_page()

    # Intestazione
    pdf.set_font("DejaVu", 'B', 14)
    pdf.cell(0, 10, f"PIANO PASTI - {int(kcal_total)} kcal giornaliere", ln=True)
    pdf.ln(4)
    pdf.set_font("DejaVu", '', 11)
    pdf.cell(0, 10, f"Distribuzione macronutrienti: Carboidrati {int(split['carbs']*100)}% | Proteine {int(split['protein']*100)}% | Grassi {int(split['fat']*100)}%", ln=True)
    pdf.ln(5)

    # Pasti
    for pasto, data in pasti.items():
        pdf.set_font("DejaVu", 'B', 13)
        pdf.cell(0, 10, f"{pasto.upper()} ({int(distrib[pasto]*100)}% = {int(data['kcal'])} kcal)", ln=True)
        pdf.set_font("DejaVu", '', 11)
        
        fat_val = data['macros']['fat']
        fat_text = f"{fat_val}g" if fat_val >= 5 else "quota coperta da altri alimenti"
        pdf.cell(0, 10, f"Carboidrati: {data['macros']['carbs']}g | Proteine: {data['macros']['protein']}g | Grassi: {fat_text}", ln=True)
        pdf.ln(2)

        pdf.set_font("DejaVu", 'B', 12)
        pdf.cell(0, 10, "Esempi alimenti:", ln=True)
        pdf.set_font("DejaVu", '', 11)

        for macro, items in data['foods'].items():
            if macro == "fat":
                if fat_val < 5:
                    pdf.multi_cell(0, 8, "Grassi: quota coperta da altri alimenti")
                elif items.strip() != "":
                    pdf.multi_cell(0, 8, f"{macro.capitalize()}: {items}")
            else:
                pdf.multi_cell(0, 8, f"{macro.capitalize()}: {items}")
        
        pdf.ln(3)

    # Disclaimer
    pdf.add_page()
    pdf.set_font("DejaVu", 'B', 14)
    pdf.cell(0, 10, "DISCLAIMER", ln=True)
    pdf.ln(2)
    pdf.set_font("DejaVu", '', 11)
    pdf.multi_cell(0, 5, disclaimer.strip())

    # Aggiunta linee guida
    pdf.add_page()
    pdf.set_font("DejaVu", 'B', 14)
    pdf.cell(0, 10, "LINEE GUIDA GENERALI", ln=True)
    pdf.ln(2)
    pdf.set_font("DejaVu", '', 10)
    pdf.multi_cell(0, 6, linee_guida.strip())

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(tmp.name)
    return tmp.name
