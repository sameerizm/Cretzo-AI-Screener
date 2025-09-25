"""
Super Minimal Cretzo AI Platform
Uses only standard library + basic FastAPI to avoid compilation issues
"""

import os
import json
import uuid
from datetime import datetime
from typing import Optional, List

# Simple FastAPI without advanced features that cause compilation
try:
    from fastapi import FastAPI, Request, Form
    from fastapi.responses import HTMLResponse, JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    # Fallback to basic HTTP server if FastAPI fails
    FASTAPI_AVAILABLE = False

# Initialize app
if FASTAPI_AVAILABLE:
    app = FastAPI(title="Cretzo AI", description="CV Screening Platform")
    
    # Simple CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    # Basic HTTP server fallback
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import socketserver

# Simple in-memory storage
contacts = []
demo_results = []

# Ultra-minimal HTML (embedded to avoid file issues)
MINIMAL_HTML = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cretzo AI - CV Screening Platform</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0f1c; color: #fff; line-height: 1.6;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
        
        /* Header */
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
        
        /* Hero */
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
        
        /* Stats */
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
        
        /* Demo */
        .demo { padding: 6rem 0; }
        .demo h2 { font-size: 2.5rem; text-align: center; margin-bottom: 3rem; }
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
        }
        .upload-area:hover { background: rgba(0,102,255,0.05); }
        .upload-area input { display: none; }
        
        /* Contact */
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
        
        /* Results */
        .result-item { 
            display: flex; justify-content: space-between; align-items: center;
            padding: 1rem; background: rgba(255,255,255,0.03); border-radius: 6px;
            margin-bottom: 1rem; border-left: 3px solid #0066ff;
        }
        .score { font-size: 1.5rem; font-weight: 700; color: #0066ff; }
        
        /* Footer */
        .footer { 
            background: rgba(0,0,0,0.5); padding: 3rem 0; text-align: center;
            border-top: 1px solid #333; margin-top: 4rem;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .demo-grid, .form-row { grid-template-columns: 1fr; }
            .hero-btns { flex-direction: column; align-items: center; }
            .stats { grid-template-columns: repeat(2, 1fr); }
            .nav { display: none; }
        }
        @media (max-width: 480px) {
            .stats { grid-template-columns: 1fr; }
        }
        
        /* Loading */
        .loading { 
            display: inline-block; width: 20px; height: 20px;
            border: 2px solid #0066ff; border-radius: 50%;
            border-top: 2px solid transparent; animation: spin 1s linear infinite;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        
        /* Utilities */
        .hidden { display: none; }
        .text-center { text-align: center; }
        .mt-2 { margin-top: 1rem; }
        .mb-2 { margin-bottom: 1rem; }
    </style>
</head>
<body>
    <!-- Header -->
    <div class="header">
        <div class="container">
            <div class="header-content">
                <div class="logo">Cretzo AI</div>
                <div class="nav">
                    <a href="#home">Home</a>
                    <a href="#demo">Demo</a>
                    <a href="#contact">Contact</a>
                </div>
                <button class="btn" onclick="scrollTo('#contact')">Book Demo</button>
            </div>
        </div>
    </div>

    <!-- Hero -->
    <section id="home" class="hero">
        <div class="container">
            <h1>Smarter CV Screening.<br>Human-like AI Decisions.</h1>
            <p>Cretzo AI helps enterprises screen CVs like top recruiters — faster, accurate, and cost-effective.</p>
            
            <div class="hero-btns">
                <button class="btn" onclick="scrollTo('#demo')">Try Demo</button>
                <button class="btn" onclick="scrollTo('#contact')">Book Demo</button>
            </div>

            <div class="stats">
                <div class="stat">
                    <span class="stat-number">65%</span>
                    <span>Cost Reduction</span>
                </div>
                <div class="stat">
                    <span class="stat-number">10x</span>
                    <span>Faster Processing</span>
                </div>
                <div class="stat">
                    <span class="stat-number">95%</span>
                    <span>Accuracy Rate</span>
                </div>
                <div class="stat">
                    <span class="stat-number">500+</span>
                    <span>Enterprises</span>
                </div>
            </div>
        </div>
    </section>

    <!-- Demo -->
    <section id="demo" class="demo">
        <div class="container">
            <h2>Try Cretzo AI Demo</h2>
            <div class="demo-container">
                <div class="demo-grid">
                    <div class="demo-section">
                        <h3>Upload Documents</h3>
                        
                        <div class="upload-area" onclick="document.getElementById('jd').click()">
                            <div style="font-size: 2rem; margin-bottom: 1rem;">📋</div>
                            <h4>Job Description</h4>
                            <p>Click to upload JD</p>
                            <input type="file" id="jd" accept=".pdf,.docx,.txt" onchange="handleUpload('jd', this.files[0])">
                        </div>
                        
                        <div class="upload-area" onclick="document.getElementById('cvs').click()">
                            <div style="font-size: 2rem; margin-bottom: 1rem;">📄</div>
                            <h4>CV Files</h4>
                            <p>Click to upload CVs</p>
                            <input type="file" id="cvs" accept=".pdf,.docx,.txt" multiple onchange="handleUpload('cvs', this.files)">
                        </div>
                        
                        <button class="btn" onclick="processDemo()" id="process-btn" disabled style="width: 100%; margin-top: 1rem;">
                            Process with AI
                        </button>
                    </div>
                    
                    <div class="demo-section">
                        <h3>AI Results</h3>
                        <div id="results">
                            <div class="text-center" style="color: #94a3b8; padding: 2rem;">
                                Upload documents to see AI analysis
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Contact -->
    <section id="contact" class="contact">
        <div class="container">
            <h2>Get Started Today</h2>
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
                            <option value="other">Other</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label>Message</label>
                        <textarea name="message" rows="4" placeholder="Tell us about your needs..."></textarea>
                    </div>
                    
                    <button type="submit" class="btn" style="width: 100%;">
                        Schedule Demo
                    </button>
                </form>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <div class="footer">
        <div class="container">
            <p>&copy; 2024 Cretzo AI. All rights reserved.</p>
            <p style="margin-top: 1rem; color: #94a3b8;">Enterprise CV Screening Platform</p>
        </div>
    </div>

    <script>
        let uploadState = { jd: false, cvs: false };

        function scrollTo(target) {
            document.querySelector(target).scrollIntoView({ behavior: 'smooth' });
        }

        function handleUpload(type, files) {
            if (type === 'jd' && files) {
                uploadState.jd = true;
                document.querySelector('#jd').parentElement.innerHTML += '<div style="color: #00b4d8; margin-top: 1rem;">✅ JD uploaded</div>';
            } else if (type === 'cvs' && files.length > 0) {
                uploadState.cvs = true;
                document.querySelector('#cvs').parentElement.innerHTML += '<div style="color: #00b4d8; margin-top: 1rem;">✅ ' + files.length + ' CVs uploaded</div>';
            }
            
            if (uploadState.jd && uploadState.cvs) {
                document.getElementById('process-btn').disabled = false;
            }
        }

        function processDemo() {
            const btn = document.getElementById('process-btn');
            const results = document.getElementById('results');
            
            btn.innerHTML = '<span class="loading"></span> Processing...';
            btn.disabled = true;
            
            results.innerHTML = '<div class="text-center"><div class="loading" style="margin: 0 auto 1rem;"></div><p>AI analyzing CVs...</p></div>';
            
            // Simulate processing
            setTimeout(() => {
                results.innerHTML = `
                    <div class="result-item">
                        <div><h4>Sarah Chen</h4><p style="color: #94a3b8;">Senior Developer</p></div>
                        <div class="score">94%</div>
                    </div>
                    <div class="result-item">
                        <div><h4>John Martinez</h4><p style="color: #94a3b8;">Full Stack Engineer</p></div>
                        <div class="score">87%</div>
                    </div>
                    <div class="result-item">
                        <div><h4>Emily Johnson</h4><p style="color: #94a3b8;">Frontend Developer</p></div>
                        <div class="score">82%</div>
                    </div>
                    <div style="margin-top: 1rem; padding: 1rem; background: rgba(0,102,255,0.1); border-radius: 6px;">
                        <strong>🤖 AI Insight:</strong> Sarah Chen shows excellent match with required skills.
                    </div>
                `;
                btn.innerHTML = '✅ Analysis Complete';
            }, 3000);
        }

        function submitContact(e) {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData.entries());
            
            // Simple form submission
            fetch('/contact', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            }).then(() => {
                alert('Thank you! We will contact you within 24 hours.');
                e.target.reset();
            }).catch(() => {
                alert('Thank you! We will contact you within 24 hours.');
                e.target.reset();
            });
        }
    </script>
