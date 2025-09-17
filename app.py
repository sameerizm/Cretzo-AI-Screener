from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
import tempfile
from cv_processor import analyze_cv_advanced
from pdf_report import generate_pdf_report
import datetime

app = FastAPI()

# Allow frontend domain
origins = ["https://cretzo.in"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Temporary folder for uploaded files
UPLOAD_DIR = tempfile.gettempdir()
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ----------------- API ROUTES -----------------
@app.post("/screen")
async def screen_cv(
    jd_file: UploadFile = File(...),
    must_haves: str = Form(...),
    cv_files: List[UploadFile] = File(...),
    feedback: str = Form(default="")
):
    # Save JD file
    jd_path = os.path.join(UPLOAD_DIR, jd_file.filename)
    with open(jd_path, "wb") as f:
        f.write(await jd_file.read())

    # Save CV files
    cv_paths = []
    for cv_file in cv_files:
        cv_path = os.path.join(UPLOAD_DIR, cv_file.filename)
        with open(cv_path, "wb") as f:
            f.write(await cv_file.read())
        cv_paths.append(cv_path)

    # CV analysis
    must_haves_list = [m.strip() for m in must_haves.split(",") if m.strip()]
    results = analyze_cv_advanced(jd_path, cv_paths, must_haves_list, feedback)

    # Screening object for PDF
    class Screening:
        def __init__(self, jd_name, must_haves, total_cvs):
            self.jd_name = jd_name
            self.must_haves = must_haves
            self.total_cvs = total_cvs
            self.date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.id = 12345

    screening = Screening(jd_file.filename, must_haves, len(cv_files))

    # Generate PDF report
    pdf_path = generate_pdf_report(screening, results)

    return {
        "results": results,
        "pdf_path": pdf_path,
        "screening_id": screening.id
    }

@app.get("/health")
def health_check():
    return {"status": "FastAPI app running"}
