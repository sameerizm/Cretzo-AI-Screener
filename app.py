import streamlit as st
import re
import pandas as pd
from collections import Counter
import PyPDF2
import docx2txt
import tempfile
import os

st.set_page_config(page_title="Advanced CV Screener", layout="wide")
st.title("🚀 Advanced AI CV Screener")
st.write("Upload multiple CVs and analyze against job description with detailed keyword insights")

# Sidebar for must-have keywords
with st.sidebar:
    st.header("⚙️ Settings")
    must_have_keywords = st.text_area(
        "**Must-Have Keywords** (comma-separated)", 
        placeholder="python, machine learning, sql, management",
        help="These keywords will be specifically tracked and weighted higher"
    )
    min_keyword_length = st.slider("Minimum keyword length", 3, 8, 4)
    match_threshold = st.slider("Match score threshold (%)", 50, 90, 70)

# Main area
jd_text = st.text_area("**Paste Job Description:**", height=150, 
                      placeholder="Copy and paste the job description here...")

uploaded_files = st.file_uploader("**Upload CVs (PDF/DOCX)**", 
                                 type=['pdf', 'docx'], 
                                 accept_multiple_files=True,
                                 help="Select multiple files to compare")

def extract_text_from_file(file):
    """Extract text from uploaded file"""
    try:
        if file.type == "application/pdf":
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + " "
            return text
        
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return docx2txt.process(file)
        
    except Exception as e:
        st.error(f"Error reading {file.name}: {str(e)}")
        return ""

def analyze_cv(cv_text, jd_text, must_have_list):
    """Analyze CV against JD"""
    # Clean text
    def clean_text(text):
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.lower().strip()
    
    cv_clean = clean_text(cv_text)
    jd_clean = clean_text(jd_text)
    
    # Extract keywords (filter short words)
    jd_words = [word for word in jd_clean.split() if len(word) >= min_keyword_length]
    cv_words = cv_clean.split()
    
    # Count frequencies
    jd_word_count = Counter(jd_words)
    cv_word_count = Counter(cv_words)
    
    # Find matching keywords with counts
    matching_keywords = {}
    for word, jd_count in jd_word_count.items():
        if word in cv_word_count:
            matching_keywords[word] = {
                'jd_count': jd_count,
                'cv_count': cv_word_count[word],
                'is_must_have': word in must_have_list
            }
    
    # Calculate scores
    total_jd_words = len(jd_words)
    matched_words = len(matching_keywords)
    
    if total_jd_words > 0:
        base_score = (matched_words / total_jd_words) * 100
    else:
        base_score = 0
    
    # Bonus for must-have keywords
    must_have_matches = sum(1 for word in must_have_list if word in matching_keywords)
    must_have_bonus = must_have_matches * 5  # 5% bonus per must-have keyword
    
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
                if cv_text:
                    analysis = analyze_cv(cv_text, jd_text, must_have_list)
                    
                    results.append({
                        'Filename': file.name,
                        'Score': f"{analysis['score']:.1f}%",
                        'Matched Keywords': analysis['matched_keywords_count'],
                        'Must-Have Matches': f"{analysis['must_have_matches']}/{analysis['total_must_have']}",
                        'Status': '✅ Good Match' if analysis['score'] >= match_threshold else '⚠️ Needs Review'
                    })
                    
                    detailed_reports.append({
                        'file': file.name,
                        'analysis': analysis,
                        'cv_text': cv_text
                    })
        
        # Display summary table
        st.subheader("📊 Summary Results")
        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True)
        
        # Detailed reports for each CV
        st.subheader("📋 Detailed Analysis")
        
        for report in detailed_reports:
            with st.expander(f"🔍 {report['file']} - {report['analysis']['score']:.1f}%", expanded=False):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Overall Score", f"{report['analysis']['score']:.1f}%")
                with col2:
                    st.metric("Keywords Matched", 
                             f"{report['analysis']['matched_keywords_count']}/{report['analysis']['total_jd_keywords']}")
                with col3:
                    st.metric("Must-Have Keywords", 
                             f"{report['analysis']['must_have_matches']}/{report['analysis']['total_must_have']}")
                
                # Keyword frequency table
                st.subheader("📈 Keyword Frequency Analysis")
                
                keyword_data = []
                for word, counts in report['analysis']['matching_keywords'].items():
                    keyword_data.append({
                        'Keyword': word,
                        'In JD': counts['jd_count'],
                        'In CV': counts['cv_count'],
                        'Must-Have': '✅' if counts['is_must_have'] else '➖'
                    })
                
                if keyword_data:
                    keyword_df = pd.DataFrame(keyword_data)
                    st.dataframe(keyword_df.sort_values('In JD', ascending=False), 
                               use_container_width=True)
                else:
                    st.info("No matching keywords found")
                
                # Must-have keywords check
                if must_have_list:
                    st.subheader("✅ Must-Have Keywords Check")
                    must_have_status = []
                    for keyword in must_have_list:
                        if keyword in report['analysis']['matching_keywords']:
                            must_have_status.append(f"✅ {keyword} (Found {report['analysis']['matching_keywords'][keyword]['cv_count']} times)")
                        else:
                            must_have_status.append(f"❌ {keyword} (Missing)")
                    
                    for status in must_have_status:
                        st.write(status)
                
                # CV preview
                with st.expander("👀 CV Text Preview"):
                    st.text(report['analysis']['cv_preview'])
        
        # Download results
        if st.button("📥 Download Summary Report"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV Report",
                data=csv,
                file_name="cv_analysis_report.csv",
                mime="text/csv"
            )

# Instructions
with st.expander("ℹ️ How to use this tool"):
    st.write("""
    1. **Add Must-Have Keywords**: In the sidebar, list critical skills required for the role (comma-separated)
    2. **Paste Job Description**: The main JD you're screening against
    3. **Upload Multiple CVs**: Select all CVs you want to screen at once
    4. **Analyze**: Get detailed scores and keyword analysis for each CV
    
    **Features:**
    - ✅ Multiple file upload
    - ✅ Must-have keyword tracking
    - ✅ Keyword frequency counts
    - ✅ Score threshold filtering
    - ✅ Downloadable reports
    """)