"""
AI-Powered CV Screening Backend
FastAPI application for screening candidate CVs against job descriptions
"""

from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Set
import re
from io import BytesIO

app = FastAPI(
    title="CV Screening API",
    description="Lightweight CV screening system using skill matching and text overlap",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def extract_text_from_file(file_content: bytes, filename: str) -> str:
    """
    Extract text from uploaded file (supports txt, docx, pdf as plain text)
    
    Args:
        file_content: Raw file bytes
        filename: Original filename with extension
    
    Returns:
        Extracted text content
    """
    try:
        # Attempt to decode as UTF-8 text
        text = file_content.decode('utf-8', errors='ignore')
        return text
    except Exception as e:
        # Fallback: try latin-1 encoding
        try:
            text = file_content.decode('latin-1', errors='ignore')
            return text
        except:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to extract text from {filename}. Ensure file is text-readable."
            )


def normalize_text(text: str) -> str:
    """
    Normalize text for processing: lowercase, remove special chars, extra spaces
    
    Args:
        text: Raw text string
    
    Returns:
        Normalized text
    """
    # Convert to lowercase
    text = text.lower()
    # Remove special characters except spaces
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def extract_words(text: str) -> Set[str]:
    """
    Extract unique words from text (excluding common stop words)
    
    Args:
        text: Normalized text
    
    Returns:
        Set of unique words
    """
    # Common stop words to exclude
    stop_words = {
        'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
        'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
        'to', 'was', 'will', 'with', 'we', 'you', 'your', 'this', 'have',
        'but', 'or', 'not', 'can', 'all', 'were', 'been', 'their', 'there'
    }
    
    words = set(text.split())
    # Filter out stop words and short words (< 3 chars)
    meaningful_words = {w for w in words if len(w) >= 3 and w not in stop_words}
    return meaningful_words


def check_skill_match(cv_text: str, skills: List[str]) -> Dict:
    """
    Check which must-have skills are present in CV
    
    Args:
        cv_text: Normalized CV text
        skills: List of must-have skills
    
    Returns:
        Dictionary with matched skills, missing skills, and match percentage
    """
    matched = []
    missing = []
    
    for skill in skills:
        # Normalize skill for matching
        skill_normalized = normalize_text(skill)
        
        # Check if skill appears in CV (flexible matching)
        if skill_normalized in cv_text:
            matched.append(skill)
        else:
            missing.append(skill)
    
    match_percentage = (len(matched) / len(skills) * 100) if skills else 0
    
    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "total_skills": len(skills),
        "matched_count": len(matched),
        "match_percentage": round(match_percentage, 2)
    }


def calculate_jd_overlap(jd_text: str, cv_text: str) -> float:
    """
    Calculate text overlap between JD and CV using word intersection
    
    Args:
        jd_text: Normalized job description text
        cv_text: Normalized CV text
    
    Returns:
        Overlap percentage (0-100)
    """
    jd_words = extract_words(jd_text)
    cv_words = extract_words(cv_text)
    
    if not jd_words:
        return 0.0
    
    # Calculate intersection
    common_words = jd_words.intersection(cv_words)
    overlap_percentage = (len(common_words) / len(jd_words)) * 100
    
    return round(overlap_percentage, 2)


def calculate_final_score(skill_match_pct: float, jd_overlap_pct: float) -> float:
    """
    Calculate weighted final score
    
    Args:
        skill_match_pct: Must-have skills match percentage
        jd_overlap_pct: JD-CV overlap percentage
    
    Returns:
        Final score (0-100)
    """
    # Weighted scoring: 40% skills, 60% JD overlap
    final_score = (skill_match_pct * 0.4) + (jd_overlap_pct * 0.6)
    return round(final_score, 2)


def assign_verdict(final_score: float) -> str:
    """
    Assign verdict based on final score
    
    Args:
        final_score: Calculated final score
    
    Returns:
        Verdict string
    """
    if final_score >= 75:
        return "Strong Match ✅"
    elif final_score >= 50:
        return "Partial Match ⚠️"
    else:
        return "Not Suitable ❌"


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "active",
        "message": "CV Screening API is running",
        "endpoints": {
            "screen": "/screen (POST)"
        }
    }


@app.post("/screen")
async def screen_candidates(
    jd_file: UploadFile = File(..., description="Job Description file"),
    must_have_skills: str = Form(..., description="Comma-separated must-have skills"),
    cv_files: List[UploadFile] = File(..., description="Candidate CV files")
):
    """
    Screen candidate CVs against job description
    
    Parameters:
        - jd_file: Job description file (txt, docx, pdf)
        - must_have_skills: Comma-separated string of required skills
        - cv_files: List of candidate CV files
    
    Returns:
        JSON array with screening results for each CV
    """
    
    # Validate inputs
    if not cv_files:
        raise HTTPException(status_code=400, detail="At least one CV file is required")
    
    if not must_have_skills.strip():
        raise HTTPException(status_code=400, detail="Must-have skills cannot be empty")
    
    try:
        # Extract JD text
        jd_content = await jd_file.read()
        jd_text_raw = extract_text_from_file(jd_content, jd_file.filename)
        jd_text_normalized = normalize_text(jd_text_raw)
        
        # Parse must-have skills
        skills_list = [skill.strip() for skill in must_have_skills.split(',') if skill.strip()]
        
        if not skills_list:
            raise HTTPException(status_code=400, detail="No valid skills provided")
        
        # Process each CV
        results = []
        
        for cv_file in cv_files:
            try:
                # Extract CV text
                cv_content = await cv_file.read()
                cv_text_raw = extract_text_from_file(cv_content, cv_file.filename)
                cv_text_normalized = normalize_text(cv_text_raw)
                
                # Check skill matches
                skill_match_result = check_skill_match(cv_text_normalized, skills_list)
                
                # Calculate JD overlap
                jd_overlap = calculate_jd_overlap(jd_text_normalized, cv_text_normalized)
                
                # Calculate final score
                final_score = calculate_final_score(
                    skill_match_result['match_percentage'],
                    jd_overlap
                )
                
                # Assign verdict
                verdict = assign_verdict(final_score)
                
                # Compile result
                result = {
                    "candidate_filename": cv_file.filename,
                    "skill_analysis": {
                        "matched_skills": skill_match_result['matched_skills'],
                        "missing_skills": skill_match_result['missing_skills'],
                        "matched_count": skill_match_result['matched_count'],
                        "total_required": skill_match_result['total_skills'],
                        "skill_match_percentage": skill_match_result['match_percentage']
                    },
                    "jd_overlap_percentage": jd_overlap,
                    "final_score": final_score,
                    "verdict": verdict
                }
                
                results.append(result)
                
            except Exception as e:
                # Handle individual CV processing errors
                results.append({
                    "candidate_filename": cv_file.filename,
                    "error": f"Failed to process CV: {str(e)}",
                    "final_score": 0,
                    "verdict": "Processing Error ❌"
                })
        
        # Sort results by final score (highest first)
        results.sort(key=lambda x: x.get('final_score', 0), reverse=True)
        
        return {
            "success": True,
            "job_description_file": jd_file.filename,
            "must_have_skills": skills_list,
            "total_candidates": len(results),
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
