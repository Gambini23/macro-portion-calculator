from fpdf import FPDF
import tempfile

def generate_pdf(pasti: dict, kcal_total: float, split: dict, distrib: dict) -> str:
    disclaimer = ("""
DISCLAIMER
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
raccomanda di rivolgersi a professionisti abilitati ai sensi della normativa vigente.
""")

    pdf = FPDF()
    pdf.add_font('DejaVu', 'B', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', uni=True)
    pdf.add_font('DejaVu', '', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', uni=True)
    pdf.add_page()
    pdf.set_font("DejaVu", 'B', 14)
    pdf.cell(0, 10, txt=f"PIANO PASTI - {int(kcal_total)} kcal giornaliere", ln=True)
    pdf.ln(4)
    pdf.set_font("DejaVu", '', 11)  # <-- cambiato qui
    pdf.cell(0, 10, txt=f"Distribuzione macronutrienti: Carboidrati {int(split['carbs']*100)}% | Proteine {int(split['protein']*100)}% | Grassi {int(split['fat']*50)}%", ln=True)
    pdf.ln(5)
    
    for pasto, data in pasti.items():
        pdf.set_font("DejaVu", 'B', 13)  # <-- cambiato qui
        pdf.cell(0, 10, txt=f"{pasto.upper()} ({int(distrib[pasto]*100)}% = {int(data['kcal'])} kcal)", ln=True)
        pdf.set_font("DejaVu", '', 11)  # <-- cambiato qui
        pdf.cell(0, 10, txt=f"Carboidrati: {data['macros']['carbs']}g", ln=True)
        pdf.cell(0, 10, txt=f"Proteine: {data['macros']['protein']}g", ln=True)
        fat_val = data['macros']['fat']
        if fat_val < 5:
            pdf.cell(0, 10, txt="Grassi: quota coperta da altri alimenti", ln=True)
        else:
            pdf.cell(0, 10, txt=f"Grassi: {fat_val}g", ln=True)
        pdf.ln(2)
        pdf.set_font("DejaVu", 'B', 12)  # <-- cambiato qui
        pdf.cell(0, 10, txt="Esempi alimenti:", ln=True)
        pdf.set_font("DejaVu", '', 11)  # <-- cambiato qui
        for macro, items in data['foods'].items():
            pdf.multi_cell(0, 8, f"{macro.capitalize()}: {items}")
        pdf.ln(5)
    
    pdf.add_page()
    pdf.set_font("DejaVu", 'B', 12)  # <-- cambiato qui
    pdf.multi_cell(0, 10, disclaimer)
    
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(tmp.name)
    return tmp.name
