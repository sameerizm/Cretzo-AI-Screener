# 🎯 AI-Powered CV Screening System

A comprehensive, production-ready CV screening web application that uses advanced AI to analyze job descriptions and candidate CVs like a human recruiter would. Built with FastAPI backend and modern HTML/CSS/JavaScript frontend.

## 🌟 Features

### 🧠 Intelligent Analysis
- **Human-like Assessment**: Goes beyond keyword matching to understand context, synonyms, and implied experience
- **Semantic Similarity**: Uses sentence transformers for deep understanding of skills and requirements
- **Holistic Evaluation**: Considers experience, skills, achievements, certifications, career progression, and gaps

### 📊 Comprehensive Scoring
- **Multi-dimensional Scoring**: Evaluates candidates across skills match, experience level, qualifications, career progression, and certifications
- **Smart Recommendations**: Provides actionable insights and hiring recommendations
- **Red Flag Detection**: Identifies potential concerns like frequent job changes or employment gaps

### 📈 Professional Reporting
- **Interactive Dashboard**: Real-time results with charts and visual indicators
- **PDF Reports**: Downloadable professional reports with detailed analysis
- **Export Capabilities**: JSON API responses ready for integration

### 🚀 Production Ready
- **FastAPI Backend**: High-performance, async API with automatic documentation
- **CORS Enabled**: Ready for frontend integration at https://cretzo.in
- **Render Compatible**: Easy deployment with uvicorn
- **Error Handling**: Comprehensive error handling and logging

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   AI Engine     │
│   (HTML/JS)     │◄──►│   Backend       │◄──►│   (Transformers)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                               │
                       ┌─────────────────┐
                       │   PDF Reports   │
                       │   Generator     │
                       └─────────────────┘
```

## 📋 Prerequisites

- Python 3.9+
- 2GB+ RAM (for AI models)
- Modern web browser
- Internet connection (for downloading AI models on first run)

## 🚀 Quick Start

### Backend Setup

1. **Clone and Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Run the Application**
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

3. **Verify Installation**
```bash
curl http://localhost:8000/health
```

### Frontend Setup

1. **Serve the Frontend**
   - Option 1: Open `frontend.html` directly in a modern browser
   - Option 2: Use a local server (recommended):
```bash
# Python 3
python -m http.server 3000

# Node.js
npx serve .
```

2. **Update API URL**
   - Edit `frontend.html` and change `API_BASE_URL` to your backend URL

## 🛠️ API Documentation

### Core Endpoints

#### `POST /screen`
Main screening endpoint that processes job descriptions and CVs.

**Request:**
- `jd_file`: Job description file (PDF/DOCX)
- `cv_files`: Multiple CV files (PDF/DOCX)
- `must_have_skills`: Optional comma-separated critical skills
- `candidate_names`: Optional comma-separated candidate names

**Response:**
```json
{
  "screening_id": "uuid",
  "status": "success",
  "results": {
    "job_analysis": {...},
    "candidates": [...],
    "summary": {...}
  },
  "report_path": "/download_report/uuid"
}
```

#### `GET /health`
Health check endpoint for monitoring.

#### `GET /download_report/{screening_id}`
Download PDF report for a screening session.

#### `GET /screening/{screening_id}`
Retrieve screening results by ID.

### Interactive Documentation
Visit `http://localhost:8000/docs` for full interactive API documentation.

## 🧪 Testing

### Manual Testing

1. **Prepare Test Files**
   - Create a sample job description (PDF/DOCX)
   - Collect 3-5 sample CVs (PDF/DOCX)

2. **Test via Frontend**
   - Upload files through the web interface
   - Verify results display correctly
   - Download PDF report

3. **Test via API**
```bash
curl -X POST "http://localhost:8000/screen" \
  -F "jd_file=@job_description.pdf" \
  -F "cv_files=@cv1.pdf" \
  -F "cv_files=@cv2.pdf" \
  -F "must_have_skills=Python,JavaScript"
```

## 🎯 AI Analysis Features

