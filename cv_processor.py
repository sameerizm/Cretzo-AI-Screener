"""
Advanced CV Processing Module
Implements human-like recruiter logic for CV screening
Compatible with minimal dependencies for deployment
"""

import re
import json
import logging
from typing import List, Dict, Any, Tuple, Optional
import pdfplumber

# Handle docx import gracefully
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    class Document:
        def __init__(self, *args, **kwargs):
            raise ImportError("python-docx not available")

# Try to import ML libraries, fall back to basic matching if not available
try:
    from sentence_transformers import SentenceTransformer
    try:
        from sklearn.metrics.pairwise import cosine_similarity
    except ImportError:
        from numpy import dot
        from numpy.linalg import norm
        def cosine_similarity(a, b):
            return [[dot(a[0], b[0]) / (norm(a[0]) * norm(b[0]))]]
    ML_AVAILABLE = True
    print("✅ AI/ML libraries loaded successfully")
except ImportError as e:
    print(f"⚠️ ML libraries not available: {e}")
    print("📝 Using basic text matching instead of AI")
    ML_AVAILABLE = False
    # Mock classes for compatibility
    class SentenceTransformer:
        def __init__(self, model_name):
            self.model_name = model_name
            print(f"⚠️ Mock model loaded: {model_name}")
        def encode(self, texts):
            return [[0.0] * 384 for _ in texts]  # Mock embeddings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CVProcessor:
    """Advanced CV processor with human-like recruitment analysis"""
    
    def __init__(self):
        # Load pre-trained sentence transformer for semantic analysis
        if ML_AVAILABLE:
            try:
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                self.ai_enabled = True
                logger.info("✅ AI model loaded successfully")
            except Exception as e:
                logger.warning(f"⚠️ Could not load AI model: {e}")
                self.model = None
                self.ai_enabled = False
        else:
            self.model = None
            self.ai_enabled = False
            logger.info("📝 Using basic text matching mode")
        
        # Skill categories and synonyms for intelligent matching
        self.skill_synonyms = {
            'python': ['python', 'py', 'django', 'flask', 'fastapi'],
            'javascript': ['javascript', 'js', 'node.js', 'nodejs', 'react', 'vue', 'angular'],
            'java': ['java', 'spring', 'hibernate', 'j2ee'],
            'sql': ['sql', 'mysql', 'postgresql', 'oracle', 'database', 'rdbms'],
            'aws': ['aws', 'amazon web services', 'ec2', 's3', 'lambda', 'cloudformation'],
            'docker': ['docker', 'containerization', 'kubernetes', 'k8s'],
            'machine learning': ['ml', 'machine learning', 'ai', 'tensorflow', 'pytorch', 'scikit-learn'],
            'project management': ['project management', 'pmp', 'agile', 'scrum', 'kanban'],
        }
        
        # Experience level keywords
        self.experience_levels = {
            'senior': ['senior', 'lead', 'principal', 'architect', 'manager'],
            'mid': ['mid-level', 'intermediate', 'associate'],
            'junior': ['junior', 'entry', 'trainee', 'intern', 'graduate']
        }
        
    def extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF file"""
        try:
            with pdfplumber.open(file_content) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                return text.strip()
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            return ""
    
    def extract_text_from_docx(self, file_content: bytes) -> str:
        """Extract text from DOCX file"""
        if not DOCX_AVAILABLE:
            logger.warning("python-docx not available, skipping DOCX file")
            return ""
        
        try:
            from io import BytesIO
            doc = Document(BytesIO(file_content))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting DOCX text: {e}")
            return ""
    
    def extract_text_from_file(self, file_content: bytes, filename: str) -> str:
        """Extract text based on file extension"""
        if filename.lower().endswith('.pdf'):
            return self.extract_text_from_pdf(file_content)
        elif filename.lower().endswith(('.docx', '.doc')):
            return self.extract_text_from_docx(file_content)
        else:
            raise ValueError(f"Unsupported file format: {filename}")
    
    def extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills from text using pattern matching and NLP"""
        skills = set()
        text_lower = text.lower()
        
        # Common skill patterns
        skill_patterns = [
            r'\b(?:python|java|javascript|js|c\+\+|c#|php|ruby|go|rust|swift)\b',
            r'\b(?:react|angular|vue|django|flask|spring|laravel|express)\b',
            r'\b(?:mysql|postgresql|mongodb|redis|elasticsearch|oracle)\b',
            r'\b(?:aws|azure|gcp|docker|kubernetes|jenkins|git|linux)\b',
            r'\b(?:machine learning|ai|data science|tensorflow|pytorch)\b',
            r'\b(?:project management|agile|scrum|kanban|pmp|prince2)\b'
        ]
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, text_lower)
            skills.update(matches)
        
        # Extract from common skill sections
        skill_sections = re.findall(
            r'(?:skills|technologies|technical skills|expertise):?\s*([^\n]*(?:\n[^\n]*){0,10})',
            text_lower
        )
        
        for section in skill_sections:
            # Split by common delimiters
            section_skills = re.split(r'[,;|•\n]', section)
            for skill in section_skills:
                skill = skill.strip()
                if len(skill) > 1 and len(skill) < 30:
                    skills.add(skill)
        
        return list(skills)
    
    def extract_experience_years(self, text: str) -> int:
        """Extract years of experience from CV text"""
        experience_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'experience:\s*(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s*in\s*(?:software|development|programming)',
        ]
        
        years = []
        for pattern in experience_patterns:
            matches = re.findall(pattern, text.lower())
            for match in matches:
                try:
                    years.append(int(match))
                except ValueError:
                    continue
        
        if years:
            return max(years)  # Take the highest mentioned experience
        
        # If no explicit years mentioned, estimate from work history
        job_sections = re.findall(r'\b(20\d{2})\s*[-–]\s*(20\d{2}|present)', text.lower())
        if job_sections:
            total_years = 0
            for start, end in job_sections:
                start_year = int(start)
                end_year = 2024 if end == 'present' else int(end)
                total_years += max(0, end_year - start_year)
            return min(total_years, 25)  # Cap at 25 years
        
        return 0
    
    def extract_education(self, text: str) -> List[str]:
        """Extract education information"""
        education_patterns = [
            r'(?:bachelor|master|phd|doctorate|diploma|degree)\s*(?:of|in)?\s*([^\n]*)',
            r'(?:b\.?tech|m\.?tech|bca|mca|bsc|msc|be|me)\s*(?:in)?\s*([^\n]*)',
            r'(?:university|college|institute)\s*([^\n]*)'
        ]
        
        education = []
        for pattern in education_patterns:
            matches = re.findall(pattern, text.lower())
            education.extend([match.strip() for match in matches if match.strip()])
        
        return education
    
    def extract_certifications(self, text: str) -> List[str]:
        """Extract certifications from CV"""
        cert_patterns = [
            r'(?:certified|certification)\s*([^\n]*)',
            r'(?:aws|azure|google|microsoft|oracle)\s*certified\s*([^\n]*)',
            r'(?:pmp|prince2|itil|cissp|ceh|comptia)\s*([^\n]*)?'
        ]
        
        certifications = []
        for pattern in cert_patterns:
            matches = re.findall(pattern, text.lower())
            certifications.extend([match.strip() for match in matches if match.strip()])
        
        return certifications
    
    def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts"""
        if not self.ai_enabled or not self.model:
            # Fall back to basic string similarity
            return self._basic_text_similarity(text1, text2)
        
        try:
            embeddings = self.model.encode([text1, text2])
            if ML_AVAILABLE:
                similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            else:
                similarity = self._basic_text_similarity(text1, text2)
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return self._basic_text_similarity(text1, text2)
    
    def _basic_text_similarity(self, text1: str, text2: str) -> float:
        """Basic text similarity using word overlap"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def match_skills_semantic(self, cv_skills: List[str], jd_skills: List[str]) -> Tuple[List[str], List[str], float]:
        """Match skills using semantic similarity"""
        if not cv_skills or not jd_skills:
            return [], jd_skills, 0.0
        
        matched_skills = []
        missing_skills = []
        
        for jd_skill in jd_skills:
            best_match = None
            best_score = 0.0
            
            for cv_skill in cv_skills:
                # Direct match or synonym match
                if (jd_skill.lower() in cv_skill.lower() or 
                    cv_skill.lower() in jd_skill.lower() or
                    self._is_skill_synonym(jd_skill, cv_skill)):
                    best_match = cv_skill
                    best_score = 1.0
                    break
                
                # Semantic similarity
                similarity = self.calculate_semantic_similarity(jd_skill, cv_skill)
                if similarity > best_score and similarity > 0.7:  # Threshold for semantic match
                    best_match = cv_skill
                    best_score = similarity
            
            if best_match and best_score > 0.6:
                matched_skills.append(f"{jd_skill} → {best_match}")
            else:
                missing_skills.append(jd_skill)
        
        match_percentage = (len(matched_skills) / len(jd_skills)) * 100 if jd_skills else 0
        return matched_skills, missing_skills, match_percentage
    
    def _is_skill_synonym(self, skill1: str, skill2: str) -> bool:
        """Check if two skills are synonyms"""
        skill1_lower = skill1.lower()
        skill2_lower = skill2.lower()
        
        for main_skill, synonyms in self.skill_synonyms.items():
            if skill1_lower in synonyms and skill2_lower in synonyms:
                return True
        return False
    
    def analyze_job_description(self, jd_text: str) -> Dict[str, Any]:
        """Analyze job description to extract requirements"""
        analysis = {
            'required_skills': [],
            'optional_skills': [],
            'experience_level': 'mid',
            'min_experience_years': 0,
            'responsibilities': [],
            'qualifications': [],
            'company_info': '',
            'role_type': 'technical'
        }
        
        try:
            # Extract required skills
            required_sections = re.findall(
                r'(?:required|must have|essential)(?:\s+skills?)?:?\s*([^.]*(?:\.[^.]*){0,5})',
                jd_text.lower()
            )
            
            for section in required_sections:
                skills = re.split(r'[,;|•\n]', section)
                analysis['required_skills'].extend([s.strip() for s in skills if s.strip() and len(s.strip()) > 2])
            
            # Extract optional skills
            optional_sections = re.findall(
                r'(?:preferred|nice to have|plus|bonus)(?:\s+skills?)?:?\s*([^.]*(?:\.[^.]*){0,3})',
                jd_text.lower()
            )
            
            for section in optional_sections:
                skills = re.split(r'[,;|•\n]', section)
                analysis['optional_skills'].extend([s.strip() for s in skills if s.strip() and len(s.strip()) > 2])
            
            # If no explicit required/optional, extract all skills
            if not analysis['required_skills']:
                all_skills = self.extract_skills_from_text(jd_text)
                analysis['required_skills'] = all_skills[:10]  # Take first 10 as required
                analysis['optional_skills'] = all_skills[10:20]  # Next 10 as optional
            
            # Extract experience requirements
            exp_matches = re.findall(r'(\d+)\+?\s*years?\s*(?:of\s*)?experience', jd_text.lower())
            if exp_matches:
                analysis['min_experience_years'] = max([int(x) for x in exp_matches])
            
            # Determine experience level
            if any(level in jd_text.lower() for level in self.experience_levels['senior']):
                analysis['experience_level'] = 'senior'
            elif any(level in jd_text.lower() for level in self.experience_levels['junior']):
                analysis['experience_level'] = 'junior'
            
            # Extract responsibilities
            resp_sections = re.findall(
                r'(?:responsibilities|duties|you will):?\s*([^.]*(?:\.[^.]*){0,10})',
                jd_text.lower()
            )
            
            for section in resp_sections:
                responsibilities = re.split(r'[•\n]', section)
                analysis['responsibilities'].extend([r.strip() for r in responsibilities if r.strip() and len(r.strip()) > 10])
            
        except Exception as e:
            logger.error(f"Error analyzing job description: {e}")
        
        return analysis
    
    def analyze_cv(self, cv_text: str, candidate_name: str = "Unknown") -> Dict[str, Any]:
        """Comprehensive CV analysis"""
        analysis = {
            'candidate_name': candidate_name,
            'skills': self.extract_skills_from_text(cv_text),
            'experience_years': self.extract_experience_years(cv_text),
            'education': self.extract_education(cv_text),
            'certifications': self.extract_certifications(cv_text),
            'career_progression': self._analyze_career_progression(cv_text),
            'strengths': [],
            'weaknesses': [],
            'red_flags': []
        }
        
        # Analyze strengths and weaknesses
        analysis['strengths'] = self._identify_strengths(cv_text, analysis)
        analysis['weaknesses'] = self._identify_weaknesses(cv_text, analysis)
        analysis['red_flags'] = self._identify_red_flags(cv_text)
        
        return analysis
    
    def _analyze_career_progression(self, cv_text: str) -> str:
        """Analyze career progression pattern"""
        job_titles = re.findall(r'(?:^|\n)\s*([^\n]*(?:engineer|developer|manager|analyst|consultant|lead|senior|junior)[^\n]*)', cv_text.lower())
        
        if len(job_titles) < 2:
            return "insufficient_data"
        
        # Simple progression analysis
        junior_keywords = ['junior', 'trainee', 'intern', 'entry']
        senior_keywords = ['senior', 'lead', 'principal', 'manager', 'director']
        
        has_junior = any(keyword in ' '.join(job_titles) for keyword in junior_keywords)
        has_senior = any(keyword in ' '.join(job_titles) for keyword in senior_keywords)
        
        if has_senior and has_junior:
            return "good_progression"
        elif has_senior:
            return "senior_level"
        elif has_junior:
            return "junior_level"
        else:
            return "stable_level"
    
    def _identify_strengths(self, cv_text: str, analysis: Dict) -> List[str]:
        """Identify candidate strengths"""
        strengths = []
        
        # Experience-based strengths
        if analysis['experience_years'] > 8:
            strengths.append("Extensive experience")
        elif analysis['experience_years'] > 5:
            strengths.append("Good experience level")
        
        # Education strengths
        if any('master' in edu.lower() or 'phd' in edu.lower() for edu in analysis['education']):
            strengths.append("Advanced degree")
        
        # Certification strengths
        if len(analysis['certifications']) > 2:
            strengths.append("Well-certified")
        
        # Skill diversity
        if len(analysis['skills']) > 15:
            strengths.append("Diverse skill set")
        
        # Career progression
        if analysis['career_progression'] == 'good_progression':
            strengths.append("Clear career growth")
        
        # Leadership indicators
        leadership_keywords = ['lead', 'manage', 'mentor', 'coordinate', 'oversee']
        if any(keyword in cv_text.lower() for keyword in leadership_keywords):
            strengths.append("Leadership experience")
        
        return strengths
    
    def _identify_weaknesses(self, cv_text: str, analysis: Dict) -> List[str]:
        """Identify potential weaknesses"""
        weaknesses = []
        
        # Experience gaps
        if analysis['experience_years'] < 2:
            weaknesses.append("Limited experience")
        
        # Skill gaps
        if len(analysis['skills']) < 5:
            weaknesses.append("Limited technical skills")
        
        # No certifications
        if not analysis['certifications']:
            weaknesses.append("No professional certifications")
        
        # Career stagnation
        if analysis['career_progression'] == 'stable_level' and analysis['experience_years'] > 5:
            weaknesses.append("Limited career progression")
        
        return weaknesses
    
    def _identify_red_flags(self, cv_text: str) -> List[str]:
        """Identify red flags in CV"""
        red_flags = []
        
        # Frequent job changes
        job_dates = re.findall(r'\b(20\d{2})\s*[-–]\s*(20\d{2}|present)', cv_text.lower())
        if len(job_dates) > 5:
            avg_tenure = sum([2024 - int(start) if end == 'present' else int(end) - int(start) 
                             for start, end in job_dates]) / len(job_dates)
            if avg_tenure < 1.5:
                red_flags.append("Frequent job changes (avg < 1.5 years)")
        
        # Employment gaps
        if 'gap' in cv_text.lower() or 'break' in cv_text.lower():
            red_flags.append("Potential employment gaps")
        
        # Typos and formatting issues
        if cv_text.count('  ') > 20:  # Multiple spaces indicating poor formatting
            red_flags.append("Poor formatting")
        
        return red_flags
    
    def calculate_fit_score(self, cv_analysis: Dict, jd_analysis: Dict, 
                          skill_match_percentage: float, must_have_skills: List[str] = None) -> Dict[str, Any]:
        """Calculate comprehensive fit score like a human recruiter would"""
        
        weights = {
            'skills_match': 0.35,
            'experience_level': 0.25,
            'qualifications': 0.15,
            'career_progression': 0.10,
            'certifications': 0.10,
            'red_flags_penalty': -0.05
        }
        
        scores = {}
        
        # Skills match score
        scores['skills_match'] = min(skill_match_percentage, 100)
        
        # Experience level match
        cv_exp = cv_analysis['experience_years']
        jd_min_exp = jd_analysis['min_experience_years']
        jd_level = jd_analysis['experience_level']
        
        if cv_exp >= jd_min_exp:
            if jd_level == 'senior' and cv_exp >= 7:
                scores['experience_level'] = 100
            elif jd_level == 'mid' and 3 <= cv_exp <= 8:
                scores['experience_level'] = 100
            elif jd_level == 'junior' and cv_exp <= 3:
                scores['experience_level'] = 100
            else:
                scores['experience_level'] = 80  # Overqualified but acceptable
        else:
            # Underqualified
            exp_ratio = cv_exp / max(jd_min_exp, 1)
            scores['experience_level'] = min(exp_ratio * 70, 70)
        
        # Qualifications score
        if cv_analysis['education']:
            scores['qualifications'] = 85
        else:
            scores['qualifications'] = 40
        
        # Career progression score
        progression_scores = {
            'good_progression': 100,
            'senior_level': 85,
            'stable_level': 70,
            'junior_level': 80,
            'insufficient_data': 50
        }
        scores['career_progression'] = progression_scores.get(cv_analysis['career_progression'], 50)
        
        # Certifications score
        cert_count = len(cv_analysis['certifications'])
        if cert_count >= 3:
            scores['certifications'] = 100
        elif cert_count >= 1:
            scores['certifications'] = 70
        else:
            scores['certifications'] = 20
        
        # Red flags penalty
        red_flag_penalty = min(len(cv_analysis['red_flags']) * 10, 50)
        scores['red_flags_penalty'] = red_flag_penalty
        
        # Must-have skills penalty
        must_have_penalty = 0
        if must_have_skills:
            cv_skills_lower = [s.lower() for s in cv_analysis['skills']]
            missing_must_have = []
            for must_skill in must_have_skills:
                if not any(must_skill.lower() in cv_skill for cv_skill in cv_skills_lower):
                    missing_must_have.append(must_skill)
            
            if missing_must_have:
                must_have_penalty = len(missing_must_have) * 15
        
        # Calculate weighted final score
        final_score = 0
        for component, weight in weights.items():
            if component == 'red_flags_penalty':
                final_score += weight * scores[component] * -1  # Penalty
            else:
                final_score += weight * scores[component]
        
        # Apply must-have penalty
        final_score = max(0, final_score - must_have_penalty)
        
        # Determine emoji and recommendation
        emoji = self._get_score_emoji(final_score)
        recommendation = self._get_recommendation(final_score, cv_analysis, jd_analysis)
        
        return {
            'overall_score': round(final_score, 1),
            'component_scores': scores,
            'emoji': emoji,
            'recommendation': recommendation,
            'must_have_penalty': must_have_penalty,
            'strengths': cv_analysis['strengths'],
            'weaknesses': cv_analysis['weaknesses'],
            'red_flags': cv_analysis['red_flags']
        }
    
    def _get_score_emoji(self, score: float) -> str:
        """Get emoji based on score"""
        if score >= 85:
            return "🌟"
        elif score >= 75:
            return "✅"
        elif score >= 65:
            return "👍"
        elif score >= 50:
            return "⚠️"
        else:
            return "❌"
    
    def _get_recommendation(self, score: float, cv_analysis: Dict, jd_analysis: Dict) -> str:
        """Generate human-like recommendation"""
        if score >= 85:
            return "Excellent fit! Strong candidate with relevant experience and skills. Recommend for interview."
        elif score >= 75:
            return "Good fit with minor gaps. Solid candidate worth considering for next round."
        elif score >= 65:
            return "Moderate fit. Has potential but may need training in some areas. Consider if other candidates are limited."
        elif score >= 50:
            return "Below average fit. Significant skill or experience gaps. Only consider if willing to invest in training."
        else:
            return "Poor fit for this role. Major gaps in requirements. Not recommended for this position."
    
    def process_screening(self, jd_text: str, cv_files: List[Tuple[str, bytes, str]], 
                         must_have_skills: List[str] = None) -> Dict[str, Any]:
        """Main screening process"""
        try:
            # Analyze job description
            logger.info("Analyzing job description...")
            jd_analysis = self.analyze_job_description(jd_text)
            
            results = {
                'job_analysis': jd_analysis,
                'candidates': [],
                'summary': {},
                'processing_timestamp': None
            }
            
            # Process each CV
            for filename, content, candidate_name in cv_files:
                try:
                    logger.info(f"Processing CV: {filename}")
                    
                    # Extract text
                    cv_text = self.extract_text_from_file(content, filename)
                    if not cv_text:
                        logger.warning(f"No text extracted from {filename}")
                        continue
                    
                    # Analyze CV
                    cv_analysis = self.analyze_cv(cv_text, candidate_name)
                    
                    # Match skills
                    all_jd_skills = jd_analysis['required_skills'] + jd_analysis['optional_skills']
                    matched_skills, missing_skills, skill_match_percentage = self.match_skills_semantic(
                        cv_analysis['skills'], all_jd_skills
                    )
                    
                    # Calculate fit score
                    fit_analysis = self.calculate_fit_score(
                        cv_analysis, jd_analysis, skill_match_percentage, must_have_skills
                    )
                    
                    candidate_result = {
                        'filename': filename,
                        'candidate_name': candidate_name,
                        'cv_analysis': cv_analysis,
                        'matched_skills': matched_skills,
                        'missing_skills': missing_skills,
                        'skill_match_percentage': round(skill_match_percentage, 1),
                        'fit_score': fit_analysis['overall_score'],
                        'emoji': fit_analysis['emoji'],
                        'recommendation': fit_analysis['recommendation'],
                        'component_scores': fit_analysis['component_scores'],
                        'strengths': fit_analysis['strengths'],
                        'weaknesses': fit_analysis['weaknesses'],
                        'red_flags': fit_analysis['red_flags']
                    }
                    
                    results['candidates'].append(candidate_result)
                    
                except Exception as e:
                    logger.error(f"Error processing {filename}: {e}")
                    continue
            
            # Sort candidates by fit score
            results['candidates'].sort(key=lambda x: x['fit_score'], reverse=True)
            
            # Generate summary
            if results['candidates']:
                scores = [c['fit_score'] for c in results['candidates']]
                results['summary'] = {
                    'total_candidates': len(results['candidates']),
                    'avg_fit_score': round(np.mean(scores), 1),
                    'top_candidate': results['candidates'][0]['candidate_name'],
                    'top_score': results['candidates'][0]['fit_score'],
                    'candidates_above_75': len([s for s in scores if s >= 75]),
                    'candidates_above_50': len([s for s in scores if s >= 50])
                }
            
            results['processing_timestamp'] = "2024-01-01"  # Would be actual timestamp
            
            return results
            
        except Exception as e:
            logger.error(f"Error in screening process: {e}")
            raise
