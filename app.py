"""
Cretzo AI - Progressive CV Screening System
Starts basic, adds features as dependencies become available
"""

import os
import json
import uuid
import re
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple

# Core framework (always available)
from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Progressive imports - graceful fallbacks
try:
    from sentence_transformers import SentenceTransformer
    AI_AVAILABLE = True
    AI_MODEL = None
    print("✅ AI libraries found - loading model...")
    try:
        AI_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ AI model loaded successfully")
    except Exception as e:
        print(f"⚠️ AI model loading failed: {e}")
        AI_AVAILABLE = False
except ImportError:
    AI_AVAILABLE = False
    AI_MODEL = None
    print("📝 AI libraries not available - using advanced text analysis")

try:
    import pdfplumber
    PDF_AVAILABLE = True
    print("✅ PDF processing available")
except ImportError:
    PDF_AVAILABLE = False
    print("📝 PDF processing not available")

try:
    from docx import Document as DocxDocument
    DOCX_AVAILABLE = True
    print("✅ DOCX processing available")
except ImportError:
    DOCX_AVAILABLE = False
    print("📝 DOCX processing not available")

try:
    from fpdf import FPDF
    PDF_GEN_AVAILABLE = True
    print("✅ PDF report generation available")
except ImportError:
    PDF_GEN_AVAILABLE = False
    print("📝 PDF report generation not available")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Cretzo AI - Progressive CV Screening",
    description="Human-like CV screening with progressive AI enhancement",
    version="2.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage
screening_results = {}
contact_submissions = []

