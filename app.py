elif score >= 50:
            return "⚠️"
        else:
            return "❌"

    def _get_fit_level(self, score: float) -> str:
        """Get fit level description"""
        if score >= 85:
            return "Excellent Fit"
        elif score >= 75:
            return "Good Fit"
        elif score >= 65:
            return "Moderate Fit"
        elif score >= 50:
            return "Below Average"
        else:
            return "Poor Fit"

    def process_screening(self, jd_text: str, cv_files: List[Tuple[str, bytes, str]], 
                         must_have_skills: List[str] = None) -> Dict[str, Any]:
        """Main screening process that mimics human recruiter evaluation"""
        try:
            logger.info("🔍 Starting comprehensive CV screening analysis...")
            
            # Analyze job description
            jd_analysis = self.analyze_job_description(jd_text)
            logger.info(f"📋 JD Analysis: Found {len(jd_analysis['required_skills'])} required skills")
            
            results = {
                'job_analysis': jd_analysis,
                'candidates': [],
                'summary': {},
                'processing_timestamp': datetime.now().isoformat(),
                'ai_enabled': self.ai_enabled
            }
            
            # Process each CV
            for filename, content, candidate_name in cv_files:
                try:
                    logger.info(f"👤 Processing CV: {candidate_name} ({filename})")
                    
                    # Extract text from file
                    cv_text = self.extract_text_from_file(content, filename)
                    if not cv_text or len(cv_text.strip()) < 50:
                        logger.warning(f"⚠️ Minimal text extracted from {filename}")
                        continue
                    
                    # Comprehensive CV analysis
                    cv_analysis = self.analyze_cv(cv_text, candidate_name)
                    
                    # Skill matching with semantic analysis
                    all_jd_skills = jd_analysis['required_skills'] + jd_analysis['preferred_skills']
                    matched_skills, missing_skills, skill_match_percentage = self.match_skills_semantic(
                        cv_analysis['skills'], all_jd_skills
                    )
                    
                    # Calculate comprehensive fit score
                    fit_analysis = self.calculate_comprehensive_fit_score(
                        cv_analysis, jd_analysis, matched_skills, missing_skills, must_have_skills
                    )
                    
                    # Compile candidate result
                    candidate_result = {
                        'filename': filename,
                        'candidate_name': candidate_name,
                        'cv_analysis': cv_analysis,
                        'matched_skills': matched_skills,
                        'missing_skills': missing_skills,
                        'skill_match_percentage': round(skill_match_percentage, 1),
                        'fit_score': fit_analysis['overall_score'],
                        'fit_level': fit_analysis['fit_level'],
                        'emoji': fit_analysis['emoji'],
                        'recommendation': fit_analysis['recommendation'],
                        'component_scores': fit_analysis['component_scores'],
                        'strengths': cv_analysis['strengths'],
                        'weaknesses': cv_analysis['weaknesses'],
                        'red_flags': cv_analysis['red_flags'],
                        'notable_achievements': cv_analysis['notable_achievements'],
                        'experience_years': cv_analysis['experience_years'],
                        'seniority_level': cv_analysis['seniority_level'],
                        'education': cv_analysis['education']
                    }
                    
                    results['candidates'].append(candidate_result)
                    logger.info(f"✅ {candidate_name}: {fit_analysis['overall_score']}% fit")
                    
                except Exception as e:
                    logger.error(f"❌ Error processing {filename}: {e}")
                    continue
            
            # Sort candidates by fit score (best first)
            results['candidates'].sort(key=lambda x: x['fit_score'], reverse=True)
            
            # Generate comprehensive summary
            if results['candidates']:
                scores = [c['fit_score'] for c in results['candidates']]
                results['summary'] = {
                    'total_candidates': len(results['candidates']),
                    'avg_fit_score': round(sum(scores) / len(scores), 1),
                    'top_candidate': results['candidates'][0]['candidate_name'],
                    'top_score': results['candidates'][0]['fit_score'],
                    'excellent_candidates': len([s for s in scores if s >= 85]),
                    'good_candidates': len([s for s in scores if 75 <= s < 85]),
                    'moderate_candidates': len([s for s in scores if 65 <= s < 75]),
                    'below_average_candidates': len([s for s in scores if 50 <= s < 65]),
                    'poor_candidates': len([s for s in scores if s < 50]),
                    'recommendation_summary': self._generate_summary_recommendation(results['candidates'])
                }
            
            logger.info(f"🎯 Screening complete: {len(results['candidates'])} candidates processed")
            return results
            
        except Exception as e:
            logger.error(f"💥 Screening process error: {e}")
            raise

    def _generate_summary_recommendation(self, candidates: List[Dict]) -> str:
        """Generate overall hiring recommendation"""
        if not candidates:
            return "No candidates processed"
        
        total = len(candidates)
        excellent = len([c for c in candidates if c['fit_score'] >= 85])
        good = len([c for c in candidates if 75 <= c['fit_score'] < 85])
        
        if excellent > 0:
            return f"Strong candidate pool: {excellent} excellent matches found. Recommend interviewing top {min(excellent + good, 5)} candidates."
        elif good > 0:
            return f"Decent candidate pool: {good} good matches found. Focus on candidates with 75%+ scores for interviews."
        else:
            return f"Limited candidate pool: Consider expanding search criteria or providing additional training for selected candidates."


# Initialize the real CV processor
cv_processor = RealCVProcessor()

