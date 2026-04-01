import os
import tempfile
from fpdf import FPDF

def generate_pdf(pasti, kcal_total, split, distrib):
    # 1. Configurazione Percorsi Font
    # Supponendo che i file .ttf siano in una cartella chiamata 'fonts' nella root del progetto
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    font_bold = os.path.join(BASE_DIR, "fonts", "DejaVuSans-Bold.ttf")
    font_regular = os.path.join(BASE_DIR, "fonts", "DejaVuSans.ttf")

    disclaimer = """ Il presente consiglio alimentare ha esclusivamente finalità informative ed esemplificative.
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
 """ # (Il tuo testo rimane invariato)
    linee_guida = """ LINEE GUIDA GENERALI DA SEGUIRE A TAVOLA

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
- Prepara con cura, evita improvvisazioni. """ # (Il tuo testo rimane invariato)

    pdf = FPDF()

    # 2. Caricamento Font con controllo esistenza
    if os.path.exists(font_bold) and os.path.exists(font_regular):
        pdf.add_font('DejaVu', 'B', font_bold, uni=True)
        pdf.add_font('DejaVu', '', font_regular, uni=True)
    else:
        # Fallback ai font standard se i file non vengono trovati (non supportano Unicode però)
        pdf.set_font("Arial", size=12)
        print("ATTENZIONE: Font DejaVu non trovati. Uso font di sistema.")

    pdf.add_page()

    # Intestazione
    pdf.set_font("DejaVu", 'B', 14)
    # ... resto del tuo codice di formattazione ...
    
    # [Mantieni qui tutto il resto del tuo ciclo for pasti e sezioni]

    # Salvataggio
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(tmp.name)
    return tmp.name