### Job Description Analysis
- Extracts required and preferred skills
- Identifies experience level requirements
- Categorizes responsibilities and qualifications
- Determines role type and context

### CV Analysis
- **Skills Extraction**: Identifies technical and soft skills
- **Experience Calculation**: Estimates years of experience
- **Education Parsing**: Extracts degrees and qualifications
- **Certification Detection**: Finds professional certifications
- **Career Progression**: Analyzes growth trajectory
- **Strength/Weakness Identification**: Provides balanced assessment

### Intelligent Matching
- **Semantic Similarity**: Uses embeddings for contextual matching
- **Synonym Recognition**: Understands skill variations
- **Experience Weighting**: Considers seniority appropriately
- **Cultural Fit Indicators**: Evaluates beyond technical skills

## 📊 Scoring Algorithm

The AI uses a weighted scoring system:

```python
Final Score = (
    Skills Match (35%) +
    Experience Level (25%) +
    Qualifications (15%) +
    Career Progression (10%) +
    Certifications (10%)
) - Red Flags Penalty (5%)
```

### Score Interpretation
- **85-100%**: 🌟 Excellent fit - Recommend for interview
- **75-84%**: ✅ Good fit - Strong candidate
- **65-74%**: 👍 Moderate fit - Consider with reservations
- **50-64%**: ⚠️ Below average - Significant gaps
- **0-49%**: ❌ Poor fit - Not recommended

## 🚀 Deployment

### Render Deployment

1. **Connect Repository**
   - Link your GitHub repository to Render
   - Render will auto-detect the `render.yaml` configuration

2. **Environment Variables**
   - `PYTHON_VERSION`: 3.9.16
   - `ENVIRONMENT`: production

3. **Deployment**
   - Render will automatically install dependencies and start the service
   - Health check endpoint ensures service reliability

### Manual Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export PORT=8000
export ENVIRONMENT=production

# Start application
uvicorn app:app --host 0.0.0.0 --port $PORT
```

### Docker Deployment (Optional)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🔧 Configuration

### Model Configuration
The system uses `all-MiniLM-L6-v2` sentence transformer model by default. To use a different model:

```python
# In cv_processor.py
self.model = SentenceTransformer('your-model-name')
```

### Skill Synonyms
Customize skill matching by editing the `skill_synonyms` dictionary in `cv_processor.py`:

```python
self.skill_synonyms = {
    'python': ['python', 'py', 'django', 'flask', 'fastapi'],
    'javascript': ['javascript', 'js', 'node.js', 'nodejs', 'react'],
    # Add more synonyms...
}
```

## 🐛 Troubleshooting

### Common Issues

1. **Model Download Failures**
   ```bash
   # Clear cache and retry
   rm -rf ~/.cache/torch/sentence_transformers/
   python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
   ```

2. **PDF/DOCX Reading Errors**
   - Ensure files are not corrupted
   - Try with different file formats
   - Check file permissions

3. **Memory Issues**
   - Reduce batch size for large numbers of CVs
   - Consider using a smaller transformer model
   - Increase server memory allocation

4. **CORS Issues**
   - Update allowed origins in `app.py`
   - Ensure frontend URL matches backend configuration

### Logs and Debugging

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

1. **Code Standards**
   - Follow PEP 8 style guide
   - Add docstrings to all functions
   - Include type hints where possible

2. **Testing**
   - Test with various file formats
   - Verify cross-browser compatibility
   - Test with different job types

3. **Documentation**
   - Update README for new features
   - Document API changes
   - Include usage examples

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review API documentation at `/docs`
3. Open an issue on GitHub
4. Contact support with detailed error logs

## 🔮 Future Enhancements

- **Multi-language Support**: Support for non-English CVs
- **Video Analysis**: AI-powered video interview screening
- **Integration APIs**: Connect with ATS systems
- **Advanced Analytics**: Detailed hiring insights and trends
- **Custom Models**: Industry-specific AI models
- **Real-time Collaboration**: Multi-user screening sessions

---

**Built with ❤️ using FastAPI, Sentence Transformers, and modern web technologies**
