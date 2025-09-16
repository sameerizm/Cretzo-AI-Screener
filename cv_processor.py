import os
from sentence_transformers import SentenceTransformer, util
import pdfplumber, docx

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_model = None

def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model

def read_pdf(path):
    text = ''
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + ' '
    return text.strip()

def read_docx(path):
    doc = docx.Document(path)
    return ' '.join([p.text for p in doc.paragraphs if p.text])

def extract_text(path):
    ext = path.split('.')[-1].lower()
    if ext == 'pdf':
        return read_pdf(path)
    if ext in ('docx','doc'):
        return read_docx(path)
    return ''

def analyze_cv(jd_path, must_haves, cv_paths):
    model = _get_model()
    jd_text = extract_text(jd_path) or ''
    jd_embed = model.encode(jd_text, convert_to_tensor=True)

    results = []
    for p in cv_paths:
        cv_text = extract_text(p) or ''
        cv_embed = model.encode(cv_text, convert_to_tensor=True)
        sim = util.pytorch_cos_sim(jd_embed, cv_embed)[0][0].item()
        percentage = round(float(sim) * 100.0, 2)
        missing = []
        lower = cv_text.lower()
        for k in must_haves:
            kk = k.strip()
            if not kk:
                continue
            if kk.lower() not in lower:
                missing.append(kk)
        if percentage >= 75 and not missing:
            emoji = '🟢😊'
        elif percentage >= 50:
            emoji = '🟡🙂'
        else:
            emoji = '🔴😟'
        results.append({'cv_name': os.path.basename(p), 'percentage': percentage, 'emoji': emoji, 'missing_skills': missing})
    return results
