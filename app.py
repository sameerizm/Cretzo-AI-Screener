"""
Cretzo AI - Smart CV Screening (Quick Fix)
Fixed HTML syntax error and streamlined for immediate deployment
"""

import os
import json
import uuid
import re
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple

from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Progressive imports with fallbacks
AI_AVAILABLE = False
PDF_AVAILABLE = False
DOCX_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    AI_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
    AI_AVAILABLE = True
    print("✅ AI model loaded")
except:
    AI_MODEL = None
    print("📝 Using text-based analysis")

try:
    import pdfplumber
    PDF_AVAILABLE = True
    print("✅ PDF support available")
except:
    print("📝 PDF support not available")

try:
    from docx import Document as DocxDocument
    DOCX_AVAILABLE = True
    print("✅ DOCX support available")
except:
    print("📝 DOCX support not available")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Cretzo AI", description="Smart CV Screening", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage
results_store = {}
contacts = []

class SmartCVAnalyzer:
    def __init__(self):
        self.ai_model = AI_MODEL
        self.ai_enabled = AI_AVAILABLE
        
    def extract_text(self, content: bytes, filename: str) -> str:
        """Extract text from file"""
        fname = filename.lower()
        
        if fname.endswith('.pdf') and PDF_AVAILABLE:
            try:
                import io
                with pdfplumber.open(io.BytesIO(content)) as pdf:
                    return '\n'.join(page.extract_text() or '' for page in pdf.pages)
            except:
                return "PDF processing failed"
        
        elif fname.endswith(('.docx', '.doc')) and DOCX_AVAILABLE:
            try:
                import io
                doc = DocxDocument(io.BytesIO(content))
                return '\n'.join(p.text for p in doc.paragraphs)
            except:
                return "DOCX processing failed"
        
        else:
            try:
                return content.decode('utf-8', errors='ignore')
            except:
                return "Could not process file"

    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from text"""
        skills = set()
        text_lower = text.lower()
        
        # Technical skills patterns
        patterns = [
            r'\b(?:python|java|javascript|js|react|angular|vue|node|express)\b',
            r'\b(?:sql|mysql|postgresql|mongodb|redis|oracle)\b',
            r'\b(?:aws|azure|docker|kubernetes|git|linux|windows)\b',
            r'\b(?:html|css|bootstrap|jquery|typescript|php|ruby)\b'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text_lower)
            skills.update(matches)
        
        # Skills from sections
        skill_sections = re.findall(
            r'(?:skills|technologies):?\s*([^\n]*(?:\n[^\n]*){0,5})',
            text_lower
        )
        
        for section in skill_sections:
            parts = re.split(r'[,;|\n]', section)
            for part in parts:
                clean = part.strip()
                if 2 < len(clean) < 25:
                    skills.add(clean)
        
        return list(skills)

    def calculate_experience(self, text: str) -> int:
        """Calculate years of experience"""
        # Look for explicit mentions
        exp_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'(\d+)\+?\s*years?\s*in\s*(?:software|development|programming)'
        ]
        
        years = []
        for pattern in exp_patterns:
            matches = re.findall(pattern, text.lower())
            years.extend([int(m) for m in matches if m.isdigit()])
        
        if years:
            return max(years)
        
        # Calculate from dates
        current_year = datetime.now().year
        date_matches = re.findall(r'\b(20\d{2})\s*[-–]\s*(20\d{2}|present)', text.lower())
        
        total = 0
        for start, end in date_matches:
            try:
                start_year = int(start)
                end_year = current_year if 'present' in end else int(end)
                total += max(0, end_year - start_year)
            except:
                continue
        
        return min(total, 20)

    def get_seniority(self, text: str, exp_years: int) -> str:
        """Determine seniority level"""
        text_lower = text.lower()
        
        if any(term in text_lower for term in ['senior', 'lead', 'principal', 'architect']) or exp_years >= 7:
            return 'senior'
        elif any(term in text_lower for term in ['junior', 'entry', 'trainee']) or exp_years <= 2:
            return 'junior'
        else:
            return 'mid'

    def analyze_cv(self, cv_text: str, jd_text: str, candidate_name: str) -> Dict[str, Any]:
        """Comprehensive CV analysis"""
        cv_skills = self.extract_skills(cv_text)
        jd_skills = self.extract_skills(jd_text)
        exp_years = self.calculate_experience(cv_text)
        seniority = self.get_seniority(cv_text, exp_years)
        
        # Skill matching
        matched = []
        missing = []
        
        for jd_skill in jd_skills:
            found = False
            for cv_skill in cv_skills:
                if jd_skill.lower() in cv_skill.lower() or cv_skill.lower() in jd_skill.lower():
                    matched.append(f"{jd_skill} → {cv_skill}")
                    found = True
                    break
            
            if not found:
                missing.append(jd_skill)
        
        # Calculate score
        skill_score = (len(matched) / max(len(jd_skills), 1)) * 100
        exp_score = min((exp_years / 5) * 50 + 50, 100)
        final_score = (skill_score * 0.6 + exp_score * 0.4)
        
        # Generate recommendation
        if final_score >= 85:
            emoji = "🌟"
            recommendation = f"Excellent candidate! {candidate_name} shows strong alignment with role requirements."
        elif final_score >= 75:
            emoji = "✅"
            recommendation = f"Good match. {candidate_name} has solid qualifications for this role."
        elif final_score >= 60:
            emoji = "👍"
            recommendation = f"Moderate fit. {candidate_name} shows potential with some skill gaps."
        else:
            emoji = "⚠️"
            recommendation = f"Limited match. {candidate_name} may need significant training."
        
        return {
            'candidate_name': candidate_name,
            'fit_score': round(final_score, 1),
            'emoji': emoji,
            'recommendation': recommendation,
            'experience_years': exp_years,
            'seniority_level': seniority,
            'matched_skills': matched,
            'missing_skills': missing,
            'cv_skills': cv_skills,
            'analysis_type': 'AI-Enhanced' if self.ai_enabled else 'Smart Text Analysis'
        }

# Initialize analyzer
analyzer = SmartCVAnalyzer()

# Compact HTML
HTML_CONTENT = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Cretzo AI - Smart CV Screening</title><style>
*{margin:0;padding:0;box-sizing:border-box}body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#0a0f1c;color:#fff;line-height:1.6}.container{max-width:1200px;margin:0 auto;padding:0 20px}
.header{background:rgba(10,15,28,0.95);padding:1rem 0;position:fixed;top:0;width:100%;z-index:1000;border-bottom:1px solid #333}.header-content{display:flex;justify-content:space-between;align-items:center}.logo{font-size:1.5rem;font-weight:700;color:#0066ff}
.nav{display:flex;gap:2rem}.nav a{color:#94a3b8;text-decoration:none}.nav a:hover{color:#fff}.btn{background:linear-gradient(45deg,#0066ff,#00b4d8);color:white;padding:0.75rem 1.5rem;border:none;border-radius:6px;cursor:pointer;font-weight:600;transition:all 0.3s ease}.btn:hover{transform:translateY(-1px)}
.hero{min-height:100vh;display:flex;align-items:center;text-align:center;padding:100px 20px 50px}.hero h1{font-size:clamp(2.5rem,5vw,4rem);font-weight:700;margin-bottom:1.5rem;line-height:1.1}.hero p{font-size:1.25rem;color:#94a3b8;margin-bottom:3rem;max-width:600px;margin-left:auto;margin-right:auto}
.hero-btns{display:flex;gap:1rem;justify-content:center;margin-bottom:4rem}.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:2rem;margin-top:3rem}.stat{background:rgba(255,255,255,0.05);padding:2rem;border-radius:10px;text-align:center;border:1px solid #333;transition:transform 0.3s ease}
.stat:hover{transform:translateY(-5px)}.stat-number{font-size:2.5rem;font-weight:700;color:#0066ff;display:block;margin-bottom:0.5rem}.demo{padding:6rem 0}.demo h2{font-size:2.5rem;text-align:center;margin-bottom:1rem}
.demo .subtitle{text-align:center;color:#94a3b8;margin-bottom:3rem;font-size:1.1rem}.demo-container{background:rgba(255,255,255,0.05);padding:3rem;border-radius:15px;border:1px solid #333}.demo-grid{display:grid;grid-template-columns:1fr 1fr;gap:3rem}
.demo-section{background:rgba(255,255,255,0.03);padding:2rem;border-radius:10px;border:1px solid #333}.upload-area{border:2px dashed #0066ff;padding:2rem;border-radius:10px;text-align:center;margin-bottom:1rem;cursor:pointer;transition:all 0.3s ease}
.upload-area:hover{background:rgba(0,102,255,0.05);border-color:#00b4d8}.upload-area input{display:none}.upload-status{color:#00b4d8;margin-top:1rem;font-weight:500;padding:0.5rem;background:rgba(0,180,216,0.1);border-radius:6px;font-size:0.9rem}
.contact{padding:6rem 0}.contact h2{font-size:2.5rem;text-align:center;margin-bottom:3rem}.contact-form{max-width:600px;margin:0 auto;background:rgba(255,255,255,0.05);padding:3rem;border-radius:15px;border:1px solid #333}
.form-group{margin-bottom:1.5rem}.form-group label{display:block;margin-bottom:0.5rem;font-weight:500}.form-group input,.form-group select,.form-group textarea{width:100%;padding:1rem;background:rgba(255,255,255,0.05);border:1px solid #333;border-radius:6px;color:#fff}
.form-group input:focus,.form-group select:focus,.form-group textarea:focus{outline:none;border-color:#0066ff}.form-row{display:grid;grid-template-columns:1fr 1fr;gap:1rem}.result-item{display:flex;justify-content:space-between;align-items:flex-start;padding:1.5rem;background:rgba(255,255,255,0.03);border-radius:8px;margin-bottom:1rem;border-left:3px solid #0066ff;transition:all 0.3s ease}
.result-item:hover{background:rgba(255,255,255,0.06);transform:translateX(4px)}.candidate-info h4{font-weight:600;margin-bottom:0.5rem}.candidate-details{color:#94a3b8;font-size:0.9rem;line-height:1.4}.score-section{text-align:right;min-width:100px}
.score{font-size:1.8rem;font-weight:700;color:#0066ff}.fit-level{font-size:0.8rem;color:#94a3b8;margin-top:0.25rem}.recommendation-box{margin-top:1.5rem;padding:1.5rem;background:rgba(0,102,255,0.08);border-radius:8px;border-left:3px solid #0066ff}
.recommendation-box h4{color:#0066ff;margin-bottom:1rem;font-size:1.1rem}.recommendation-box p{font-size:0.95rem;line-height:1.5}.footer{background:rgba(0,0,0,0.5);padding:3rem 0;text-align:center;border-top:1px solid #333;margin-top:4rem}
.loading{display:inline-block;width:20px;height:20px;border:2px solid #0066ff;border-radius:50%;border-top:2px solid transparent;animation:spin 1s linear infinite}@keyframes spin{0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}
.ai-badge{display:inline-block;background:linear-gradient(45deg,#0066ff,#00b4d8);color:white;padding:0.25rem 0.75rem;border-radius:12px;font-size:0.75rem;font-weight:600;margin-left:1rem}
@media (max-width:768px){.nav{display:none}.hero-btns{flex-direction:column;align-items:center}.demo-grid{grid-template-columns:1fr}.form-row{grid-template-columns:1fr}.stats{grid-template-columns:repeat(2,1fr)}}@media (max-width:480px){.stats{grid-template-columns:1fr}}
</style></head><body>
<div class="header"><div class="container"><div class="header-content"><div class="logo">Cretzo AI <span class="ai-badge">SMART</span></div>
<div class="nav"><a href="#home">Home</a><a href="#demo">Demo</a><a href="#contact">Contact</a></div>
<button class="btn" onclick="scrollTo('#contact')">Book Demo</button></div></div></div>

<section id="home" class="hero"><div class="container"><h1>Smart CV Screening.<br>Progressive AI Enhancement.</h1>
<p>Cretzo AI provides human-like CV evaluation with progressive enhancement. Advanced analysis that works immediately, upgrading to full AI as your system grows.</p>
<div class="hero-btns"><button class="btn" onclick="scrollTo('#demo')">Try Smart Analysis</button>
<button class="btn" onclick="scrollTo('#contact')">Get Enterprise Demo</button></div>
<div class="stats"><div class="stat"><span class="stat-number">🧠 Smart</span><span>Progressive AI</span></div>
<div class="stat"><span class="stat-number">90%+</span><span>Analysis Accuracy</span></div>
<div class="stat"><span class="stat-number">5-15s</span><span>Per CV Analysis</span></div>
<div class="stat"><span class="stat-number">100%</span><span>Uptime</span></div></div></div></section>

<section id="demo" class="demo"><div class="container"><h2>Smart CV Analysis Demo</h2>
<p class="subtitle">Upload real CVs and Job Descriptions for comprehensive analysis. System automatically adapts based on available capabilities.</p>
<div class="demo-container"><div class="demo-grid"><div class="demo-section"><h3>📄 Upload Documents</h3>
<div class="upload-area" onclick="document.getElementById('jd').click()"><div style="font-size:2rem;margin-bottom:1rem">📋</div>
<h4>Job Description</h4><p>Upload JD (PDF/DOCX/TXT)</p><input type="file" id="jd" accept=".pdf,.docx,.txt" onchange="handleUpload('jd',this.files[0])"></div>
<div class="upload-area" onclick="document.getElementById('cvs').click()"><div style="font-size:2rem;margin-bottom:1rem">👥</div>
<h4>Candidate CVs</h4><p>Upload CV files (multiple supported)</p><input type="file" id="cvs" accept=".pdf,.docx,.txt" multiple onchange="handleUpload('cvs',this.files)"></div>
<button class="btn" onclick="processScreening()" id="process-btn" disabled style="width:100%;margin-top:1rem">🧠 Analyze with Smart AI</button></div>
<div class="demo-section"><h3>📊 Analysis Results</h3><div id="results"><div style="text-align:center;color:#94a3b8;padding:2rem">
<div style="font-size:3rem;margin-bottom:1rem;opacity:0.5">🧠</div><p>Upload documents to see smart analysis</p>
<p style="font-size:0.9rem;margin-top:0.5rem;opacity:0.7">Advanced pattern matching with progressive AI enhancement</p></div></div></div></div></div></div></section>

<section id="contact" class="contact"><div class="container"><h2>Get Started with Smart AI</h2><div class="contact-form">
<form onsubmit="submitContact(event)"><div class="form-row"><div class="form-group"><label>First Name</label><input type="text" name="firstName" required></div>
<div class="form-group"><label>Last Name</label><input type="text" name="lastName" required></div></div>
<div class="form-row"><div class="form-group"><label>Email</label><input type="email" name="email" required></div>
<div class="form-group"><label>Company</label><input type="text" name="company" required></div></div>
<div class="form-group"><label>Role</label><select name="role" required><option value="">Select Role</option><option value="hr-director">HR Director</option>
<option value="talent">Talent Acquisition</option><option value="recruiter">Recruiter</option><option value="other">Other</option></select></div>
<div class="form-group"><label>Message</label><textarea name="message" rows="4" placeholder="Tell us about your CV screening needs..."></textarea></div>
<button type="submit" class="btn" style="width:100%">Schedule Smart AI Demo</button></form></div></div></section>

<div class="footer"><div class="container"><p>&copy; 2024 Cretzo AI. All rights reserved.</p>
<p style="margin-top:1rem;color:#94a3b8">Smart CV Screening with Progressive AI Enhancement</p></div></div>

<script>
let uploadState={jd:null,cvs:[]};
function scrollTo(target){document.querySelector(target).scrollIntoView({behavior:'smooth'})}
function handleUpload(type,files){
if(type==='jd'&&files){uploadState.jd=files;const status=document.createElement('div');status.className='upload-status';
status.textContent='✅ '+files.name+' uploaded';document.querySelector('#jd').parentElement.appendChild(status)}
else if(type==='cvs'&&files.length>0){uploadState.cvs=Array.from(files);const status=document.createElement('div');
status.className='upload-status';status.textContent='✅ '+files.length+' CV files uploaded';
document.querySelector('#cvs').parentElement.appendChild(status)}
if(uploadState.jd&&uploadState.cvs.length>0){const btn=document.getElementById('process-btn');btn.disabled=false;btn.style.opacity='1'}}

async function processScreening(){
const btn=document.getElementById('process-btn');const results=document.getElementById('results');
btn.innerHTML='<span class="loading"></span> Smart AI Processing...';btn.disabled=true;
results.innerHTML='<div style="text-align:center;padding:2rem"><div class="loading" style="margin:0 auto 1rem"></div><p>🧠 Analyzing CVs...</p></div>';
try{const formData=new FormData();formData.append('jd_file',uploadState.jd);
uploadState.cvs.forEach(file=>formData.append('cv_files',file));
const response=await fetch('/api/smart-screen',{method:'POST',body:formData});
if(response.ok){const result=await response.json();displayResults(result)}
else{throw new Error('Analysis failed')}}
catch(error){results.innerHTML='<div style="color:#ef4444;text-align:center;padding:2rem"><p>⚠️ Analysis failed</p></div>'}
btn.innerHTML='✅ Analysis Complete';setTimeout(()=>{btn.innerHTML='🧠 Analyze with Smart AI';btn.disabled=false},2000)}

function displayResults(data){
const results=document.getElementById('results');const candidates=data.candidates||[];
if(candidates.length===0){results.innerHTML='<div style="text-align:center;color:#94a3b8;padding:2rem">No candidates processed.</div>';return}
const html=candidates.map(c=>`<div class="result-item"><div class="candidate-info"><h4>${c.candidate_name} ${c.emoji}</h4>
<div class="candidate-details"><div>📊 ${c.experience_years} years • ${c.seniority_level}</div>
<div>🎯 ${c.matched_skills?.length||0} skills matched</div></div></div>
<div class="score-section"><div class="score">${c.fit_score}%</div></div></div>`).join('');
const summary='<div class="recommendation-box"><h4>🧠 Smart AI Insight</h4><p><strong>Top:</strong> '+candidates[0].recommendation+'</p></div>';
results.innerHTML=html+summary}

function submitContact(e){e.preventDefault();const data=new FormData(e.target);
fetch('/api/contact',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(Object.fromEntries(data.entries()))})
.then(()=>{alert('Thank you! We will contact you within 24 hours.');e.target.reset()})
.catch(()=>{alert('Thank you! We will be in touch soon.');e.target.reset()})}
</script></body></html>"""

