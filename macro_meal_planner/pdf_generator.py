from fpdf import FPDF
import tempfile
from datetime import date

# Etichette leggibili per i macronutrienti
MACRO_LABELS = {"carbs": "Carboidrati", "protein": "Proteine", "fat": "Grassi"}

def generate_pdf(pasti, kcal_total, split, distrib, disclaimer_custom=None, consigli_custom=None):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    f_std = "Helvetica"

    # Helper: converti in latin-1 senza crash
    def c(t):
        return str(t).encode("latin-1", "replace").decode("latin-1")

    # ── INTESTAZIONE (helper riutilizzabile) ─────────────────────────────────
    def header(title: str, subtitle: str = ""):
        pdf.set_font(f_std, "B", 15)
        pdf.cell(0, 10, c(title), ln=True)
        if subtitle:
            pdf.set_font(f_std, "I", 10)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(0, 6, c(subtitle), ln=True)
            pdf.set_text_color(0, 0, 0)
        pdf.ln(3)
        pdf.set_draw_color(180, 180, 180)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(4)

    # ────────────────────────────────────────────────────────────────────────
    # PAGINA 1 – RIEPILOGO PASTI
    # ────────────────────────────────────────────────────────────────────────
    pdf.add_page()
    oggi = date.today().strftime("%d/%m/%Y")
    header(
        f"PIANO PASTI  –  {int(kcal_total)} kcal/giorno",
        f"Data: {oggi}  |  Carbo {int(split['carbs']*100)}%  |  Proteine {int(split['protein']*100)}%  |  Grassi {int(split['fat']*100)}%"
    )

    for pasto, data in pasti.items():
        m_p = data["split"]
        kcal_p = int(data["kcal"])

        # Titolo pasto
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font(f_std, "B", 12)
        pdf.cell(
            0, 8,
            c(f"  {pasto.upper()}  –  {kcal_p} kcal"
              f"  [C:{int(m_p['carbs']*100)}%  P:{int(m_p['protein']*100)}%  G:{int(m_p['fat']*100)}%]"),
            ln=True, fill=True
        )

        # Target grammi
        pdf.set_font(f_std, "I", 10)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(
            0, 6,
            c(f"  Target: {data['macros']['carbs']}g carbo  |  "
              f"{data['macros']['protein']}g proteine  |  "
              f"{data['macros']['fat']}g grassi"),
            ln=True
        )
        pdf.set_text_color(0, 0, 0)
        pdf.ln(1)

        # Cibi per macro (solo quelli con % > 0 e selezione non vuota)
        for macro, items in data["foods"].items():
            if not items.strip():
                continue
            if data["split"].get(macro, 0) <= 0:
                continue
            label = MACRO_LABELS.get(macro, macro.capitalize())
            pdf.set_font(f_std, "B", 10)
            pdf.write(5, c(f"  {label}: "))
            pdf.set_font(f_std, "", 10)
            pdf.multi_cell(0, 5, c(items))

        pdf.ln(5)

    # ────────────────────────────────────────────────────────────────────────
    # PAGINA 2 – CONSIGLI ALIMENTARI
    # ────────────────────────────────────────────────────────────────────────
    pdf.add_page()
    header("LINEE GUIDA E CONSIGLI ALIMENTARI")
    pdf.set_font(f_std, "", 10)
    testo_c = consigli_custom if consigli_custom else "Nessuna linea guida inserita."
    pdf.multi_cell(0, 6, c(testo_c.strip()))

    # ────────────────────────────────────────────────────────────────────────
    # PAGINA 3 – DISCLAIMER
    # ────────────────────────────────────────────────────────────────────────
    pdf.add_page()
    header("DISCLAIMER LEGALE")
    pdf.set_font(f_std, "", 9)
    testo_d = disclaimer_custom if disclaimer_custom else "Disclaimer non inserito."
    pdf.multi_cell(0, 5, c(testo_d.strip()))

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(tmp.name)
    return tmp.name
