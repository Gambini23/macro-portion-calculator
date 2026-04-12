from fpdf import FPDF
import tempfile

def generate_pdf(pasti, kcal_total, split, distrib, disclaimer_custom=None, consigli_custom=None):
    pdf = FPDF()
    pdf.add_page()
    f_std = "Helvetica"

    def c(t): return str(t).encode('latin-1', 'replace').decode('latin-1')

    # PAGINA 1: INTESTAZIONE E PASTI
    pdf.set_font(f_std, 'B', 14)
    pdf.cell(0, 10, c(f"PIANO PASTI - {int(kcal_total)} kcal giornaliere"), ln=True)
    pdf.set_font(f_std, '', 11)
    macro_info = f"Media Giornaliera: Carbo {int(split['carbs']*100)}% | Pro {int(split['protein']*100)}% | Grassi {int(split['fat']*100)}%"
    pdf.cell(0, 10, c(macro_info), ln=True)
    pdf.ln(5)

    for pasto, data in pasti.items():
        pdf.set_font(f_std, 'B', 13)
        m_p = data['split']
        titolo = f"{pasto.upper()} ({int(data['kcal'])} kcal) [C:{int(m_p['carbs']*100)}% P:{int(m_p['protein']*100)}% G:{int(m_p['fat']*100)}%]"
        pdf.cell(0, 10, c(titolo), ln=True)
        
        pdf.set_font(f_std, '', 11)
        pdf.cell(0, 8, c(f"Target grammi: Carbo {data['macros']['carbs']}g | Pro {data['macros']['protein']}g | Grassi {data['macros']['fat']}g"), ln=True)
        
        for macro, items in data['foods'].items():
            pdf.set_font(f_std, 'B', 11)
            pdf.write(6, c(f"{macro.capitalize()}: "))
            pdf.set_font(f_std, '', 11)
            pdf.multi_cell(0, 6, c(items if items.strip() else "Nessuna selezione"))
        pdf.ln(4)

    # PAGINA 2: CONSIGLI ALIMENTARI (Personalizzata)
    pdf.add_page()
    pdf.set_font(f_std, 'B', 14)
    pdf.cell(0, 10, "LINEE GUIDA E CONSIGLI ALIMENTARI", ln=True)
    pdf.ln(2)
    pdf.set_font(f_std, '', 10)
    testo_c = consigli_custom if consigli_custom else "Nessuna linea guida inserita."
    pdf.multi_cell(0, 6, c(testo_c.strip()))

    # PAGINA 3: DISCLAIMER (Personalizzato)
    pdf.add_page()
    pdf.set_font(f_std, 'B', 14)
    pdf.cell(0, 10, "DISCLAIMER LEGALE", ln=True)
    pdf.ln(2)
    pdf.set_font(f_std, '', 9)
    testo_d = disclaimer_custom if disclaimer_custom else "Disclaimer non inserito."
    pdf.multi_cell(0, 5, c(testo_d.strip()))

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(tmp.name)
    return tmp.name
