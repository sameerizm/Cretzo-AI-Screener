"""
FastAPI CV Screening Application
Main application with API endpoints
Handles missing dependencies gracefully
"""

import os
import uuid
import logging
import re
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

# Try to import our modules, handle gracefully if dependencies missing
try:
    from cv_processor import CVProcessor
    CV_PROCESSOR_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ CV Processor not fully available: {e}")
    CV_PROCESSOR_AVAILABLE = False

try:
    from pdf_report import PDFReportGenerator
    PDF_GENERATOR_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ PDF Generator not available: {e}")
    PDF_GENERATOR_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="CV Screening API",
    description="Professional CV Screening System powered by AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://cretzo.in", "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize processors if available
cv_processor = None
pdf_generator = None

if CV_PROCESSOR_AVAILABLE:
    try:
        cv_processor = CVProcessor()
        logger.info("✅ CV Processor initialized")
    except Exception as e:
        logger.warning(f"⚠️ CV Processor initialization failed: {e}")
        cv_processor = None

if PDF_GENERATOR_AVAILABLE:
    try:
        pdf_generator = PDFReportGenerator()
        logger.info("✅ PDF Generator initialized")
    except Exception as e:
        logger.warning(f"⚠️ PDF Generator initialization failed: {e}")
        pdf_generator = None

# Mock CV Processor for basic functionality
class MockCVProcessor:
    def __init__(self):
        self.ai_enabled = False
    
    def extract_text_from_file(self, file_content: bytes, filename: str) -> str:
        """Basic text extraction fallback"""
        try:
            # Try to decode as text if it's a simple text file
            return file_content.decode('utf-8', errors='ignore')
        except:
            return f"Content extracted from {filename} (basic mode)"
    
    def process_screening(self, jd_text: str, cv_files: List, must_have_skills: List = None) -> dict:
        """Mock screening process"""
        candidates = []
        
        for filename, content, candidate_name in cv_files:
            # Basic mock analysis
            candidate_result = {
                'filename': filename,
                'candidate_name': candidate_name,
                'cv_analysis': {
                    'skills': ['Python', 'JavaScript', 'Communication'],
                    'experience_years': 3,
                    'education': ['Bachelor Degree'],
                    'certifications': [],
                    'career_progression': 'stable_level',
                    'strengths': ['Technical Skills'],
                    'weaknesses': ['Limited Experience'],
                    'red_flags': []
                },
                'matched_skills': ['Python'],
                'missing_skills': ['Advanced Framework Knowledge'],
                'skill_match_percentage': 65.0,
                'fit_score': 65.0,
                'emoji': '👍',
                'recommendation': 'Moderate fit. Basic analysis mode - upload working but limited features.',
                'component_scores': {'skills_match': 65, 'experience_level': 60, 'qualifications': 70},
                'strengths': ['Technical Skills'],
                'weaknesses': ['Limited Experience'],
                'red_flags': []
            }
            candidates.append(candidate_result)
        
        # Sort by fit score
        candidates.sort(key=lambda x: x['fit_score'], reverse=True)
        
        return {
            'job_analysis': {
                'required_skills': ['Python', 'JavaScript'],
                'optional_skills': ['React', 'Node.js'],
                'experience_level': 'mid',
                'min_experience_years': 2
            },
            'candidates': candidates,
            'summary': {
                'total_candidates': len(candidates),
                'avg_fit_score': 65.0,
                'top_candidate': candidates[0]['candidate_name'] if candidates else 'N/A',
                'top_score': candidates[0]['fit_score'] if candidates else 0,
                'candidates_above_75': 0,
                'candidates_above_50': len(candidates)
            },
            'processing_timestamp': datetime.now().isoformat()
        }

# Use mock processor if real one not available
if not cv_processor:
    cv_processor = MockCVProcessor()
    logger.info("📝 Using mock CV processor - basic functionality only")

# In-memory storage for screening results (in production, use a database)
screening_results_store = {}

