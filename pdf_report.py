import os
from fpdf import FPDF

REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reports')
os.makedirs(REPORTS_DIR, exist_ok=True)

def generate_pdf_report(screening, cvs):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, f"Screening Report: {screening.jd_name}", ln=True, align='C')
    pdf.ln(4)

    # Basic info
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 8, f"Date: {screening.date}", ln=True)
    pdf.cell(0, 8, f"Must-haves: {screening.must_haves}", ln=True)
    pdf.cell(0, 8, f"Total CVs Processed: {screening.total_cvs}", ln=True)
    pdf.ln(6)

    # CV details
    for c in cvs:
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, f"{c['cv_name']} — {c['percentage']}% {c['emoji']}", ln=True)
        
        pdf.set_font('Arial', '', 11)
        missing = ', '.join(c['missing_skills']) if c['missing_skills'] else 'None'
        pdf.multi_cell(0, 7, f"Missing Skills: {missing}")
        
        notes = c.get('notes', '')
        if notes:
            pdf.multi_cell(0, 7, f"Notes: {notes}")
        
        pdf.ln(4)

    # Save PDF
    out_path = os.path.join(REPORTS_DIR, f'screening_{screening.id}.pdf')
    pdf.output(out_path)
    return out_path