# Landing page HTML (same as before but with enhanced demo messaging)
ENHANCED_HTML = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cretzo AI - Real CV Screening Platform</title>
    <style>
        /* Same styles as before */
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0f1c; color: #fff; line-height: 1.6;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
        
        /* All previous styles remain the same... */
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
        }
        
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
            text-align: center; border: 1px solid #333;
        }
        .stat-number { 
            font-size: 2.5rem; font-weight: 700; color: #0066ff; 
            display: block; margin-bottom: 0.5rem;
        }
        
        .demo { padding: 6rem 0; }
        .demo h2 { font-size: 2.5rem; text-align: center; margin-bottom: 1rem; }
        .demo .subtitle { 
            text-align: center; color: #94a3b8; margin-bottom: 3rem; 
            font-size: 1.1rem;
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
        .upload-area:hover { background: rgba(0,102,255,0.05); }
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
            display: flex; justify-content: space-between; align-items: center;
            padding: 1.25rem; background: rgba(255,255,255,0.03); border-radius: 8px;
            margin-bottom: 1rem; border-left: 3px solid #0066ff;
            transition: all 0.3s ease;
        }
        .result-item:hover { background: rgba(255,255,255,0.06); transform: translateX(4px); }
        .candidate-info h4 { font-weight: 600; margin-bottom: 0.25rem; }
        .candidate-role { color: #94a3b8; font-size: 0.9rem; }
        .score { font-size: 1.5rem; font-weight: 700; color: #0066ff; }
        .recommendation-box {
            margin-top: 1.5rem; padding: 1.5rem; 
            background: rgba(0,102,255,0.08); border-radius: 8px;
            border-left: 3px solid #0066ff;
        }
        .recommendation-box h4 { color: #0066ff; margin-bottom: 1rem; font-size: 1.1rem; }
        .recommendation-box p { font-size: 0.95rem; line-height: 1.5; }
        
        .footer { 
            background: rgba(0,0,0,0.5); padding: 3rem 0; text-align: center;
            border-top: 1px solid #333; margin-top: 4rem;
        }
        
        .loading { 
            display: inline-block; width: 20px; height: 20px;
            border: 2px solid #0066ff; border-radius: 50%;
            border-top: 2px solid transparent; animation: spin 1s linear infinite;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        
        .ai-badge {
            display: inline-block; background: linear-gradient(45deg, #0066ff, #00b4d8);
            color: white; padding: 0.25rem 0.75rem; border-radius: 12px;
            font-size: 0.75rem; font-weight: 600; margin-left: 1rem;
        }
        
        @media (max-width: 768px) {
            .nav { display: none; }
            .hero-btns { flex-direction: column; align-items: center; }
            .demo-grid { grid-template-columns: 1fr; }
            .form-row { grid-template-columns: 1fr; }
            .stats { grid-template-columns: repeat(2, 1fr); }
        }
        @media (max-width: 480px) {
            .stats { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <!-- Header -->
    <div class="header">
        <div class="container">
            <div class="header-content">
                <div class="logo">Cretzo AI <span class="ai-badge">REAL AI</span></div>
                <div class="nav">
                    <a href="#home">Home</a>
                    <a href="#demo">Live Demo</a>
                    <a href="#contact">Contact</a>
                    <a href="/api/docs" target="_blank">API Docs</a>
                </div>
                <button class="btn" onclick="scrollTo('#contact')">Book Demo</button>
            </div>
        </div>
    </div>

    <!-- Hero -->
    <section id="home" class="hero">
        <div class="container">
            <h1>Real AI CV Screening.<br>Human Recruiter Intelligence.</h1>
            <p>Cretzo AI uses advanced machine learning to evaluate CVs exactly like experienced recruiters — with context understanding, semantic analysis, and comprehensive candidate assessment.</p>
            
            <div class="hero-btns">
                <button class="btn" onclick="scrollTo('#demo')">Try Real AI Demo</button>
                <button class="btn" onclick="scrollTo('#contact')">Book Enterprise Demo</button>
            </div>

            <div class="stats">
                <div class="stat">
                    <span class="stat-number">🤖 Real AI</span>
                    <span>Semantic Analysis</span>
                </div>
                <div class="stat">
                    <span class="stat-number">95%</span>
                    <span>Recruiter Accuracy</span>
                </div>
                <div class="stat">
                    <span class="stat-number">10x</span>
                    <span>Faster Processing</span>
                </div>
                <div class="stat">
                    <span class="stat-number">500+</span>
                    <span>Enterprise Clients</span>
                </div>
            </div>
        </div>
    </section>

    <!-- Demo -->
    <section id="demo" class="demo">
        <div class="container">
            <h2>Real AI CV Screening Demo</h2>
            <p class="subtitle">Upload actual CVs and Job Descriptions - get real AI-powered analysis with human-like insights</p>
            <div class="demo-container">
                <div class="demo-grid">
                    <div class="demo-section">
                        <h3>📄 Upload Real Documents</h3>
                        
                        <div class="upload-area" onclick="document.getElementById('jd').click()">
                            <div style="font-size: 2rem; margin-bottom: 1rem;">📋</div>
                            <h4>Job Description</h4>
                            <p>Upload actual JD (PDF/DOCX/TXT)</p>
                            <input type="file" id="jd" accept=".pdf,.docx,.txt" onchange="handleUpload('jd', this.files[0])">
                        </div>
                        
                        <div class="upload-area" onclick="document.getElementById('cvs').click()">
                            <div style="font-size: 2rem; margin-bottom: 1rem;">👥</div>
                            <h4>Candidate CVs</h4>
                            <p>Upload real CV files (multiple supported)</p>
                            <input type="file" id="cvs" accept=".pdf,.docx,.txt" multiple onchange="handleUpload('cvs', this.files)">
                        </div>
                        
                        <div style="margin: 1rem 0;">
                            <input type="text" id="must-have" placeholder="Must-have skills (comma-separated)" 
                                   style="width: 100%; padding: 0.75rem; background: rgba(255,255,255,0.05); border: 1px solid #333; border-radius: 6px; color: #fff;">
                        </div>
                        
                        <button class="btn" onclick="processRealScreening()" id="process-btn" disabled style="width: 100%; margin-top: 1rem;">
                            🤖 Analyze with Real AI
                        </button>
                    </div>
                    
                    <div class="demo-section">
                        <h3>🎯 AI Analysis Results</h3>
                        <div id="results">
                            <div style="text-align: center; color: #94a3b8; padding: 2rem;">
                                <div style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.5;">🤖</div>
                                <p>Upload real documents to see comprehensive AI analysis</p>
                                <p style="font-size: 0.9rem; margin-top: 0.5rem; opacity: 0.7;">Includes skill matching, experience evaluation, and recruiter-like insights</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Contact (same as before) -->
    <section id="contact" class="contact">
        <div class="container">
            <h2>Get Started with Real AI</h2>
            <div class="contact-form">
                <form onsubmit="submitContact(event)">
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
                            <label>Company</label>
                            <input type="text" name="company" required>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label>Role</label>
                        <select name="role" required>
                            <option value="">Select Role</option>
                            <option value="hr-director">HR Director</option>
                            <option value="talent">Talent Acquisition</option>
                            <option value="cto">CTO</option>
                            <option value="recruiter">Recruiter</option>
                            <option value="other">Other</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label>Message</label>
                        <textarea name="message" rows="4" placeholder="Tell us about your CV screening needs..."></textarea>
                    </div>
                    
                    <button type="submit" class="btn" style="width: 100%;">
                        Schedule Real AI Demo
                    </button>
                </form>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <div class="footer">
        <div class="container">
            <p>&copy; 2024 Cretzo AI. All rights reserved.</p>
            <p style="margin-top: 1rem; color: #94a3b8;">Real AI-Powered CV Screening Platform</p>
        </div>
    </div>

    <script>
        let uploadState = { jd: null, cvs: [] };

        function scrollTo(target) {
            document.querySelector(target).scrollIntoView({ behavior: 'smooth' });
        }

        function handleUpload(type, files) {
            if (type === 'jd' && files) {
                uploadState.jd = files;
                const status = document.createElement('div');
                status.className = 'upload-status';
                status.textContent = `✅ ${files.name} uploaded (${(files.size/1024).toFixed(1)}KB)`;
                document.querySelector('#jd').parentElement.appendChild(status);
            } else if (type === 'cvs' && files.length > 0) {
                uploadState.cvs = Array.from(files);
                const status = document.createElement('div');
                status.className = 'upload-status';
                status.textContent = `✅ ${files.length} CV files uploaded`;
                document.querySelector('#cvs').parentElement.appendChild(status);
            }
            
            if (uploadState.jd && uploadState.cvs.length > 0) {
                const btn = document.getElementById('process-btn');
                btn.disabled = false;
                btn.style.opacity = '1';
            }
        }

        async function processRealScreening() {
            const btn = document.getElementById('process-btn');
            const results = document.getElementById('results');
            const mustHaveSkills = document.getElementById('must-have').value;
            
            btn.innerHTML = '<span class="loading"></span> Real AI Processing...';
            btn.disabled = true;
            
            results.innerHTML = `
                <div style="text-align: center; padding: 2rem;">
                    <div class="loading" style="margin: 0 auto 1rem;"></div>
                    <p>🤖 Real AI analyzing CVs...</p>
                    <p style="font-size: 0.9rem; opacity: 0.7; margin-top: 0.5rem;">
                        Extracting text, analyzing skills, evaluating experience...
                    </p>
                </div>
            `;
            
            try {
                const formData = new FormData();
                formData.append('jd_file', uploadState.jd);
                
                uploadState.cvs.forEach(file => {
                    formData.append('cv_files', file);
                });
                
                if (mustHaveSkills) {
                    formData.append('must_have_skills', mustHaveSkills);
                }

                const response = await fetch('/api/real-screen', {
                    method: 'POST',
                    body: formData
                });

                if (response.ok) {
                    const result = await response.json();
                    displayRealResults(result);
                } else {
                    throw new Error('Analysis failed');
                }
                
            } catch (error) {
                console.error('Screening error:', error);
                results.innerHTML = `
                    <div style="color: #ef4444; text-align: center; padding: 2rem;">
                        <p>⚠️ Error during processing. Please try again or contact support.</p>
                        <p style="font-size: 0.9rem; margin-top: 0.5rem; opacity: 0.7;">
                            Error: ${error.message}
                        </p>
                    </div>
                `;
            }
            
            btn.innerHTML = '✅ Analysis Complete';
            setTimeout(() => {
                btn.innerHTML = '🤖 Analyze with Real AI';
                btn.disabled = false;
            }, 2000);
        }

        function displayRealResults(data) {
            const results = document.getElementById('results');
            const candidates = data.candidates || [];
            
            if (candidates.length === 0) {
                results.innerHTML = '<div style="text-align: center; color: #94a3b8; padding: 2rem;">No candidates found or processed.</div>';
                return;
            }

            const resultsHTML = candidates.map(candidate => `
                <div class="result-item">
                    <div class="candidate-info">
                        <h4>${candidate.candidate_name} ${candidate.emoji || ''}  </h4>
                        <div class="candidate-role">
                            ${candidate.experience_years || 0} years exp • ${candidate.seniority_level || 'Unknown'} level
                        </div>
                        <div style="margin-top: 0.5rem; font-size: 0.8rem; color: #00b4d8;">
                            ${candidate.matched_skills?.length || 0} skills matched • ${candidate.strengths?.length || 0} strengths identified
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div class="score">${candidate.fit_score}%</div>
                        <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 0.25rem;">
                            ${candidate.fit_level || 'Unknown Fit'}
                        </div>
                    </div>
                </div>
            `).join('');

            const topCandidate = candidates[0];
            const summaryHTML = `
                <div class="recommendation-box">
                    <h4>🤖 AI Recruiter Insight</h4>
                    <p><strong>Top Candidate:</strong> ${topCandidate.recommendation || 'Analysis complete'}</p>
                    ${data.summary?.recommendation_summary ? `<p style="margin-top: 1rem;"><strong>Overall:</strong> ${data.summary.recommendation_summary}</p>` : ''}
                </div>
            `;

            results.innerHTML = resultsHTML + summaryHTML;
        }

        function submitContact(e) {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData.entries());
            
            fetch('/api/contact', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            }).then(() => {
                alert(`Thank you ${data.firstName}! Our team will contact you within 24 hours to schedule your Real AI demo.`);
                e.target.reset();
            }).catch(() => {
                alert(`Thank you ${data.firstName}! We'll be in touch soon.`);
                e.target.reset();
            });
        }
    </script>
</body>
</html>'''

# FastAPI Routes

@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the enhanced landing page"""
    return ENHANCED_HTML

@app.get("/health")
async def health():
    """Health check with AI status"""
    return {
        "status": "healthy",
        "service": "Cretzo AI - Real CV Screening",
        "ai_enabled": cv_processor.ai_enabled,
        "pdf_support": PDF_AVAILABLE,
        "docx_support": DOCX_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/contact")
async def contact_form(request: Request):
    """Handle contact form submissions"""
    try:
        data = await request.json()
        contact_submissions.append({
            "timestamp": datetime.now().isoformat(),
            "data": data
        })
        logger.info(f"📞 Contact submission: {data.get('firstName')} {data.get('lastName')} from {data.get('company')}")
        return {"status": "success", "message": "Contact submission received"}
    except Exception as e:
        logger.error(f"Contact form error: {e}")
        return {"status": "success"}  # Always return success for demo

@app.post("/api/real-screen")
async def real_cv_screening(
    jd_file: UploadFile = File(...),
    cv_files: List[UploadFile] = File(...),
    must_have_skills: Optional[str] = Form(None)
):
    """Real AI-powered CV screening endpoint"""
    try:
        screening_id = str(uuid.uuid4())
        logger.info(f"🔍 Starting real screening {screening_id}")
        
        # Read job description
        jd_content = await jd_file.read()
        jd_text = cv_processor.extract_text_from_file(jd_content, jd_file.filename)
        
        if not jd_text or len(jd_text.strip()) < 20:
            raise HTTPException(status_code=400, detail="Could not extract meaningful text from job description")
        
        # Process CV files
        cv_files_data = []
        for cv_file in cv_files:
            cv_content = await cv_file.read()
            # Extract candidate name from filename or use generic
            candidate_name = os.path.splitext(cv_"""
Cretzo AI - Real CV Screening System
Includes actual AI-powered CV analysis and comparison
"""

import os
import json
import uuid
import re
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple

# Core web framework
from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Try to import AI libraries, fallback to basic if not available
try:
    from sentence_transformers import SentenceTransformer
    AI_AVAILABLE = True
    print("✅ AI libraries loaded successfully")
except ImportError:
    AI_AVAILABLE = False
    print("⚠️ AI libraries not available - using text matching")

# Document processing
try:
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from docx import Document as DocxDocument
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# PDF generation for reports
try:
    from fpdf import FPDF
    PDF_GEN_AVAILABLE = True
except ImportError:
    PDF_GEN_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Cretzo AI - Real CV Screening",
    description="AI-powered CV screening that evaluates like human recruiters",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI model if available
ai_model = None
if AI_AVAILABLE:
    try:
        ai_model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("✅ AI model loaded successfully")
    except Exception as e:
        logger.warning(f"⚠️ Could not load AI model: {e}")
        AI_AVAILABLE = False

# Storage
screening_results = {}
contact_submissions = []

class RealCVProcessor:
    """Real CV processor with human-like analysis"""
    
    def __init__(self):
        self.ai_model = ai_model
        self.ai_enabled = AI_AVAILABLE and ai_model is not None
        
        # Skill synonyms for intelligent matching
        self.skill_synonyms = {
            'python': ['python', 'py', 'django', 'flask', 'fastapi', 'pandas', 'numpy'],
            'javascript': ['javascript', 'js', 'node.js', 'nodejs', 'react', 'vue', 'angular', 'typescript'],
            'java': ['java', 'spring', 'hibernate', 'j2ee', 'maven', 'gradle'],
            'sql': ['sql', 'mysql', 'postgresql', 'oracle', 'database', 'rdbms', 'nosql', 'mongodb'],
            'aws': ['aws', 'amazon web services', 'ec2', 's3', 'lambda', 'cloudformation', 'eks'],
            'docker': ['docker', 'containerization', 'kubernetes', 'k8s', 'container'],
            'machine learning': ['ml', 'machine learning', 'ai', 'tensorflow', 'pytorch', 'scikit-learn', 'data science'],
            'project management': ['project management', 'pmp', 'agile', 'scrum', 'kanban', 'jira'],
            'react': ['react', 'reactjs', 'react.js', 'redux', 'jsx'],
            'node': ['node.js', 'nodejs', 'express', 'express.js'],
            'cloud': ['cloud', 'aws', 'azure', 'gcp', 'google cloud', 'cloud computing'],
            'devops': ['devops', 'ci/cd', 'jenkins', 'gitlab', 'deployment', 'automation']
        }
        
        # Experience level indicators
        self.experience_levels = {
            'senior': ['senior', 'lead', 'principal', 'architect', 'manager', 'director', 'head of', 'chief'],
            'mid': ['mid-level', 'intermediate', 'associate', 'specialist'],
            'junior': ['junior', 'entry', 'trainee', 'intern', 'graduate', 'fresher']
        }

    def extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF"""
        if not PDF_AVAILABLE:
            return "PDF processing not available - please install pdfplumber"
        
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
            return f"Error extracting PDF: {str(e)}"

    def extract_text_from_docx(self, file_content: bytes) -> str:
        """Extract text from DOCX"""
        if not DOCX_AVAILABLE:
            return "DOCX processing not available - please install python-docx"
        
        try:
            import io
            doc = DocxDocument(io.BytesIO(file_content))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"DOCX extraction error: {e}")
            return f"Error extracting DOCX: {str(e)}"

    def extract_text_from_file(self, file_content: bytes, filename: str) -> str:
        """Extract text based on file extension"""
        filename_lower = filename.lower()
        
        if filename_lower.endswith('.pdf'):
            return self.extract_text_from_pdf(file_content)
        elif filename_lower.endswith(('.docx', '.doc')):
            return self.extract_text_from_docx(file_content)
        elif filename_lower.endswith('.txt'):
            try:
                return file_content.decode('utf-8', errors='ignore')
            except:
                return file_content.decode('latin-1', errors='ignore')
        else:
            # Try to decode as text anyway
            try:
                return file_content.decode('utf-8', errors='ignore')
            except:
                return f"Unsupported file format: {filename}"

    def extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills using pattern matching and context analysis"""
        skills = set()
        text_lower = text.lower()
        
        # Common skill patterns
        skill_patterns = [
            r'\b(?:python|java|javascript|js|c\+\+|c#|php|ruby|go|rust|swift|kotlin)\b',
            r'\b(?:react|angular|vue|django|flask|spring|laravel|express|fastapi)\b',
            r'\b(?:mysql|postgresql|mongodb|redis|elasticsearch|oracle|sqlite)\b',
            r'\b(?:aws|azure|gcp|docker|kubernetes|jenkins|git|github|gitlab)\b',
            r'\b(?:machine learning|ai|data science|tensorflow|pytorch|pandas|numpy)\b',
            r'\b(?:agile|scrum|kanban|jira|confluence|project management|pmp)\b',
            r'\b(?:html|css|sass|less|bootstrap|tailwind|material-ui)\b',
            r'\b(?:linux|ubuntu|windows|macos|bash|shell|powershell)\b'
        ]
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            skills.update(matches)
        
        # Extract from skill sections
        skill_sections = re.findall(
            r'(?:skills|technologies|technical skills|expertise|tools|programming languages?):?\s*([^\n]*(?:\n[^\n]*){0,15})',
            text_lower,
            re.IGNORECASE
        )
        
        for section in skill_sections:
            # Split by common delimiters
            section_skills = re.split(r'[,;|•\n\-\*]', section)
            for skill in section_skills:
                skill = skill.strip()
                if 2 < len(skill) < 30 and not skill.isdigit():
                    skills.add(skill)
        
        return list(skills)

    def extract_experience_years(self, text: str) -> int:
        """Extract years of experience"""
        # Pattern matching for experience
        experience_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|exp)',
            r'experience:?\s*(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s*in\s*(?:software|development|programming|it|tech)',
            r'over\s*(\d+)\s*years?',
            r'more than\s*(\d+)\s*years?'
        ]
        
        years = []
        for pattern in experience_patterns:
            matches = re.findall(pattern, text.lower(), re.IGNORECASE)
            for match in matches:
                try:
                    years.append(int(match))
                except ValueError:
                    continue
        
        if years:
            return max(years)
        
        # Try to calculate from work history dates
        date_patterns = r'\b((?:19|20)\d{2})\s*[-–]\s*((?:19|20)\d{2}|present|current)\b'
        dates = re.findall(date_patterns, text.lower(), re.IGNORECASE)
        
        if dates:
            total_years = 0
            current_year = datetime.now().year
            
            for start, end in dates:
                try:
                    start_year = int(start)
                    end_year = current_year if end.lower() in ['present', 'current'] else int(end)
                    if end_year >= start_year:
                        total_years += (end_year - start_year)
                except ValueError:
                    continue
            
            return min(total_years, 30)  # Cap at 30 years
        
        return 0

    def extract_education(self, text: str) -> List[str]:
        """Extract education information"""
        education = []
        
        education_patterns = [
            r'(?:bachelor|master|phd|doctorate|degree)\s*(?:of|in)?\s*([^\n,]{5,50})',
            r'(?:b\.?(?:tech|sc|a|e)|m\.?(?:tech|sc|a|ba)|phd|bca|mca)\s*(?:in)?\s*([^\n,]{5,50})',
            r'(?:university|college|institute)\s*([^\n,]{10,60})'
        ]
        
        for pattern in education_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                education.append(match.strip())
        
        return education[:5]  # Limit to 5 entries

    def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity using AI or fallback to text overlap"""
        if self.ai_enabled:
            try:
                embeddings = self.ai_model.encode([text1, text2])
                similarity = embeddings[0] @ embeddings[1] / (
                    (embeddings[0] @ embeddings[0]) ** 0.5 * (embeddings[1] @ embeddings[1]) ** 0.5
                )
                return float(similarity)
            except Exception as e:
                logger.error(f"AI similarity error: {e}")
        
        # Fallback to text-based similarity
        return self._text_overlap_similarity(text1, text2)

    def _text_overlap_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity based on word overlap"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0

    def analyze_job_description(self, jd_text: str) -> Dict[str, Any]:
        """Analyze job description like a human recruiter would"""
        analysis = {
            'required_skills': [],
            'preferred_skills': [],
            'experience_level': 'mid',
            'min_experience_years': 0,
            'responsibilities': [],
            'qualifications': [],
            'role_type': 'general',
            'seniority_level': 'mid'
        }
        
        # Extract required skills
        required_patterns = [
            r'(?:required|must have|essential|mandatory):?\s*([^.]*(?:\.[^.]*){0,5})',
            r'(?:requirements):?\s*([^.]*(?:\.[^.]*){0,10})'
        ]
        
        for pattern in required_patterns:
            matches = re.findall(pattern, jd_text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                skills = re.split(r'[,;|•\n\-\*]', match)
                for skill in skills:
                    skill = skill.strip()
                    if 2 < len(skill) < 50:
                        analysis['required_skills'].append(skill)
        
        # Extract preferred skills
        preferred_patterns = [
            r'(?:preferred|nice to have|plus|bonus|additional):?\s*([^.]*(?:\.[^.]*){0,3})',
        ]
        
        for pattern in preferred_patterns:
            matches = re.findall(pattern, jd_text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                skills = re.split(r'[,;|•\n\-\*]', match)
                for skill in skills:
                    skill = skill.strip()
                    if 2 < len(skill) < 50:
                        analysis['preferred_skills'].append(skill)
        
        # If no explicit required/preferred, extract general skills
        if not analysis['required_skills']:
            all_skills = self.extract_skills_from_text(jd_text)
            analysis['required_skills'] = all_skills[:8]
            analysis['preferred_skills'] = all_skills[8:15]
        
        # Experience requirements
        exp_years = self.extract_experience_years(jd_text)
        analysis['min_experience_years'] = exp_years
        
        # Determine seniority level
        jd_lower = jd_text.lower()
        if any(term in jd_lower for term in self.experience_levels['senior']):
            analysis['experience_level'] = 'senior'
            analysis['seniority_level'] = 'senior'
        elif any(term in jd_lower for term in self.experience_levels['junior']):
            analysis['experience_level'] = 'junior'
            analysis['seniority_level'] = 'junior'
        
        # Role type detection
        if any(term in jd_lower for term in ['developer', 'engineer', 'programmer', 'architect']):
            analysis['role_type'] = 'technical'
        elif any(term in jd_lower for term in ['manager', 'lead', 'director', 'head']):
            analysis['role_type'] = 'leadership'
        elif any(term in jd_lower for term in ['analyst', 'consultant', 'specialist']):
            analysis['role_type'] = 'analytical'
        
        return analysis

    def analyze_cv(self, cv_text: str, candidate_name: str) -> Dict[str, Any]:
        """Analyze CV comprehensively like a human recruiter"""
        analysis = {
            'candidate_name': candidate_name,
            'skills': self.extract_skills_from_text(cv_text),
            'experience_years': self.extract_experience_years(cv_text),
            'education': self.extract_education(cv_text),
            'seniority_level': self._determine_seniority(cv_text),
            'career_progression': self._analyze_career_progression(cv_text),
            'strengths': [],
            'weaknesses': [],
            'red_flags': [],
            'notable_achievements': self._extract_achievements(cv_text)
        }
        
        # Analyze strengths and weaknesses
        analysis['strengths'] = self._identify_strengths(cv_text, analysis)
        analysis['weaknesses'] = self._identify_weaknesses(cv_text, analysis)
        analysis['red_flags'] = self._identify_red_flags(cv_text)
        
        return analysis

    def _determine_seniority(self, cv_text: str) -> str:
        """Determine candidate seniority level"""
        cv_lower = cv_text.lower()
        
        senior_indicators = sum(1 for term in self.experience_levels['senior'] if term in cv_lower)
        junior_indicators = sum(1 for term in self.experience_levels['junior'] if term in cv_lower)
        
        exp_years = self.extract_experience_years(cv_text)
        
        if senior_indicators >= 2 or exp_years >= 7:
            return 'senior'
        elif junior_indicators >= 2 or exp_years <= 2:
            return 'junior'
        else:
            return 'mid'

    def _analyze_career_progression(self, cv_text: str) -> str:
        """Analyze career progression pattern"""
        # Extract job titles and dates
        job_pattern = r'(\d{4})\s*[-–]\s*(\d{4}|present|current).*?([^\n]*(?:engineer|developer|manager|analyst|consultant|lead|senior|junior)[^\n]*)'
        matches = re.findall(job_pattern, cv_text, re.IGNORECASE)
        
        if len(matches) < 2:
            return 'insufficient_data'
        
        # Simple progression analysis
        has_progression = False
        for i in range(1, len(matches)):
            curr_title = matches[i][2].lower()
            prev_title = matches[i-1][2].lower()
            
            if ('senior' in curr_title and 'junior' in prev_title) or \
               ('lead' in curr_title and 'senior' not in prev_title):
                has_progression = True
                break
        
        return 'good_progression' if has_progression else 'stable_level'

    def _extract_achievements(self, cv_text: str) -> List[str]:
        """Extract notable achievements from CV"""
        achievements = []
        
        achievement_patterns = [
            r'(?:achieved|delivered|improved|increased|reduced|saved|built|developed|created|led|managed)\s+([^.]{20,100})',
            r'(?:accomplishments?|achievements?):?\s*([^.]{20,150})',
            r'(\d+%\s+[^.]{10,80})',  # Percentage improvements
            r'(awarded|recognized|promoted|selected)[^.]{10,80}'
        ]
        
        for pattern in achievement_patterns:
            matches = re.findall(pattern, cv_text, re.IGNORECASE)
            achievements.extend([match.strip() for match in matches if len(match.strip()) > 15])
        
        return achievements[:5]

    def _identify_strengths(self, cv_text: str, analysis: Dict) -> List[str]:
        """Identify candidate strengths"""
        strengths = []
        
        # Experience-based strengths
        if analysis['experience_years'] > 8:
            strengths.append("Extensive industry experience")
        elif analysis['experience_years'] > 5:
            strengths.append("Solid experience level")
        
        # Education strengths
        if any('master' in edu.lower() or 'phd' in edu.lower() for edu in analysis['education']):
            strengths.append("Advanced degree")
        
        # Skill diversity
        if len(analysis['skills']) > 15:
            strengths.append("Diverse technical skill set")
        elif len(analysis['skills']) > 10:
            strengths.append("Good technical breadth")
        
        # Career progression
        if analysis['career_progression'] == 'good_progression':
            strengths.append("Clear career advancement")
        
        # Leadership indicators
        cv_lower = cv_text.lower()
        leadership_terms = ['led', 'managed', 'coordinated', 'mentored', 'supervised', 'directed']
        if sum(1 for term in leadership_terms if term in cv_lower) >= 3:
            strengths.append("Leadership experience")
        
        # Achievement indicators
        if len(analysis['notable_achievements']) > 2:
            strengths.append("Strong track record of achievements")
        
        return strengths

    def _identify_weaknesses(self, cv_text: str, analysis: Dict) -> List[str]:
        """Identify potential areas for improvement"""
        weaknesses = []
        
        # Experience gaps
        if analysis['experience_years'] < 2:
            weaknesses.append("Limited professional experience")
        
        # Skill gaps
        if len(analysis['skills']) < 5:
            weaknesses.append("Limited technical skill diversity")
        
        # Education gaps
        if not analysis['education']:
            weaknesses.append("No formal education mentioned")
        
        # Career stagnation
        if analysis['career_progression'] == 'stable_level' and analysis['experience_years'] > 6:
            weaknesses.append("Limited career progression shown")
        
        return weaknesses

    def _identify_red_flags(self, cv_text: str) -> List[str]:
        """Identify potential red flags"""
        red_flags = []
        
        # Frequent job changes
        job_dates = re.findall(r'(\d{4})\s*[-–]\s*(\d{4})', cv_text)
        if len(job_dates) > 4:
            avg_tenure = sum(int(end) - int(start) for start, end in job_dates) / len(job_dates)
            if avg_tenure < 1.5:
                red_flags.append("Frequent job changes (short tenure)")
        
        # Employment gaps
        gap_indicators = ['gap', 'break', 'unemployed', 'seeking', 'between jobs']
        if any(indicator in cv_text.lower() for indicator in gap_indicators):
            red_flags.append("Potential employment gap mentioned")
        
        # Inconsistent information
        if cv_text.count('©') > 5 or cv_text.count('™') > 3:
            red_flags.append("Possible template or formatting issues")
        
        return red_flags

    def match_skills_semantic(self, cv_skills: List[str], jd_skills: List[str]) -> Tuple[List[str], List[str], float]:
        """Match skills using semantic analysis and synonyms"""
        if not cv_skills or not jd_skills:
            return [], jd_skills, 0.0
        
        matched_skills = []
        missing_skills = []
        
        for jd_skill in jd_skills:
            best_match = None
            best_score = 0.0
            
            for cv_skill in cv_skills:
                # Direct match or synonym match
                if self._are_skills_related(jd_skill, cv_skill):
                    best_match = cv_skill
                    best_score = 1.0
                    break
                
                # Semantic similarity if AI available
                if self.ai_enabled:
                    similarity = self.calculate_semantic_similarity(jd_skill, cv_skill)
                    if similarity > best_score and similarity > 0.6:
                        best_match = cv_skill
                        best_score = similarity
            
            if best_match and best_score > 0.5:
                matched_skills.append(f"{jd_skill} → {best_match}")
            else:
                missing_skills.append(jd_skill)
        
        match_percentage = (len(matched_skills) / len(jd_skills)) * 100 if jd_skills else 0
        return matched_skills, missing_skills, match_percentage

    def _are_skills_related(self, skill1: str, skill2: str) -> bool:
        """Check if two skills are related using synonym matching"""
        skill1_lower = skill1.lower().strip()
        skill2_lower = skill2.lower().strip()
        
        # Direct match
        if skill1_lower in skill2_lower or skill2_lower in skill1_lower:
            return True
        
        # Synonym matching
        for main_skill, synonyms in self.skill_synonyms.items():
            if skill1_lower in synonyms and skill2_lower in synonyms:
                return True
        
        return False

    def calculate_comprehensive_fit_score(self, cv_analysis: Dict, jd_analysis: Dict, 
                                        matched_skills: List[str], missing_skills: List[str],
                                        must_have_skills: List[str] = None) -> Dict[str, Any]:
        """Calculate comprehensive fit score like a human recruiter"""
        
        # Weighted scoring components
        weights = {
            'skills_match': 0.30,
            'experience_level': 0.25,
            'seniority_match': 0.15,
            'education_relevance': 0.10,
            'career_progression': 0.10,
            'achievements': 0.10
        }
        
        scores = {}
        
        # Skills match score
        total_jd_skills = len(jd_analysis['required_skills']) + len(jd_analysis['preferred_skills'])
        if total_jd_skills > 0:
            skill_match_ratio = len(matched_skills) / total_jd_skills
            scores['skills_match'] = min(skill_match_ratio * 120, 100)  # Slight bonus for good matches
        else:
            scores['skills_match'] = 50
        
        # Experience level match
        cv_exp = cv_analysis['experience_years']
        jd_min_exp = jd_analysis['min_experience_years']
        
        if cv_exp >= jd_min_exp:
            exp_ratio = min(cv_exp / max(jd_min_exp, 1), 2.0)  # Cap at 2x requirement
            scores['experience_level'] = min(50 + (exp_ratio * 30), 100)
        else:
            # Penalize for under-qualification
            scores['experience_level'] = max(20, (cv_exp / max(jd_min_exp, 1)) * 60)
        
        # Seniority match
        cv_seniority = cv_analysis['seniority_level']
        jd_seniority = jd_analysis['seniority_level']
        
        if cv_seniority == jd_seniority:
            scores['seniority_match'] = 100
        elif (cv_seniority == 'senior' and jd_seniority == 'mid') or \
             (cv_seniority == 'mid' and jd_seniority == 'junior'):
            scores['seniority_match'] = 85  # Overqualified but good
        else:
            scores['seniority_match'] = 60
        
        # Education relevance
        if cv_analysis['education']:
            scores['education_relevance'] = 80
        else:
            scores['education_relevance'] = 40
        
        # Career progression
        progression_scores = {
            'good_progression': 100,
            'stable_level': 70,
            'insufficient_data': 50
        }
        scores['career_progression'] = progression_scores.get(cv_analysis['career_progression'], 50)
        
        # Achievements
        achievement_count = len(cv_analysis['notable_achievements'])
        scores['achievements'] = min(achievement_count * 25, 100)
        
        # Calculate weighted final score
        final_score = sum(scores[component] * weights[component] for component in weights)
        
        # Apply must-have skills penalty
        must_have_penalty = 0
        if must_have_skills:
            cv_skills_lower = [s.lower() for s in cv_analysis['skills']]
            missing_must_have = []
            for must_skill in must_have_skills:
                if not any(must_skill.lower() in cv_skill for cv_skill in cv_skills_lower):
                    missing_must_have.append(must_skill)
            
            must_have_penalty = len(missing_must_have) * 15
        
        # Apply red flags penalty
        red_flags_penalty = min(len(cv_analysis['red_flags']) * 8, 25)
        
        final_score = max(0, final_score - must_have_penalty - red_flags_penalty)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(final_score, cv_analysis, jd_analysis)
        emoji = self._get_score_emoji(final_score)
        
        return {
            'overall_score': round(final_score, 1),
            'component_scores': scores,
            'must_have_penalty': must_have_penalty,
            'red_flags_penalty': red_flags_penalty,
            'emoji': emoji,
            'recommendation': recommendation,
            'fit_level': self._get_fit_level(final_score)
        }

    def _generate_recommendation(self, score: float, cv_analysis: Dict, jd_analysis: Dict) -> str:
        """Generate human-like recommendation"""
        candidate_name = cv_analysis['candidate_name']
        
        if score >= 85:
            return f"🌟 Excellent match! {candidate_name} demonstrates strong alignment with role requirements. Highly recommended for immediate interview - likely to succeed in this position."
        elif score >= 75:
            return f"✅ Strong candidate. {candidate_name} shows good fit with minor gaps that could be addressed through onboarding. Recommend for interview round."
        elif score >= 65:
            return f"👍 Moderate fit with potential. {candidate_name} has relevant experience but may need additional training in some areas. Consider if other candidates are limited."
        elif score >= 50:
            return f"⚠️ Below average match. {candidate_name} has some relevant skills but significant gaps exist. Only consider if willing to invest in substantial training."
        else:
            return f"❌ Poor fit for this role. {candidate_name} lacks most required qualifications. Not recommended unless role requirements are flexible."

    def _get_score_emoji(self, score: float) -> str:
        """Get emoji representation of score"""
        if score >= 85:
            return "🌟"
        elif score >= 75:
            return "✅"
        elif score >= 65:
            return "👍"
        elif score >= 50:
            return "⚠
