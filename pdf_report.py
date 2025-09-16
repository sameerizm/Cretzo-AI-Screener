import os
from fpdf import FPDF

REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reports')
os.makedirs(REPORTS_DIR, exist_ok=True)

def generate_pdf_report(screening, cvs):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font('Arial', size=14)
    pdf.cell(0, 8, f'Screening Report: {screening.jd_name}', ln=True, align='C')
    pdf.ln(4)
    pdf.set_font('Arial', size=11)
    pdf.cell(0, 8, f'Date: {screening.date}', ln=True)
    pdf.cell(0, 8, f'Must-haves: {screening.must_haves}', ln=True)
    pdf.cell(0, 8, f'Total CVs: {screening.total_cvs}', ln=True)
    pdf.ln(6)
    for c in cvs:
        pdf.set_font('Arial', size=12, style='B')
        pdf.cell(0, 8, f'{c.cv_name} — {c.percentage}% {c.emoji}', ln=True)
        pdf.set_font('Arial', size=11)
        missing = c.missing_skills if c.missing_skills else 'None'
        pdf.multi_cell(0, 7, f'Missing Skills: {missing}')
        pdf.ln(4)
    out = os.path.join(REPORTS_DIR, f'screening_{screening.id}.pdf')
    pdf.output(out)
    return out
