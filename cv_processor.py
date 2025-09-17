import os
from sentence_transformers import SentenceTransformer, util
import pdfplumber
import docx

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_model = None

def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model

def extract_text(path):
    ext = path.split('.')[-1].lower()
    if ext == 'pdf':
        text = ''
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text += t + ' '
        return text.strip()
    elif ext in ('docx', 'doc'):
        doc = docx.Document(path)
        return ' '.join([p.text for p in doc.paragraphs if p.text])
    return ''

def analyze_cv_advanced(jd_path, cv_paths, must_haves=[], feedback=""):
    model = _get_model()
    jd_text = extract_text(jd_path) or ""
    jd_embed = model.encode(jd_text, convert_to_tensor=True)

    results = []
    for cv_path in cv_paths:
        cv_text = extract_text(cv_path) or ""
        cv_embed = model.encode(cv_text, convert_to_tensor=True)
        sim = util.pytorch_cos_sim(jd_embed, cv_embed)[0][0].item()
        percentage = round(float(sim) * 100.0, 2)

        # Human-like evaluation
        missing = []
        lower = cv_text.lower()
        for k in must_haves:
            if k.lower() not in lower:
                missing.append(k)

        # Assign emoji based on match quality
        if percentage >= 75 and not missing:
            emoji = "🟢😊"
        elif percentage >= 50:
            emoji = "🟡🙂"
        else:
            emoji = "🔴😟"

        results.append({
            "cv_name": os.path.basename(cv_path),
            "percentage": percentage,
            "emoji": emoji,
            "missing_skills": missing,
            "notes": feedback or ""
        })

    return results