</body>
</html>'''

if FASTAPI_AVAILABLE:
    # FastAPI routes
    @app.get("/", response_class=HTMLResponse)
    async def home():
        return MINIMAL_HTML

    @app.get("/health")
    async def health():
        return {"status": "ok", "service": "Cretzo AI"}

    @app.post("/contact")
    async def contact_form(request: Request):
        try:
            data = await request.json()
            contacts.append({
                "timestamp": datetime.now().isoformat(),
                "data": data
            })
            return {"status": "success"}
        except:
            return {"status": "success"}  # Always return success for demo

    @app.get("/api/demo")
    async def demo_results():
        return {
            "candidates": [
                {"name": "Sarah Chen", "score": 94, "role": "Senior Developer"},
                {"name": "John Martinez", "score": 87, "role": "Full Stack Engineer"},
                {"name": "Emily Johnson", "score": 82, "role": "Frontend Developer"}
            ]
        }

# Fallback HTTP server if FastAPI fails
else:
    class SimpleHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/':
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(MINIMAL_HTML.encode())
            elif self.path == '/health':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"status":"ok"}')
            else:
                self.send_response(404)
                self.end_headers()
        
        def do_POST(self):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status":"success"}')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    
    if FASTAPI_AVAILABLE:
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        # Basic HTTP server fallback
        with socketserver.TCPServer(("0.0.0.0", port), SimpleHandler) as httpd:
            print(f"Server running on port {port}")
            httpd.serve_forever()
