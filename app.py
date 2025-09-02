import streamlit as st
import re
import pandas as pd
from collections import Counter
import tempfile

st.set_page_config(page_title="Advanced CV Screener", layout="wide")
st.title("🚀 Advanced AI CV Screener")
st.write("Upload CVs and analyze against job description with detailed keyword insights")

# Try to import PDF/DOCX libraries with error handling
try:
    import PyPDF2
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    st.warning("PDF support disabled - install PyPDF2 for full functionality")

try:
    import docx2txt
    DOCX_SUPPORT = True
except ImportError:
    DOCX_SUPPORT = False
    st.warning("DOCX support disabled - install python-docx for full functionality")

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Settings")
    must_have_keywords = st.text_area(
        "**Must-Have Keywords** (comma-separated)", 
        placeholder="python, machine learning, sql, management",
        help="These keywords will be specifically tracked"
    )
    min_keyword_length = st.slider("Minimum keyword length", 3, 8, 4)

# Main area
jd_text = st.text_area("**Paste Job Description:**", height=150, 
                      placeholder="Copy and paste the job description here...")

uploaded_files = st.file_uploader("**Upload CVs (TXT/PDF/DOCX)**", 
                                 type=['txt', 'pdf', 'docx'], 
                                 accept_multiple_files=True,
                                 help="Select multiple files to compare")

def extract_text_from_file(file):
    """Extract text from uploaded file"""
    try:
        if file.type == "text/plain":
            # Text file
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
        
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document" and DOCX_SUPPORT:
            # DOCX file
            return docx2txt.process(file)
        
        else:
            # Fallback for unsupported types
            return "File type not fully supported. Please use text files for best results."
            
    except Exception as e:
        return f"Error reading file: {str(e)}"

def analyze_cv(cv_text, jd_text, must_have_list):
    """Analyze CV against JD"""
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
        'cv_preview': cv_clean[:500] + "..." if len(cv_clean) > 500 else cv_clean
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
                if cv_text and not cv_text.startswith("Error"):
                    analysis = analyze_cv(cv_text, jd_text, must_have_list)
                    
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
                else:
                    results.append({
                        'Filename': file.name,
                        'Score': '0%',
                        'Matched Keywords': 'Error',
                        'Must-Have Matches': '0/0',
                        'Status': '❌ Read Error'
                    })
        
        # Display results
        if results:
            st.subheader("📊 Summary Results")
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)
            
            # Detailed reports
            st.subheader("📋 Detailed Analysis")
            for report in detailed_reports:
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
    3. Upload CV files (TXT works best)
    4. Click Analyze to see results
    """)
