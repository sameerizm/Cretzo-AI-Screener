import streamlit as st
import re
import pandas as pd
from collections import Counter
import tempfile

st.set_page_config(page_title="Advanced CV Screener", layout="wide")
st.title("🚀 Advanced AI CV Screener")
st.write("Upload CVs and analyze against job description with detailed keyword insights")

# Import with better error handling and alternatives
PDF_SUPPORT = True
DOCX_SUPPORT = True

try:
    import pypdf2 as PyPDF2  # Use lowercase import
except ImportError:
    try:
        import PyPDF2  # Try original uppercase
    except ImportError:
        PDF_SUPPORT = False
        st.sidebar.warning("📄 PDF support disabled - install pypdf2")

try:
    import docx2txt
except ImportError:
    DOCX_SUPPORT = False
    st.sidebar.warning("📝 DOCX support disabled - install python-docx")

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Settings")
    must_have_keywords = st.text_area(
        "**Must-Have Keywords** (comma-separated)", 
        placeholder="python, machine learning, sql, management",
        help="These keywords will be specifically tracked"
    )
    min_keyword_length = st.slider("Minimum keyword length", 3, 8, 4)
    
    # Show status
    st.header("📊 System Status")
    if PDF_SUPPORT:
        st.success("✅ PDF support: ENABLED")
    else:
        st.error("❌ PDF support: DISABLED")
    
    if DOCX_SUPPORT:
        st.success("✅ DOCX support: ENABLED")
    else:
        st.error("❌ DOCX support: DISABLED")

# Main area
jd_text = st.text_area("**Paste Job Description:**", height=150, 
                      placeholder="Copy and paste the job description here...")

# File upload based on available support
file_types = ['txt']
if PDF_SUPPORT:
    file_types.append('pdf')
if DOCX_SUPPORT:
    file_types.append('docx')

uploaded_files = st.file_uploader(f"**Upload CVs** (Supported: {', '.join(file_types).upper()})", 
                                 type=file_types, 
                                 accept_multiple_files=True,
                                 help="Select multiple files to compare")

def extract_text_from_file(file):
    """Extract text from uploaded file"""
    try:
        if file.type == "text/plain":
            # Text file - always supported
            return file.getvalue().decode("utf-8")
        
        elif file.type == "application/pdf" and PDF_SUPPORT:
            # PDF file
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + " "
            return text
        
        elif (file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document" and 
              DOCX_SUPPORT):
            # DOCX file
            return docx2txt.process(file)
        
        else:
            return f"File type not supported: {file.type}"
            
    except Exception as e:
        return f"Error reading {file.name}: {str(e)}"

def analyze_cv(cv_text, jd_text, must_have_list):
    """Analyze CV against JD"""
    # Skip analysis if we got an error message instead of actual text
    if cv_text.startswith("File type not supported") or cv_text.startswith("Error reading"):
        return {
            'score': 0,
            'matching_keywords': {},
            'total_jd_keywords': 0,
            'matched_keywords_count': 0,
            'must_have_matches': 0,
            'total_must_have': len(must_have_list),
            'cv_preview': cv_text,
            'error': True
        }
    
    # Clean text
    def clean_text(text):
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.lower().strip()
    
    cv_clean = clean_text(cv_text)
    jd_clean = clean_text(jd_text)
    
    # Extract keywords
    jd_words = [word for word in jd_clean.split() if len(word) >= min_keyword_length]
    cv_words = cv_clean.split()
    
    # Count frequencies
    jd_word_count = Counter(jd_words)
    cv_word_count = Counter(cv_words)
    
    # Find matching keywords
    matching_keywords = {}
    for word, jd_count in jd_word_count.items():
        if word in cv_word_count:
            matching_keywords[word] = {
                'jd_count': jd_count,
                'cv_count': cv_word_count[word],
                'is_must_have': word in must_have_list
            }
    
    # Calculate score
    total_jd_words = len(jd_words)
    matched_words = len(matching_keywords)
    
    if total_jd_words > 0:
        base_score = (matched_words / total_jd_words) * 100
    else:
        base_score = 0
    
    # Bonus for must-have keywords
    must_have_matches = sum(1 for word in must_have_list if word in matching_keywords)
    must_have_bonus = must_have_matches * 5
    final_score = min(base_score + must_have_bonus, 100)
    
    return {
        'score': final_score,
        'matching_keywords': matching_keywords,
        'total_jd_keywords': total_jd_words,
        'matched_keywords_count': matched_words,
        'must_have_matches': must_have_matches,
        'total_must_have': len(must_have_list),
        'cv_preview': cv_clean[:500] + "..." if len(cv_clean) > 500 else cv_clean,
        'error': False
    }

if st.button("🚀 Analyze All CVs", key="analyze_all"):
    if not uploaded_files:
        st.error("❌ Please upload at least one CV file!")
    elif not jd_text.strip():
        st.error("❌ Please paste a job description first!")
    else:
        # Process must-have keywords
        must_have_list = [word.strip().lower() for word in must_have_keywords.split(',') if word.strip()]
        
        results = []
        detailed_reports = []
        
        with st.spinner(f"🔍 Analyzing {len(uploaded_files)} CVs..."):
            for file in uploaded_files:
                cv_text = extract_text_from_file(file)
                analysis = analyze_cv(cv_text, jd_text, must_have_list)
                
                if analysis['error']:
                    results.append({
                        'Filename': file.name,
                        'Score': '0%',
                        'Matched Keywords': 'Error',
                        'Must-Have Matches': '0/0',
                        'Status': '❌ Read Error'
                    })
                else:
                    results.append({
                        'Filename': file.name,
                        'Score': f"{analysis['score']:.1f}%",
                        'Matched Keywords': analysis['matched_keywords_count'],
                        'Must-Have Matches': f"{analysis['must_have_matches']}/{analysis['total_must_have']}",
                        'Status': '✅ Good Match' if analysis['score'] >= 70 else '⚠️ Needs Review'
                    })
                    
                    detailed_reports.append({
                        'file': file.name,
                        'analysis': analysis
                    })
        
        # Display results
        if results:
            st.subheader("📊 Summary Results")
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)
            
            # Detailed reports for successful analyses
            successful_reports = [r for r in detailed_reports if not r['analysis']['error']]
            if successful_reports:
                st.subheader("📋 Detailed Analysis")
                for report in successful_reports:
                    with st.expander(f"🔍 {report['file']} - {report['analysis']['score']:.1f}%"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Score", f"{report['analysis']['score']:.1f}%")
                        with col2:
                            st.metric("Keywords", f"{report['analysis']['matched_keywords_count']}/{report['analysis']['total_jd_keywords']}")
                        with col3:
                            st.metric("Must-Have", f"{report['analysis']['must_have_matches']}/{report['analysis']['total_must_have']}")
                        
                        # Keyword table
                        if report['analysis']['matching_keywords']:
                            keyword_data = []
                            for word, counts in report['analysis']['matching_keywords'].items():
                                keyword_data.append({
                                    'Keyword': word,
                                    'In JD': counts['jd_count'],
                                    'In CV': counts['cv_count'],
                                    'Must-Have': '✅' if counts['is_must_have'] else '➖'
                                })
                            keyword_df = pd.DataFrame(keyword_data)
                            st.dataframe(keyword_df.sort_values('In JD', ascending=False), use_container_width=True)

# Instructions
with st.expander("ℹ️ How to use"):
    st.write("""
    1. Add must-have keywords in sidebar
    2. Paste job description
    3. Upload CV files
    4. Click Analyze to see results
    
    **Note:** If PDF/DOCX support is disabled, convert files to TXT format for best results.
    """)
