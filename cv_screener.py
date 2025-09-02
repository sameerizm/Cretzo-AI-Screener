import pdfplumber
import docx2txt
import re
from sentence_transformers import SentenceTransformer, util

class CVScreener:
    def __init__(self):
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')

    def extract_text(self, file_path):
        if file_path.endswith('.pdf'):
            with pdfplumber.open(file_path) as pdf:
                return ' '.join([page.extract_text() for page in pdf.pages if page.extract_text()])
        elif file_path.endswith('.docx'):
            return docx2txt.process(file_path)
        return ""

    def clean_text(self, text):
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def get_score(self, cv_text, jd_text):
        cv_embed = self.embedder.encode(cv_text, convert_to_tensor=True)
        jd_embed = self.embedder.encode(jd_text, convert_to_tensor=True)
        return round(util.pytorch_cos_sim(cv_embed, jd_embed).item() * 100, 2)

    def analyze(self, cv_path, jd_text):
        cv_text = self.clean_text(self.extract_text(cv_path))
        jd_text_clean = self.clean_text(jd_text)
        
        score = self.get_score(cv_text, jd_text_clean)
        
        return {
            "match_score": score,
            "cv_preview": cv_text[:500] + "..."
        }