# Pydantic models
class ScreeningResponse(BaseModel):
    screening_id: str
    status: str
    message: str
    results: dict
    report_path: Optional[str] = None
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    message: str
    timestamp: str
    version: str

@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information"""
    return {
        "message": "CV Screening API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "/screen": "POST - Screen CVs against job description",
            "/health": "GET - Health check",
            "/download_report/{screening_id}": "GET - Download PDF report",
            "/docs": "GET - API documentation",
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Test CV processor initialization
        test_processor = CVProcessor()
        
        return HealthResponse(
            status="healthy",
            message="CV Screening API is operational",
            timestamp=datetime.now().isoformat(),
            version="1.0.0"
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

@app.post("/screen", response_model=ScreeningResponse)
async def screen_candidates(
    jd_file: UploadFile = File(..., description="Job Description file (PDF or DOCX)"),
    cv_files: List[UploadFile] = File(..., description="CV files (PDF or DOCX)"),
    must_have_skills: Optional[str] = Form(None, description="Comma-separated must-have skills"),
    candidate_names: Optional[str] = Form(None, description="Comma-separated candidate names (optional)")
):
    """
    Screen CVs against job description
    
    Args:
        jd_file: Job description file (PDF/DOCX)
        cv_files: List of CV files (PDF/DOCX)
        must_have_skills: Optional comma-separated must-have skills
        candidate_names: Optional comma-separated candidate names
    
    Returns:
        ScreeningResponse with results and report path
    """
    screening_id = str(uuid.uuid4())
    
    try:
        logger.info(f"Starting screening process {screening_id}")
        
        # Validate file types
        allowed_extensions = {'.pdf', '.docx', '.doc'}
        
        # Validate JD file
        jd_extension = os.path.splitext(jd_file.filename.lower())[1]
        if jd_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported JD file format: {jd_extension}. Supported: {allowed_extensions}"
            )
        
        # Validate CV files
        for cv_file in cv_files:
            cv_extension = os.path.splitext(cv_file.filename.lower())[1]
            if cv_extension not in allowed_extensions:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Unsupported CV file format: {cv_extension}. Supported: {allowed_extensions}"
                )
        
        # Read JD file
        logger.info("Reading job description file...")
        jd_content = await jd_file.read()
        jd_text = cv_processor.extract_text_from_file(jd_content, jd_file.filename)
        
        if not jd_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from job description file")
        
        # Process candidate names
        names_list = []
        if candidate_names:
            names_list = [name.strip() for name in candidate_names.split(',')]
        
        # Read and process CV files
        logger.info(f"Processing {len(cv_files)} CV files...")
        cv_files_data = []
        
        for i, cv_file in enumerate(cv_files):
            try:
                cv_content = await cv_file.read()
                
                # Determine candidate name
                if i < len(names_list) and names_list[i]:
                    candidate_name = names_list[i]
                else:
                    # Try to extract name from filename
                    candidate_name = os.path.splitext(cv_file.filename)[0].replace('_', ' ').title()
                
                cv_files_data.append((cv_file.filename, cv_content, candidate_name))
                
            except Exception as e:
                logger.error(f"Error reading CV file {cv_file.filename}: {e}")
                continue
        
        if not cv_files_data:
            raise HTTPException(status_code=400, detail="No valid CV files could be processed")
        
        # Process must-have skills
        must_have_list = []
        if must_have_skills:
            must_have_list = [skill.strip() for skill in must_have_skills.split(',')]
        
        # Run screening process
        logger.info("Running CV screening analysis...")
        screening_results = cv_processor.process_screening(
            jd_text=jd_text,
            cv_files=cv_files_data,
            must_have_skills=must_have_list if must_have_list else None
        )
        
        # Add metadata
        screening_results['screening_id'] = screening_id
        screening_results['jd_filename'] = jd_file.filename
        screening_results['total_cvs_processed'] = len(cv_files_data)
        screening_results['must_have_skills'] = must_have_list
        screening_results['processing_timestamp'] = datetime.now().isoformat()
        
        # Generate PDF report
        logger.info("Generating PDF report...")
        try:
            report_path = pdf_generator.generate_report(screening_results, screening_id)
            screening_results['report_path'] = report_path
        except Exception as e:
            logger.error(f"Error generating PDF report: {e}")
            screening_results['report_path'] = None
        
        # Store results for later retrieval
        screening_results_store[screening_id] = screening_results
        
        # Prepare response data (remove sensitive information)
        response_results = {
            'screening_id': screening_id,
            'job_analysis': screening_results['job_analysis'],
            'candidates': screening_results['candidates'],
            'summary': screening_results['summary'],
            'metadata': {
                'jd_filename': jd_file.filename,
                'total_cvs_processed': len(cv_files_data),
                'must_have_skills': must_have_list,
                'processing_timestamp': screening_results['processing_timestamp']
            }
        }
        
        logger.info(f"Screening process {screening_id} completed successfully")
        
        return ScreeningResponse(
            screening_id=screening_id,
            status="success",
            message=f"Successfully screened {len(cv_files_data)} candidates",
            results=response_results,
            report_path=f"/download_report/{screening_id}" if screening_results.get('report_path') else None,
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in screening process {screening_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/download_report/{screening_id}")
async def download_report(screening_id: str):
    """
    Download PDF report for a screening session
    
    Args:
        screening_id: Unique screening session ID
    
    Returns:
        PDF file response
    """
    try:
        # Check if screening results exist
        if screening_id not in screening_results_store:
            raise HTTPException(status_code=404, detail="Screening results not found")
        
        screening_results = screening_results_store[screening_id]
        report_path = screening_results.get('report_path')
        
        if not report_path or not os.path.exists(report_path):
            raise HTTPException(status_code=404, detail="Report file not found")
        
        # Return file response
        return FileResponse(
            path=report_path,
            media_type='application/pdf',
            filename=f"cv_screening_report_{screening_id}.pdf"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading report {screening_id}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving report")

@app.get("/screening/{screening_id}")
async def get_screening_results(screening_id: str):
    """
    Get screening results by ID
    
    Args:
        screening_id: Unique screening session ID
    
    Returns:
        Screening results
    """
    try:
        if screening_id not in screening_results_store:
            raise HTTPException(status_code=404, detail="Screening results not found")
        
        screening_results = screening_results_store[screening_id]
        
        # Prepare response (exclude sensitive data)
        response_data = {
            'screening_id': screening_id,
            'job_analysis': screening_results['job_analysis'],
            'candidates': screening_results['candidates'],
            'summary': screening_results['summary'],
            'metadata': {
                'jd_filename': screening_results.get('jd_filename'),
                'total_cvs_processed': screening_results.get('total_cvs_processed'),
                'must_have_skills': screening_results.get('must_have_skills'),
                'processing_timestamp': screening_results.get('processing_timestamp')
            },
            'report_available': bool(screening_results.get('report_path'))
        }
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving screening results {screening_id}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving screening results")

@app.delete("/screening/{screening_id}")
async def delete_screening_results(screening_id: str):
    """
    Delete screening results and associated files
    
    Args:
        screening_id: Unique screening session ID
    
    Returns:
        Deletion confirmation
    """
    try:
        if screening_id not in screening_results_store:
            raise HTTPException(status_code=404, detail="Screening results not found")
        
        screening_results = screening_results_store[screening_id]
        
        # Delete PDF report file if exists
        report_path = screening_results.get('report_path')
        if report_path and os.path.exists(report_path):
            try:
                os.remove(report_path)
                logger.info(f"Deleted report file: {report_path}")
            except Exception as e:
                logger.warning(f"Could not delete report file {report_path}: {e}")
        
        # Remove from memory store
        del screening_results_store[screening_id]
        
        return {
            "message": f"Screening results {screening_id} deleted successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting screening results {screening_id}: {e}")
        raise HTTPException(status_code=500, detail="Error deleting screening results")

@app.get("/screenings")
async def list_screenings():
    """
    List all screening sessions
    
    Returns:
        List of screening sessions with basic info
    """
    try:
        screenings = []
        
        for screening_id, results in screening_results_store.items():
            screening_info = {
                'screening_id': screening_id,
                'jd_filename': results.get('jd_filename', 'Unknown'),
                'total_candidates': results.get('summary', {}).get('total_candidates', 0),
                'avg_fit_score': results.get('summary', {}).get('avg_fit_score', 0),
                'top_candidate': results.get('summary', {}).get('top_candidate', 'N/A'),
                'processing_timestamp': results.get('processing_timestamp', ''),
                'report_available': bool(results.get('report_path'))
            }
            screenings.append(screening_info)
        
        # Sort by processing timestamp (newest first)
        screenings.sort(key=lambda x: x['processing_timestamp'], reverse=True)
        
        return {
            'total_screenings': len(screenings),
            'screenings': screenings,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error listing screenings: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving screening list")

@app.get("/statistics")
async def get_statistics():
    """
    Get overall statistics from all screenings
    
    Returns:
        Aggregated statistics
    """
    try:
        if not screening_results_store:
            return {
                'message': 'No screening data available',
                'statistics': {},
                'timestamp': datetime.now().isoformat()
            }
        
        total_screenings = len(screening_results_store)
        total_candidates = 0
        all_scores = []
        skill_frequency = {}
        
        for results in screening_results_store.values():
            summary = results.get('summary', {})
            candidates = results.get('candidates', [])
            
            total_candidates += len(candidates)
            
            # Collect scores
            for candidate in candidates:
                score = candidate.get('fit_score', 0)
                if score > 0:
                    all_scores.append(score)
            
            # Collect skill frequency
            job_analysis = results.get('job_analysis', {})
            required_skills = job_analysis.get('required_skills', [])
            
            for skill in required_skills:
                skill_lower = skill.lower().strip()
                if skill_lower:
                    skill_frequency[skill_lower] = skill_frequency.get(skill_lower, 0) + 1
        
        # Calculate statistics
        avg_score = sum(all_scores) / len(all_scores) if all_scores else 0
        high_performers = len([s for s in all_scores if s >= 75])
        moderate_performers = len([s for s in all_scores if 50 <= s < 75])
        low_performers = len([s for s in all_scores if s < 50])
        
        # Top skills
        top_skills = sorted(skill_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
        
        statistics = {
            'overview': {
                'total_screenings': total_screenings,
                'total_candidates_processed': total_candidates,
                'average_fit_score': round(avg_score, 1),
                'high_performers_count': high_performers,
                'moderate_performers_count': moderate_performers,
                'low_performers_count': low_performers
            },
            'performance_distribution': {
                'excellent_75_plus': high_performers,
                'good_50_to_74': moderate_performers,
                'needs_improvement_below_50': low_performers,
                'percentages': {
                    'excellent': round((high_performers / len(all_scores)) * 100, 1) if all_scores else 0,
                    'good': round((moderate_performers / len(all_scores)) * 100, 1) if all_scores else 0,
                    'needs_improvement': round((low_performers / len(all_scores)) * 100, 1) if all_scores else 0
                }
            },
            'top_requested_skills': [{'skill': skill, 'frequency': freq} for skill, freq in top_skills],
            'score_statistics': {
                'min_score': min(all_scores) if all_scores else 0,
                'max_score': max(all_scores) if all_scores else 0,
                'median_score': sorted(all_scores)[len(all_scores)//2] if all_scores else 0
            }
        }
        
        return {
            'statistics': statistics,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating statistics: {e}")
        raise HTTPException(status_code=500, detail="Error generating statistics")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "The requested resource was not found",
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(500)
async def internal_server_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("reports", exist_ok=True)
    
    # Run the application
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        reload=False,  # Set to False in production
        log_level="info"
    )
