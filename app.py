"""
CV-JD MATCHING BACKEND SYSTEM
==============================

RUNNING LOCALLY:
----------------
1. Install dependencies:
   pip install -r requirements.txt

2. Run the server:
   uvicorn main:app --reload --host 0.0.0.0 --port 8000

3. Access API docs at: http://localhost:8000/docs

DEPLOYING ON RENDER:
--------------------
1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set Build Command: pip install -r requirements.txt
4. Set Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
5. Add environment variable: PYTHON_VERSION = 3.9.0 (or higher)
6. Deploy!

FRONTEND INTEGRATION (JavaScript):
----------------------------------
// Upload Job Description
const uploadJD = async () => {
    const response = await fetch('https://your-app.onrender.com/upload_jd', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            jd_text: "Looking for Python developer with 5+ years experience...",
            mandatory_keywords: ["Python", "FastAPI", "PostgreSQL"]
        })
    });
    const result = await response.json();
    console.log(result);
};

// Upload CV
const uploadCV = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch('https://your-app.onrender.com/upload_cv', {
        method: 'POST',
        body: formData
    });
    const result = await response.json();
    console.log(result);
};

// Analyze CV against JD
const analyze = async () => {
    const response = await fetch('https://your-app.onrender.com/analyze', {
        method: 'GET'
    });
    const result = await response.json();
    console.log(result);
};
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import re
from io import BytesIO
import uvicorn
from datetime import datetime

# Document processing
try:
    from PyPDF2 import PdfReader
except ImportError:
    from PyPDF2 import PdfFileReader as PdfReader

try:
    from docx import Document
except ImportError:
    import docx
    Document = docx.Document

# Text processing
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Initialize FastAPI app
app = FastAPI(
    title="CV-JD Matching System",
    description="Intelligent CV screening and matching against Job Descriptions",
    version="1.0.0"
)

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your Hostinger domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
storage = {
    "jd": None,
    "jd_text": "",
    "mandatory_keywords": [],
    "cv_text": "",
    "cv_filename": "",
    "uploaded_at": None
}

# Pydantic models
class JobDescription(BaseModel):
    jd_text: str
    mandatory_keywords: Optional[List[str]] = []

class AnalysisResponse(BaseModel):
    match_score: int
    remarks: str
    mandatory_keywords_missing: List[str]
    experience_gap: Optional[str]
    skills_matched: List[str]
    skills_missing: List[str]

# Helper Functions
def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file"""
    try:
        pdf_file = BytesIO(file_content)
        pdf_reader = PdfReader(pdf_file)
        text = ""
        
        # Handle both old and new PyPDF2 API
        if hasattr(pdf_reader, 'pages'):
            pages = pdf_reader.pages
        else:
            pages = [pdf_reader.getPage(i) for i in range(pdf_reader.numPages)]
        
        for page in pages:
            if hasattr(page, 'extract_text'):
                text += page.extract_text()
            else:
                text += page.extractText()
        
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")

def extract_text_from_docx(file_content: bytes) -> str:
    """Extract text from DOCX file"""
    try:
        docx_file = BytesIO(file_content)
        doc = Document(docx_file)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading DOCX: {str(e)}")

