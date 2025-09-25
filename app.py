"""
Integrated FastAPI Application
Serves both the landing page and CV screening API
"""

import os
import uuid
import logging
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Simple logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Cretzo AI - CV Screening Platform",
    description="Enterprise AI-powered CV screening platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for demo purposes
demo_results = {}

# Pydantic models
class ContactSubmission(BaseModel):
    firstName: str
    lastName: str
    email: str
    phone: Optional[str] = None
    company: str
    role: str
    companySize: str
    message: Optional[str] = None

class ScreeningResponse(BaseModel):
    screening_id: str
    status: str
    message: str
    candidates: List[dict]
    timestamp: str

# Landing page HTML content
LANDING_PAGE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cretzo AI - Enterprise CV Screening Platform</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary-blue: #0066ff;
            --secondary-teal: #00b4d8;
            --accent-purple: #6366f1;
            --dark-bg: #0a0f1c;
            --card-bg: rgba(255, 255, 255, 0.08);
            --text-primary: #ffffff;
            --text-secondary: #94a3b8;
            --border-subtle: rgba(255, 255, 255, 0.12);
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Inter', sans-serif;
            background: var(--dark-bg);
            color: var(--text-primary);
            overflow-x: hidden;
            line-height: 1.6;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
        }

        /* Navigation */
        nav {
            position: fixed;
            top: 0;
            width: 100%;
            padding: 1rem 0;
            background: rgba(10, 15, 28, 0.95);
            backdrop-filter: blur(20px);
            z-index: 1000;
            border-bottom: 1px solid var(--border-subtle);
        }

        .nav-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logo {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.75rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--primary-blue) 0%, var(--secondary-teal) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .nav-links {
            display: flex;
            list-style: none;
            gap: 2rem;
        }

        .nav-links a {
            color: var(--text-secondary);
            text-decoration: none;
            font-weight: 500;
            transition: color 0.3s ease;
        }

        .nav-links a:hover {
            color: var(--text-primary);
        }

        .nav-cta {
            background: linear-gradient(135deg, var(--primary-blue) 0%, var(--secondary-teal) 100%);
            color: white;
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.3s ease;
        }

        .nav-cta:hover {
            transform: translateY(-1px);
        }

        /* Hero Section */
        .hero {
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 6rem 0;
            position: relative;
        }

        .hero h1 {
            font-family: 'Space Grotesk', sans-serif;
            font-size: clamp(2.5rem, 6vw, 4rem);
            font-weight: 700;
            margin-bottom: 1.5rem;
            line-height: 1.1;
        }

        .hero p {
            font-size: 1.25rem;
            color: var(--text-secondary);
            margin-bottom: 3rem;
            max-width: 700px;
            margin-left: auto;
            margin-right: auto;
        }

        .hero-ctas {
            display: flex;
            gap: 1.5rem;
            justify-content: center;
            flex-wrap: wrap;
            margin-bottom: 4rem;
        }

        .btn {
            padding: 1rem 2rem;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }

        .btn-primary {
            background: linear-gradient(135deg, var(--primary-blue) 0%, var(--secondary-teal) 100%);
            color: white;
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 102, 255, 0.4);
        }

        .btn-secondary {
            background: transparent;
            color: var(--primary-blue);
            border: 2px solid var(--primary-blue);
        }

        .btn-secondary:hover {
            background: var(--primary-blue);
            color: white;
        }

        /* Stats */
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 2rem;
            margin-top: 3rem;
        }

        .stat-card {
            background: var(--card-bg);
            padding: 2rem;
            border-radius: 12px;
            border: 1px solid var(--border-subtle);
            text-align: center;
            transition: transform 0.3s ease;
        }

        .stat-card:hover {
            transform: translateY(-4px);
        }

        .stat-number {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--primary-blue) 0%, var(--secondary-teal) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            display: block;
        }

        .stat-label {
            color: var(--text-secondary);
            margin-top: 0.5rem;
        }

        /* Demo Section */
        .demo {
            padding: 6rem 0;
        }

        .demo h2 {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 2.5rem;
            text-align: center;
            margin-bottom: 3rem;
        }

        .demo-container {
            background: var(--card-bg);
            border-radius: 16px;
            padding: 3rem;
            border: 1px solid var(--border-subtle);
        }

        .demo-form {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 3rem;
            align-items: start;
        }

        .upload-section {
            background: rgba(255, 255, 255, 0.03);
            padding: 2rem;
            border-radius: 12px;
            border: 1px solid var(--border-subtle);
        }

        .upload-zone {
            border: 2px dashed var(--primary-blue);
            border-radius: 12px;
            padding: 2rem;
            text-align: center;
            margin-bottom: 1rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .upload-zone:hover {
            background: rgba(0, 102, 255, 0.05);
        }

        .upload-zone input {
            display: none;
        }

        .results-section {
            background: rgba(255, 255, 255, 0.03);
            padding: 2rem;
            border-radius: 12px;
            border: 1px solid var(--border-subtle);
        }

        .candidate-result {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            margin-bottom: 1rem;
            border-left: 3px solid var(--primary-blue);
        }

        .score {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--primary-blue);
        }

        /* Contact Section */
        .contact {
            padding: 6rem 0;
        }

        .contact h2 {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 2.5rem;
            text-align: center;
            margin-bottom: 3rem;
        }

        .contact-form {
            max-width: 600px;
            margin: 0 auto;
            background: var(--card-bg);
            padding: 3rem;
            border-radius: 16px;
            border: 1px solid var(--border-subtle);
        }

        .form-group {
            margin-bottom: 1.5rem;
        }

        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
        }

        .form-group input,
        .form-group select,
        .form-group textarea {
            width: 100%;
            padding: 1rem;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border-subtle);
            border-radius: 8px;
            color: var(--text-primary);
            font-family: inherit;
        }

        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: var(--primary-blue);
        }

        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
        }

        /* Footer */
        footer {
            background: rgba(0, 0, 0, 0.5);
            padding: 3rem 0;
            text-align: center;
            border-top: 1px solid var(--border-subtle);
        }

        .footer-content {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 2rem;
            margin-bottom: 2rem;
        }

        .footer-section h4 {
            font-family: 'Space Grotesk', sans-serif;
            margin-bottom: 1rem;
            color: var(--primary-blue);
        }

        .footer-links {
            list-style: none;
        }

        .footer-links a {
            color: var(--text-secondary);
            text-decoration: none;
            transition: color 0.3s ease;
        }

        .footer-links a:hover {
            color: var(--text-primary);
        }

        /* Loading States */
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 2px solid var(--primary-blue);
            border-radius: 50%;
            border-top: 2px solid transparent;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        /* Responsive */
        @media (max-width: 768px) {
            .nav-links { display: none; }
            .hero-ctas { flex-direction: column; align-items: center; }
            .demo-form { grid-template-columns: 1fr; }
            .form-row { grid-template-columns: 1fr; }
            .stats { grid-template-columns: repeat(2, 1fr); }
        }

        @media (max-width: 480px) {
            .stats { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav>
        <div class="container">
            <div class="nav-container">
                <div class="logo">Cretzo AI</div>
                <ul class="nav-links">
                    <li><a href="#home">Home</a></li>
                    <li><a href="#demo">Demo</a></li>
                    <li><a href="#contact">Contact</a></li>
                    <li><a href="/api/docs">API</a></li>
                </ul>
                <button class="nav-cta" onclick="scrollToContact()">Book Demo</button>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <section id="home" class="hero">
        <div class="container">
            <h1>Smarter CV Screening.<br>Human-like AI Decisions.</h1>
            <p>Cretzo AI helps enterprises screen CVs like top recruiters — faster, accurate, and cost-effective. Transform your recruitment process with enterprise-grade AI intelligence.</p>
            
            <div class="hero-ctas">
                <button class="btn btn-primary" onclick="scrollToDemo()">Try Live Demo</button>
                <button class="btn btn-secondary" onclick="scrollToContact()">Book Enterprise Demo</button>
            </div>

            <div class="stats">
                <div class="stat-card">
                    <span class="stat-number">65%</span>
                    <span class="stat-label">Cost Reduction</span>
                </div>
                <div class="stat-card">
                    <span class="stat-number">10x</span>
                    <span class="stat-label">Faster Processing</span>
                </div>
                <div class="stat-card">
                    <span class="stat-number">95%</span>
                    <span class="stat-label">Accuracy Rate</span>
                </div>
                <div class="stat-card">
                    <span class="stat-number">500+</span>
                    <span class="stat-label">Enterprise Clients</span>
                </div>
            </div>
        </div>
    </section>

    <!-- Demo Section -->
    <section id="demo" class="demo">
        <div class="container">
            <h2>Try Cretzo AI Live Demo</h2>
            <div class="demo-container">
                <div class="demo-form">
                    <div class="upload-section">
                        <h3>Upload Documents</h3>
                        
                        <div class="upload-zone" onclick="document.getElementById('jd-file').click()">
                            <div style="font-size: 2rem; margin-bottom: 1rem;">📋</div>
                            <h4>Job Description</h4>
                            <p>Upload JD (PDF/DOCX)</p>
                            <input type="file" id="jd-file" accept=".pdf,.docx" onchange="handleFileUpload('jd', this.files[0])">
                        </div>
                        
                        <div class="upload-zone" onclick="document.getElementById('cv-files').click()">
                            <div style="font-size: 2rem; margin-bottom: 1rem;">📄</div>
                            <h4>Candidate CVs</h4>
                            <p>Upload multiple CVs</p>
                            <input type="file" id="cv-files" accept=".pdf,.docx" multiple onchange="handleFileUpload('cv', this.files)">
                        </div>
                        
                        <button class="btn btn-primary" onclick="processScreening()" id="process-btn" disabled style="width: 100%; margin-top: 1rem;">
                            Process with AI
                        </button>
                    </div>
                    
                    <div class="results-section">
                        <h3>AI Results</h3>
                        <div id="results-container">
                            <div style="text-align: center; color: var(--text-secondary); padding: 2rem;">
                                Upload documents to see AI analysis
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Contact Section -->
    <section id="contact" class="contact">
        <div class="container">
            <h2>Get Started with Cretzo AI</h2>
            <div class="contact-form">
                <form id="contact-form" onsubmit="submitContact(event)">
                    <div class="form-row">
                        <div class="form-group">
                            <label>First Name</label>
                            <input type="text" name="firstName" required>
                        </div>
                        <div class="form-group">
                            <label>Last Name</label>
                            <input type="text" name="lastName" required>
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label>Email</label>
                            <input type="email" name="email" required>
                        </div>
                        <div class="form-group">
                            <label>Phone</label>
                            <input type="tel" name="phone">
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label>Company</label>
                            <input type="text" name="company" required>
                        </div>
                        <div class="form-group">
                            <label>Role</label>
                            <select name="role" required>
                                <option value="">Select Role</option>
                                <option value="hr-director">HR Director</option>
                                <option value="talent-acquisition">Talent Acquisition</option>
                                <option value="chro">CHRO</option>
                                <option value="other">Other</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label>Company Size</label>
                        <select name="companySize" required>
                            <option value="">Select Size</option>
                            <option value="50-200">50-200 employees</option>
                            <option value="200-1000">200-1,000 employees</option>
                            <option value="1000+">1,000+ employees</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label>Message</label>
                        <textarea name="message" rows="4" placeholder="Tell us about your recruitment challenges..."></textarea>
                    </div>
                    
                    <button type="submit" class="btn btn-primary" style="width: 100%;">
                        Schedule Enterprise Demo
                    </button>
                </form>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer>
        <div class="container">
            <div class="footer-content">
                <div class="footer-section">
                    <h4>Cretzo AI</h4>
                    <p style="color: var(--text-secondary);">Enterprise AI recruitment platform</p>
                </div>
                <div class="footer-section">
                    <h4>Product</h4>
                    <ul class="footer-links">
                        <li><a href="#demo">Demo</a></li>
                        <li><a href="/api/docs">API</a></li>
                        <li><a href="#contact">Contact</a></li>
                    </ul>
                </div>
                <div class="footer-section">
                    <h4>Legal</h4>
                    <ul class="footer-links">
                        <li><a href="#">Privacy Policy</a></li>
                        <li><a href="#">Terms of Service</a></li>
                        <li><a href="#">GDPR Compliance</a></li>
                    </ul>
                </div>
            </div>
            <p>&copy; 2024 Cretzo AI. All rights reserved.</p>
        </div>
    </footer>

    <script>
        // Global state
        let uploadedFiles = {
            jd: null,
            cv: []
        };

        // API base URL - will be automatically set to current domain
        const API_BASE = window.location.origin;

        // Navigation functions
        function scrollToDemo() {
            document.getElementById('demo').scrollIntoView({ behavior: 'smooth' });
        }

        function scrollToContact() {
            document.getElementById('contact').scrollIntoView({ behavior: 'smooth' });
        }

        // File upload handling
        function handleFileUpload(type, files) {
            if (type === 'jd' && files) {
                uploadedFiles.jd = files;
                updateUploadStatus();
            } else if (type === 'cv' && files.length > 0) {
                uploadedFiles.cv = Array.from(files);
                updateUploadStatus();
            }
        }

        function updateUploadStatus() {
            const processBtn = document.getElementById('process-btn');
            if (uploadedFiles.jd && uploadedFiles.cv.length > 0) {
                processBtn.disabled = false;
                processBtn.style.opacity = '1';
            }
        }

        // Process CV screening
        async function processScreening() {
            const processBtn = document.getElementById('process-btn');
            const resultsContainer = document.getElementById('results-container');
            
            processBtn.innerHTML = '<span class="loading"></span> Processing...';
            processBtn.disabled = true;
            
            resultsContainer.innerHTML = `
                <div style="text-align: center; padding: 2rem;">
                    <div class="loading" style="margin: 0 auto 1rem;"></div>
                    <p>AI is analyzing CVs...</p>
                </div>
            `;

            try {
                const formData = new FormData();
                formData.append('jd_file', uploadedFiles.jd);
                
                uploadedFiles.cv.forEach(file => {
                    formData.append('cv_files', file);
                });

                const response = await fetch(`${API_BASE}/api/screen`, {
                    method: 'POST',
                    body: formData
                });

                if (response.ok) {
                    const result = await response.json();
                    displayResults(result.candidates);
                } else {
                    throw new Error('Screening failed');
                }
            } catch (error) {
                resultsContainer.innerHTML = `
                    <div style="color: #ef4444; text-align: center; padding: 2rem;">
                        <p>Demo mode: Showing sample results</p>
                    </div>
                `;
                // Show demo results
                showDemoResults();
            }
            
            processBtn.innerHTML = '✅ Analysis Complete';
        }

        function displayResults(candidates) {
            const resultsContainer = document.getElementById('results-container');
            
            if (!candidates || candidates.length === 0) {
                showDemoResults();
                return;
            }

            const resultsHTML = candidates.map(candidate => `
                <div class="candidate-result">
                    <div>
                        <h4>${candidate.candidate_name || 'Unknown'}</h4>
                        <p style="color: var(--text-secondary); font-size: 0.9rem;">
                            ${candidate.fit_score}% match
                        </p>
                    </div>
                    <div class="score">${candidate.fit_score}%</div>
                </div>
            `).join('');

            resultsContainer.innerHTML = resultsHTML;
        }

        function showDemoResults() {
            const resultsContainer = document.getElementById('results-container');
            resultsContainer.innerHTML = `
                <div class="candidate-result">
                    <div>
                        <h4>Sarah Chen</h4>
                        <p style="color: var(--text-secondary); font-size: 0.9rem;">Senior Developer</p>
                    </div>
                    <div class="score">94%</div>
                </div>
                <div class="candidate-result">
                    <div>
                        <h4>Marcus Rodriguez</h4>
                        <p style="color: var(--text-secondary); font-size: 0.9rem;">Full Stack Engineer</p>
                    </div>
                    <div class="score">87%</div>
                </div>
                <div class="candidate-result">
                    <div>
                        <h4>Emily Johnson</h4>
                        <p style="color: var(--text-secondary); font-size: 0.9rem;">Frontend Engineer</p>
                    </div>
                    <div class="score">82%</div>
                </div>
                <div style="margin-top: 1rem; padding: 1rem; background: rgba(0, 102, 255, 0.1); border-radius: 8px;">
                    <p style="font-size: 0.9rem;"><strong>🤖 AI Insight:</strong> Sarah Chen shows excellent match with required skills and experience.</p>
                </div>
            `;
        }

        // Contact form submission
        async function submitContact(event) {
            event.preventDefault();
            
            const formData = new FormData(event.target);
            const data = Object.fromEntries(formData.entries());
            
            try {
                const response = await fetch(`${API_BASE}/api/contact`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });

                if (response.ok) {
                    alert(`Thank you ${data.firstName}! Your demo request has been submitted. We'll contact you within 24 hours.`);
                    event.target.reset();
                } else {
                    throw new Error('Submission failed');
                }
            } catch (error) {
                alert(`Thank you ${data.firstName}! Your demo request has been received. We'll contact you within 24 hours.`);
                event.target.reset();
            }
        }

        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            });
        });
    </script>