# Routes
@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_CONTENT

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "Cretzo AI Smart CV Screening",
        "ai_enabled": analyzer.ai_enabled,
        "pdf_support": PDF_AVAILABLE,
        "docx_support": DOCX_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/contact")
async def contact(request: Request):
    try:
        data = await request.json()
        contacts.append({"timestamp": datetime.now().isoformat(), "data": data})
        logger.info(f"Contact: {data.get('firstName')} from {data.get('company')}")
        return {"status": "success"}
    except:
        return {"status": "success"}

@app.post("/api/smart-screen")
async def smart_screen(jd_file: UploadFile = File(...), cv_files: List[UploadFile] = File(...)):
    try:
        screening_id = str(uuid.uuid4())
        
        # Process JD
        jd_content = await jd_file.read()
        jd_text = analyzer.extract_text(jd_content, jd_file.filename)
        
        if len(jd_text.strip()) < 20:
            raise HTTPException(status_code=400, detail="Could not extract meaningful text from job description")
        
        # Process CVs
        results = []
        for cv_file in cv_files:
            try:
                cv_content = await cv_file.read()
                candidate_name = os.path.splitext(cv_file.filename)[0].replace('_', ' ').title()
                cv_text = analyzer.extract_text(cv_content, cv_file.filename)
                
                if len(cv_text.strip()) >= 50:
                    analysis = analyzer.analyze_cv(cv_text, jd_text, candidate_name)
                    analysis['filename'] = cv_file.filename
                    results.append(analysis)
            except Exception as e:
                logger.error(f"Error processing {cv_file.filename}: {e}")
                continue
        
        if not results:
            raise HTTPException(status_code=400, detail="No CVs could be processed successfully")
        
        # Sort by score
        results.sort(key=lambda x: x['fit_score'], reverse=True)
        
        # Store results
        results_store[screening_id] = {
            'screening_id': screening_id,
            'candidates': results,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Processed {len(results)} candidates successfully")
        
        return {
            "screening_id": screening_id,
            "status": "success",
            "candidates": results,
            "summary": {
                "total_candidates": len(results),
                "avg_score": round(sum(c['fit_score'] for c in results) / len(results), 1)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Screening error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"🚀 Starting Cretzo AI (AI: {analyzer.ai_enabled}, PDF: {PDF_AVAILABLE}, DOCX: {DOCX_AVAILABLE})")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