def extract_years_of_experience(text: str) -> Optional[int]:
    """Extract years of experience from text using regex patterns"""
    patterns = [
        r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
        r'experience[:\s]+(\d+)\+?\s*years?',
        r'(\d+)\+?\s*yrs?\s+(?:of\s+)?experience',
        r'(\d+)\+?\s*years?\s+(?:in|with)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text.lower())
        if matches:
            return max([int(m) for m in matches])
    
    return None

def extract_skills(text: str) -> List[str]:
    """Extract technical skills from text"""
    # Common technical skills keywords
    skill_keywords = [
        'python', 'java', 'javascript', 'c\\+\\+', 'c#', 'ruby', 'php', 'swift', 'kotlin',
        'react', 'angular', 'vue', 'node', 'express', 'django', 'flask', 'fastapi',
        'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch',
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'ci/cd',
        'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'scikit-learn',
        'rest api', 'graphql', 'microservices', 'agile', 'scrum', 'devops',
        'html', 'css', 'typescript', 'linux', 'bash', 'shell scripting',
        'splunk', 'elk', 'kafka', 'spark', 'hadoop', 'airflow',
        'network security', 'cybersecurity', 'penetration testing', 'firewall',
    ]
    
    text_lower = text.lower()
    found_skills = []
    
    for skill in skill_keywords:
        if re.search(r'\b' + skill + r'\b', text_lower):
            found_skills.append(skill.replace('\\', '').title())
    
    return list(set(found_skills))

def semantic_similarity(text1: str, text2: str) -> float:
    """Calculate semantic similarity using TF-IDF and cosine similarity"""
    if not text1 or not text2:
        return 0.0
    
    try:
        vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=500,
            ngram_range=(1, 2)
        )
        
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        return float(similarity)
    except Exception as e:
        return 0.0

def check_mandatory_keywords(cv_text: str, keywords: List[str]) -> List[str]:
    """Check which mandatory keywords are missing from CV"""
    cv_lower = cv_text.lower()
    missing = []
    
    for keyword in keywords:
        if keyword.lower() not in cv_lower:
            missing.append(keyword)
    
    return missing

def generate_remarks(
    match_score: int,
    missing_keywords: List[str],
    exp_gap: Optional[str],
    skills_matched: List[str],
    skills_missing: List[str]
) -> str:
    """Generate recruiter-style feedback"""
    remarks = []
    
    if match_score >= 80:
        remarks.append("Strong candidate with excellent alignment to the role.")
    elif match_score >= 60:
        remarks.append("Good candidate with relevant experience.")
    else:
        remarks.append("Candidate shows some potential but has significant gaps.")
    
    if skills_matched:
        top_skills = skills_matched[:5]
        remarks.append(f"Demonstrates proficiency in: {', '.join(top_skills)}.")
    
    if missing_keywords:
        remarks.append(f"Missing critical requirements: {', '.join(missing_keywords)}.")
    
    if skills_missing and len(skills_missing) <= 5:
        remarks.append(f"Would benefit from experience in: {', '.join(skills_missing)}.")
    
    if exp_gap:
        remarks.append(f"Experience note: {exp_gap}.")
    
    return " ".join(remarks)

# API Endpoints
@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "status": "active",
        "message": "CV-JD Matching System API",
        "version": "1.0.0",
        "endpoints": {
            "upload_jd": "/upload_jd [POST]",
            "upload_cv": "/upload_cv [POST]",
            "analyze": "/analyze [GET]",
            "docs": "/docs"
        }
    }

@app.post("/upload_jd")
def upload_job_description(jd: JobDescription):
    """
    Upload Job Description with mandatory keywords
    
    Request body:
    {
        "jd_text": "Job description text...",
        "mandatory_keywords": ["Python", "FastAPI", "5+ years"]
    }
    """
    if not jd.jd_text or len(jd.jd_text.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Job description must be at least 50 characters long"
        )
    
    storage["jd"] = jd
    storage["jd_text"] = jd.jd_text
    storage["mandatory_keywords"] = jd.mandatory_keywords or []
    storage["uploaded_at"] = datetime.now().isoformat()
    
    return {
        "success": True,
        "message": "Job description uploaded successfully",
        "jd_length": len(jd.jd_text),
        "mandatory_keywords_count": len(storage["mandatory_keywords"]),
        "mandatory_keywords": storage["mandatory_keywords"]
    }