</body>
</html>
"""

# Routes

@app.get("/", response_class=HTMLResponse)
async def landing_page():
    """Serve the landing page"""
    return LANDING_PAGE_HTML

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Cretzo AI Platform",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.post("/api/contact")
async def submit_contact(contact: ContactSubmission):
    """Handle contact form submissions"""
    try:
        # In production, save to database and send to CRM
        logger.info(f"Contact submission from {contact.firstName} {contact.lastName} at {contact.company}")
        
        return {
            "status": "success",
            "message": "Contact submission received",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Contact submission error: {e}")
        raise HTTPException(status_code=500, detail="Submission failed")

@app.post("/api/screen")
async def screen_candidates_demo(
    jd_file: UploadFile = File(...),
    cv_files: List[UploadFile] = File(...),
    must_have_skills: Optional[str] = Form(None)
):
    """Demo CV screening endpoint"""
    try:
        screening_id = str(uuid.uuid4())
        
        # Read files (basic validation)
        jd_content = await jd_file.read()
        cv_contents = []
        
        for cv_file in cv_files:
            content = await cv_file.read()
            cv_contents.append((cv_file.filename, content))
        
        # Generate demo results
        candidates = []
        names = ["Sarah Chen", "Marcus Rodriguez", "Emily Johnson", "Alex Kim", "Jordan Smith"]
        roles = ["Senior Developer", "Full Stack Engineer", "Frontend Engineer", "Backend Developer", "DevOps Engineer"]
        scores = [94, 87, 82, 78, 71]
        
        for i, (name, role, score) in enumerate(zip(names[:len(cv_files)], roles, scores)):
            candidate = {
                "candidate_name": name,
                "filename": cv_files[i].filename,
                "role": role,
                "fit_score": score,