class SmartCVProcessor:
    """Smart CV processor with progressive enhancement"""
    
    def __init__(self):
        self.ai_model = AI_MODEL
        self.ai_enabled = AI_AVAILABLE and AI_MODEL is not None
        
        # Enhanced skill patterns for text-based analysis
        self.skill_patterns = {
            'programming_languages': [
                r'\b(?:python|java|javascript|js|typescript|c\+\+|c#|php|ruby|go|rust|swift|kotlin|scala)\b',
                r'\b(?:html|css|sass|less|scss)\b'
            ],
            'frameworks': [
                r'\b(?:react|angular|vue|django|flask|spring|laravel|express|fastapi|nodejs|node\.js)\b',
                r'\b(?:bootstrap|tailwind|material-ui|mui|jquery)\b'
            ],
            'databases': [
                r'\b(?:mysql|postgresql|mongodb|redis|elasticsearch|oracle|sqlite|cassandra|dynamodb)\b'
            ],
            'cloud_devops': [
                r'\b(?:aws|azure|gcp|google cloud|docker|kubernetes|k8s|jenkins|git|github|gitlab)\b',
                r'\b(?:terraform|ansible|chef|puppet|nagios|prometheus)\b'
            ],
            'data_ai': [
                r'\b(?:machine learning|ml|ai|data science|tensorflow|pytorch|pandas|numpy|scikit-learn)\b',
                r'\b(?:tableau|power bi|excel|sql|analytics|statistics)\b'
            ],
            'project_management': [
                r'\b(?:agile|scrum|kanban|jira|confluence|project management|pmp|prince2)\b'
            ]
        }
        
        # Synonym mapping for intelligent matching
        self.skill_synonyms = {
            'javascript': ['javascript', 'js', 'ecmascript', 'es6', 'es2015', 'typescript'],
            'react': ['react', 'reactjs', 'react.js', 'redux', 'jsx'],
            'nodejs': ['node.js', 'nodejs', 'node', 'express', 'express.js'],
            'python': ['python', 'py', 'python3', 'django', 'flask', 'fastapi'],
            'aws': ['aws', 'amazon web services', 'ec2', 's3', 'lambda', 'cloudformation'],
            'database': ['sql', 'mysql', 'postgresql', 'mongodb', 'database', 'db'],
            'docker': ['docker', 'containerization', 'containers', 'kubernetes', 'k8s']
        }

    def extract_text_from_file(self, file_content: bytes, filename: str) -> str:
        """Extract text with progressive enhancement"""
        filename_lower = filename.lower()
        
        if filename_lower.endswith('.pdf') and PDF_AVAILABLE:
            return self._extract_pdf(file_content)
        elif filename_lower.endswith(('.docx', '.doc')) and DOCX_AVAILABLE:
            return self._extract_docx(file_content)
        elif filename_lower.endswith('.txt'):
            return self._extract_txt(file_content)
        else:
            # Fallback: try to decode as text
            try:
                return file_content.decode('utf-8', errors='ignore')
            except:
                return f"Could not process {filename} - unsupported format"

    def _extract_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF"""
        try:
            import io
            with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                return text.strip()
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            return f"PDF processing failed: {str(e)}"

    def _extract_docx(self, file_content: bytes) -> str:
        """Extract text from DOCX"""
        try:
            import io
            doc = DocxDocument(io.BytesIO(file_content))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"DOCX extraction error: {e}")
            return f"DOCX processing failed: {str(e)}"

    def _extract_txt(self, file_content: bytes) -> str:
        """Extract text from TXT"""
        try:
            return file_content.decode('utf-8', errors='ignore')
        except:
            try:
                return file_content.decode('latin-1', errors='ignore')
            except:
                return "Text file encoding not supported"

    def extract_skills_comprehensive(self, text: str) -> List[str]:
        """Extract skills using comprehensive pattern matching"""
        skills = set()
        text_lower = text.lower()
        
        # Apply all skill patterns
        for category, patterns in self.skill_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                skills.update(matches)
        
        # Extract from skill sections
        skill_sections = re.findall(
            r'(?:skills|technologies|technical skills|expertise|tools|competencies):?\s*([^\n]*(?:\n[^\n]*){0,15})',
            text_lower, re.IGNORECASE
        )
        
        for section in skill_sections:
            # Split by delimiters
            section_skills = re.split(r'[,;|•\n\-\*\t]', section)
            for skill in section_skills:
                skill = skill.strip()
                if 2 < len(skill) < 30 and not skill.isdigit():
                    skills.add(skill)
        
        return list(skills)

    def calculate_experience_years(self, text: str) -> int:
        """Enhanced experience calculation"""
        # Direct experience mentions
        exp_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|exp)',
            r'experience:?\s*(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s*in\s*(?:software|development|programming|it|tech)',
            r'over\s*(\d+)\s*years?',
            r'more than\s*(\d+)\s*years?',
            r'(\d+)\s*years?\s*professional\s*experience'
        ]
        
        years = []
        for pattern in exp_patterns:
            matches = re.findall(pattern, text.lower(), re.IGNORECASE)
            for match in matches:
                try:
                    years.append(int(match))
                except ValueError:
                    continue
        
        if years:
            return max(years)
        
        # Calculate from employment dates
        current_year = datetime.now().year
        date_patterns = [
            r'\b((?:19|20)\d{2})\s*[-–]\s*((?:19|20)\d{2}|present|current|now)\b',
            r'\b((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*)\s+((?:19|20)\d{2})\s*[-–]\s*((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+(?:19|20)\d{2}|present|current)\b'
        ]
        
        total_years = 0
        for pattern in date_patterns:
            matches = re.findall(pattern, text.lower(), re.IGNORECASE)
            for match in matches:
                try:
                    if len(match) == 2:  # Year format
                        start_year = int(match[0])
                        end_year = current_year if match[1].lower() in ['present', 'current', 'now'] else int(match[1])
                        if end_year >= start_year:
                            total_years += (end_year - start_year)
                except (ValueError, IndexError):
                    continue
        
        return min(total_years, 25)  # Cap at 25 years

    def analyze_seniority_level(self, text: str, experience_years: int) -> str:
        """Determine candidate seniority"""
        text_lower = text.lower()
        
        senior_indicators = ['senior', 'lead', 'principal', 'architect', 'manager', 'director', 'head of', 'chief']
        junior_indicators = ['junior', 'entry', 'trainee', 'intern', 'graduate', 'fresher', 'associate']
        
        senior_count = sum(1 for indicator in senior_indicators if indicator in text_lower)
        junior_count = sum(1 for indicator in junior_indicators if indicator in text_lower)
        
        # Experience-based classification
        if experience_years >= 8 or senior_count >= 2:
            return 'senior'
        elif experience_years <= 2 or junior_count >= 2:
            return 'junior'
        else:
            return 'mid'

    def extract_education(self, text: str) -> List[str]:
        """Extract education information"""
        education = []
        
        education_patterns = [
            r'(?:bachelor|master|phd|doctorate|degree)\s*(?:of|in)?\s*([^\n,.]{5,60})',
            r'(?:b\.?(?:tech|sc|a|e)|m\.?(?:tech|sc|a|ba)|phd|bca|mca)\s*(?:in)?\s*([^\n,.]{5,60})',
            r'(?:university|college|institute)\s*([^\n,.]{10,80})',
            r'(?:diploma|certificate)\s*(?:in)?\s*([^\n,.]{5,60})'
        ]
        
        for pattern in education_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                clean_match = match.strip()
                if clean_match and len(clean_match) > 3:
                    education.append(clean_match)
        
        return education[:5]

    def identify_strengths_weaknesses(self, text: str, skills: List[str], experience_years: int) -> Tuple[List[str], List[str]]:
        """Identify candidate strengths and potential areas for improvement"""
        strengths = []
        weaknesses = []
        text_lower = text.lower()
        
        # Strength indicators
        if experience_years > 8:
            strengths.append("Extensive industry experience")
        elif experience_years > 5:
            strengths.append("Solid professional experience")
        
        if len(skills) > 15:
            strengths.append("Diverse technical skill set")
        elif len(skills) > 8:
            strengths.append("Good technical breadth")
        
        # Leadership indicators
        leadership_terms = ['led', 'managed', 'coordinated', 'mentored', 'supervised', 'directed', 'team lead']
        if sum(1 for term in leadership_terms if term in text_lower) >= 2:
            strengths.append("Leadership experience")
        
        # Achievement indicators
        achievement_terms = ['achieved', 'improved', 'increased', 'reduced', 'delivered', 'implemented', 'optimized']
        if sum(1 for term in achievement_terms if term in text_lower) >= 3:
            strengths.append("Results-oriented with proven achievements")
        
        # Potential weaknesses
        if experience_years < 2:
            weaknesses.append("Limited professional experience")
        
        if len(skills) < 5:
            weaknesses.append("Limited technical skill diversity")
        
        # Check for skill depth vs breadth
        framework_skills = [s for s in skills if any(fw in s.lower() for fw in ['react', 'angular', 'vue', 'django', 'spring'])]
        if len(framework_skills) > 5:
            weaknesses.append("May lack depth in core technologies")
        
        return strengths, weaknesses

    def intelligent_skill_matching(self, cv_skills: List[str], jd_skills: List[str]) -> Tuple[List[str], List[str], float]:
        """Match skills using intelligent text analysis and synonyms"""
        if not cv_skills or not jd_skills:
            return [], jd_skills, 0.0
        
        matched_skills = []
        missing_skills = []
        
        for jd_skill in jd_skills:
            best_match = None
            best_score = 0.0
            
            for cv_skill in cv_skills:
                # Calculate match score
                score = self._calculate_skill_similarity(jd_skill, cv_skill)
                
                if score > best_score:
                    best_match = cv_skill
                    best_score = score
            
            if best_match and best_score > 0.3:  # Threshold for match
                matched_skills.append(f"{jd_skill} → {best_match}")
            else:
                missing_skills.append(jd_skill)
        
        match_percentage = (len(matched_skills) / len(jd_skills)) * 100 if jd_skills else 0
        return matched_skills, missing_skills, match_percentage

    def _calculate_skill_similarity(self, skill1: str, skill2: str) -> float:
        """Calculate similarity between two skills"""
        s1_lower = skill1.lower().strip()
        s2_lower = skill2.lower().strip()
        
        # Direct match
        if s1_lower == s2_lower or s1_lower in s2_lower or s2_lower in s1_lower:
            return 1.0
        
        # Synonym matching
        for main_skill, synonyms in self.skill_synonyms.items():
            if s1_lower in synonyms and s2_lower in synonyms:
                return 0.9
        
        # AI-powered similarity if available
        if self.ai_enabled:
            try:
                embeddings = self.ai_model.encode([skill1, skill2])
                similarity = embeddings[0] @ embeddings[1] / (
                    (embeddings[0] @ embeddings[0]) ** 0.5 * (embeddings[1] @ embeddings[1]) ** 0.5
                )
                return float(similarity)
            except Exception:
                pass
        
        # Fallback: word overlap similarity
        words1 = set(s1_lower.split())
        words2 = set(s2_lower.split())
        if words1 and words2:
            overlap = words1.intersection(words2)
            return len(overlap) / max(len(words1), len(words2))
        
        return 0.0

    def generate_comprehensive_analysis(self, jd_text: str, cv_text: str, candidate_name: str) -> Dict[str, Any]:
        """Generate comprehensive analysis like a human recruiter"""
        
        # Extract information
        cv_skills = self.extract_skills_comprehensive(cv_text)
        jd_skills = self.extract_skills_comprehensive(jd_text)
        experience_years = self.calculate_experience_years(cv_text)
        seniority = self.analyze_seniority_level(cv_text, experience_years)
        education = self.extract_education(cv_text)
        strengths, weaknesses = self.identify_strengths_weaknesses(cv_text, cv_skills, experience_years)
        
        # Skill matching
        matched_skills, missing_skills, skill_match_pct = self.intelligent_skill_matching(cv_skills, jd_skills)
        
        # Calculate comprehensive score
        fit_score = self._calculate_comprehensive_score(
            skill_match_pct, experience_years, len(education), len(strengths), len(weaknesses)
        )
        
        # Generate recommendation
        recommendation = self._generate_recommendation(fit_score, candidate_name, strengths, weaknesses)
        
        return {
            'candidate_name': candidate_name,
            'fit_score': round(fit_score, 1),
            'fit_level': self._get_fit_level(fit_score),
            'emoji': self._get_score_emoji(fit_score),
            'recommendation': recommendation,
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'skill_match_percentage': round(skill_match_pct, 1),
            'experience_years': experience_years,
            'seniority_level': seniority,
            'education': education,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'cv_skills': cv_skills,
            'analysis_type': 'AI-Enhanced' if self.ai_enabled else 'Advanced Text Analysis'
        }

    def _calculate_comprehensive_score(self, skill_match_pct: float, exp_years: int, 
                                     education_count: int, strength_count: int, weakness_count: int) -> float:
        """Calculate comprehensive fit score"""
        
        # Base score from skill matching
        score = skill_match_pct * 0.4  # 40% weight
        
        # Experience component (30% weight)
        if exp_years >= 5:
            score += 30
        elif exp_years >= 2:
            score += 20
        elif exp_years >= 1:
            score += 15
        else:
            score += 5
        
        # Education component (15% weight)
        if education_count > 0:
            score += 15
        else:
            score += 5
        
        # Strengths/weaknesses component (15% weight)
        strength_bonus = min(strength_count * 3, 15)
        weakness_penalty = min(weakness_count * 2, 10)
        score += strength_bonus - weakness_penalty
        
        return min(max(score, 0), 100)  # Ensure 0-100 range

    def _generate_recommendation(self, score: float, name: str, strengths: List[str], weaknesses: List[str]) -> str:
        """Generate human-like recommendation"""
        if score >= 85:
            return f"🌟 Excellent candidate! {name} shows strong alignment with role requirements. {' '.join(strengths[:2])}. Highly recommended for immediate interview."
        elif score >= 75:
            return f"✅ Strong match. {name} demonstrates good fit with solid qualifications. {strengths[0] if strengths else 'Good overall profile'}. Recommend for interview."
        elif score >= 65:
            return f"👍 Moderate fit. {name} has relevant experience but some gaps exist. {'Consider if ' + weaknesses[0].lower() if weaknesses else 'May need additional evaluation'}."
        elif score >= 50:
            return f"⚠️ Below average match. {name} has basic qualifications but significant gaps. {weaknesses[0] if weaknesses else 'Limited alignment with requirements'}."
        else:
            return f"❌ Poor fit. {name} lacks most required qualifications. Not recommended unless requirements are flexible."

    def _get_score_emoji(self, score: float) -> str:
        """Get emoji for score"""
        if score >= 85: return "🌟"
        elif score >= 75: return "✅"
        elif score >= 65: return "👍"
        elif score >= 50: return "⚠️"
        else: return "❌"

    def _get_fit_level(self, score: float) -> str:
        """Get fit level description"""
        if score >= 85: return "Excellent Fit"
        elif score >= 75: return "Good Fit"
        elif score >= 65: return "Moderate Fit"
        elif score >= 50: return "Below Average"
        else: return "Poor Fit"


# Initialize processor
cv_processor = SmartCVProcessor()

# Enhanced HTML with progressive messaging
PROGRESSIVE_HTML = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cretzo AI - Smart CV Screening Platform</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0f1c; color: #fff; line-height: 1.6;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
        
        .header { 
            background: rgba(10,15,28,0.95); padding: 1rem 0; 
            position: fixed; top: 0; width: 100%; z-index: 1000;
            border-bottom: 1px solid #333;
        }
        .header-content { display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 1.5rem; font-weight: 700; color: #0066ff; }
        .nav { display: flex; gap: 2rem; }
        .nav a { color: #94a3b8; text-decoration: none; }
        .nav a:hover { color: #fff; }
        .btn { 
            background: linear-gradient(45deg, #0066ff, #00b4d8); 
            color: white; padding: 0.75rem 1.5rem; border: none; 
            border-radius: 6px; cursor: pointer; font-weight: 600;
            transition: all 0.3s ease;
        }
        .btn:hover { transform: translateY(-1px); }
        
        .hero { 
            min-height: 100vh; display: flex; align-items: center; 
            text-align: center; padding: 100px 20px 50px;
        }
        .hero h1 { 
            font-size: clamp(2.5rem, 5vw, 4rem); font-weight: 700; 
            margin-bottom: 1.5rem; line-height: 1.1;
        }
        .hero p { 
            font-size: 1.25rem; color: #94a3b8; margin-bottom: 3rem; 
            max-width: 600px; margin-left: auto; margin-right: auto;
        }
        .hero-btns { display: flex; gap: 1rem; justify-content: center; margin-bottom: 4rem; }
        
        .stats { 
            display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 2rem; margin-top: 3rem;
        }
        .stat { 
            background: rgba(255,255,255,0.05); padding: 2rem; border-radius: 10px;
            text-align: center; border: 1px solid #333; transition: transform 0.3s ease;
        }
        .stat:hover { transform: translateY(-5px); }
        .stat-number { 
            font-size: 2.5rem; font-weight: 700; color: #0066ff; 
            display: block; margin-bottom: 0.5rem;
        }
        
        .demo { padding: 6rem 0; }
        .demo h2 { font-size: 2.5rem; text-align: center; margin-bottom: 1rem; }
        .demo .subtitle { 
            text-align: center; color: #94a3b8; margin-bottom: 3rem; 
            font-size: 1.1rem; max-width: 800px; margin-left: auto; margin-right: auto;
        }
        .demo-container { 
            background: rgba(255,255,255,0.05); padding: 3rem; 
            border-radius: 15px; border: 1px solid #333;
        }
        .demo-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 3rem; }
        .demo-section { 
            background: rgba(255,255,255,0.03); padding: 2rem; 
            border-radius: 10px; border: 1px solid #333;
        }
        .upload-area { 
            border: 2px dashed #0066ff; padding: 2rem; border-radius: 10px;
            text-align: center; margin-bottom: 1rem; cursor: pointer;
            transition: all 0.3s ease;
        }
        .upload-area:hover { 
            background: rgba(0,102,255,0.05); 
            border-color: #00b4d8;
        }
        .upload-area input { display: none; }
        .upload-status { 
            color: #00b4d8; margin-top: 1rem; font-weight: 500; 
            padding: 0.5rem; background: rgba(0,180,216,0.1); 
            border-radius: 6px; font-size: 0.9rem;
        }
        
        .contact { padding: 6rem 0; }
        .contact h2 { font-size: 2.5rem; text-align: center; margin-bottom: 3rem; }
        .contact-form { 
            max-width: 600px; margin: 0 auto; background: rgba(255,255,255,0.05);
            padding: 3rem; border-radius: 15px; border: 1px solid #333;
        }
        .form-group { margin-bottom: 1.5rem; }
        .form-group label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
        .form-group input, .form-group select, .form-group textarea {
            width: 100%; padding: 1rem; background: rgba(255,255,255,0.05);
            border: 1px solid #333; border-radius: 6px; color: #fff;
        }
        .form-group input:focus, .form-group select:focus, .form-group textarea:focus {
            outline: none; border-color: #0066ff;
        }
        .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
        
        .result-item { 
            display: flex; justify-content: space-between; align-items: flex-start;
            padding: 1.5rem; background: rgba(255,255,255,0.03); border-radius: 8px;
            margin-bottom: 1rem; border-left: 3px solid #0066ff;
            transition: all 0.3s ease;
        }
        .result-item:hover { background: rgba(255,255,255,0.06); transform: translateX(4px); }
        .candidate-info h4 { font-weight: 600; margin-bottom: 0.5rem; }
        .candidate-details { color: #94a3b8; font-size: 0.9rem; line-height: 1.4; }
        .score-section { text-align: right; min-width: 100px; }
        .score { font-size: 1.8rem; font-weight: 700; color: #0066ff; }
        .fit-level { font-size: 0.8rem; color: #94a3b8; margin-top: 0.25rem; }
        
        .