@app.post("/upload_cv")
async def upload_cv(file: UploadFile = File(...)):
    """
    Upload CV file (PDF or DOCX) and perform initial analysis
    
    Accepts: PDF, DOCX files
    """
    if not storage["jd"]:
        raise HTTPException(
            status_code=400,
            detail="Please upload a job description first using /upload_jd"
        )
    
    # Validate file type
    filename = file.filename.lower()
    if not (filename.endswith('.pdf') or filename.endswith('.docx')):
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are supported"
        )
    
    # Read file content
    content = await file.read()
    
    # Extract text based on file type
    if filename.endswith('.pdf'):
        cv_text = extract_text_from_pdf(content)
    else:
        cv_text = extract_text_from_docx(content)
    
    if not cv_text or len(cv_text.strip()) < 100:
        raise HTTPException(
            status_code=400,
            detail="Could not extract sufficient text from CV. Please ensure the file is not corrupted."
        )
    
    # Store CV
    storage["cv_text"] = cv_text
    storage["cv_filename"] = file.filename
    
    return {
        "success": True,
        "message": "CV uploaded and processed successfully",
        "filename": file.filename,
        "cv_length": len(cv_text),
        "ready_for_analysis": True
    }

@app.get("/analyze", response_model=AnalysisResponse)
def analyze_cv_against_jd():
    """
    Analyze uploaded CV against the Job Description
    
    Returns structured feedback with match score, remarks, and gap analysis
    """
    if not storage["jd"] or not storage["cv_text"]:
        raise HTTPException(
            status_code=400,
            detail="Please upload both Job Description (/upload_jd) and CV (/upload_cv) first"
        )
    
    jd_text = storage["jd_text"]
    cv_text = storage["cv_text"]
    mandatory_keywords = storage["mandatory_keywords"]
    
    # 1. Check mandatory keywords
    missing_keywords = check_mandatory_keywords(cv_text, mandatory_keywords)
    
    # 2. Extract and compare skills
    jd_skills = extract_skills(jd_text)
    cv_skills = extract_skills(cv_text)
    
    skills_matched = [skill for skill in jd_skills if skill in cv_skills]
    skills_missing = [skill for skill in jd_skills if skill not in cv_skills]
    
    # 3. Calculate semantic similarity
    semantic_score = semantic_similarity(jd_text, cv_text)
    
    # 4. Extract years of experience
    jd_years = extract_years_of_experience(jd_text)
    cv_years = extract_years_of_experience(cv_text)
    
    experience_gap = None
    if jd_years and cv_years:
        if cv_years < jd_years:
            gap = jd_years - cv_years
            experience_gap = f"{gap} year{'s' if gap > 1 else ''} less than required ({cv_years} vs {jd_years} years)"
        elif cv_years >= jd_years:
            experience_gap = f"Meets experience requirement ({cv_years} years)"
    elif jd_years:
        experience_gap = "Experience duration not clearly stated in CV"
    
    # 5. Calculate overall match score
    base_score = int(semantic_score * 100)
    
    # Adjust for mandatory keywords
    if mandatory_keywords:
        keyword_penalty = (len(missing_keywords) / len(mandatory_keywords)) * 30
        base_score -= int(keyword_penalty)
    
    # Adjust for skills match
    if jd_skills:
        skills_bonus = (len(skills_matched) / len(jd_skills)) * 15
        base_score += int(skills_bonus)
    
    # Adjust for experience
    if jd_years and cv_years and cv_years < jd_years:
        exp_penalty = min(15, (jd_years - cv_years) * 5)
        base_score -= exp_penalty
    
    # Ensure score is between 0-100
    match_score = max(0, min(100, base_score))
    
    # 6. Generate remarks
    remarks = generate_remarks(
        match_score,
        missing_keywords,
        experience_gap,
        skills_matched,
        skills_missing
    )
    
    return AnalysisResponse(
        match_score=match_score,
        remarks=remarks,
        mandatory_keywords_missing=missing_keywords,
        experience_gap=experience_gap,
        skills_matched=skills_matched[:10],  # Top 10 matched skills
        skills_missing=skills_missing[:10]   # Top 10 missing skills
    )

@app.get("/status")
def get_system_status():
    """Get current system status and uploaded data info"""
    return {
        "jd_uploaded": storage["jd"] is not None,
        "cv_uploaded": bool(storage["cv_text"]),
        "cv_filename": storage.get("cv_filename", ""),
        "mandatory_keywords": storage.get("mandatory_keywords", []),
        "ready_for_analysis": storage["jd"] is not None and bool(storage["cv_text"])
    }

# Run the application (for local development)
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
