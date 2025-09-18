"""
PDF Report Generation Module
Creates professional CV screening reports
"""

import os
import logging
from typing import Dict, Any, List
from fpdf import FPDF
from datetime import datetime

logger = logging.getLogger(__name__)

class PDFReportGenerator:
    """Professional PDF report generator for CV screening results"""
    
    def __init__(self):
        self.report_dir = "reports"
        os.makedirs(self.report_dir, exist_ok=True)
    
    def generate_report(self, screening_results: Dict[str, Any], screening_id: str) -> str:
        """Generate comprehensive PDF report"""
        try:
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            
            # Add title page
            self._add_title_page(pdf, screening_results)
            
            # Add executive summary
            self._add_executive_summary(pdf, screening_results)
            
            # Add job analysis
            self._add_job_analysis(pdf, screening_results['job_analysis'])
            
            # Add candidate results
            for candidate in screening_results['candidates']:
                self._add_candidate_page(pdf, candidate)
            
            # Add recommendations
            self._add_recommendations(pdf, screening_results)
            
            # Save report
            report_path = os.path.join(self.report_dir, f"screening_report_{screening_id}.pdf")
            pdf.output(report_path)
            
            logger.info(f"Report generated: {report_path}")
            return report_path
            
        except Exception as e:
            logger.error(f"Error generating PDF report: {e}")
            raise
    
    def _add_title_page(self, pdf: FPDF, screening_results: Dict[str, Any]):
        """Add title page to report"""
        pdf.add_page()
        
        # Set font and colors
        pdf.set_font("Arial", "B", 24)
        pdf.set_text_color(33, 37, 41)
        
        # Title
        pdf.ln(40)
        pdf.cell(0, 20, "CV SCREENING REPORT", 0, 1, 'C')
        
        pdf.set_font("Arial", "", 14)
        pdf.set_text_color(108, 117, 125)
        pdf.ln(10)
        pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%B %d, %Y')}", 0, 1, 'C')
        
        # Summary box
        pdf.ln(30)
        pdf.set_fill_color(248, 249, 250)
        pdf.rect(20, pdf.get_y(), 170, 80, 'F')
        
        pdf.set_font("Arial", "B", 16)
        pdf.set_text_color(33, 37, 41)
        pdf.ln(10)
        pdf.cell(0, 10, "SCREENING SUMMARY", 0, 1, 'C')
        
        pdf.set_font("Arial", "", 12)
        summary = screening_results.get('summary', {})
        
        pdf.ln(10)
        pdf.cell(0, 8, f"Total Candidates Screened: {summary.get('total_candidates', 0)}", 0, 1, 'C')
        pdf.cell(0, 8, f"Average Fit Score: {summary.get('avg_fit_score', 0)}%", 0, 1, 'C')
        pdf.cell(0, 8, f"Top Candidate: {summary.get('top_candidate', 'N/A')}", 0, 1, 'C')
        pdf.cell(0, 8, f"Candidates Above 75%: {summary.get('candidates_above_75', 0)}", 0, 1, 'C')
        
        # Footer
        pdf.ln(40)
        pdf.set_font("Arial", "I", 10)
        pdf.set_text_color(108, 117, 125)
        pdf.cell(0, 10, "Professional CV Screening System - Powered by AI", 0, 1, 'C')
    
    def _add_executive_summary(self, pdf: FPDF, screening_results: Dict[str, Any]):
        """Add executive summary page"""
        pdf.add_page()
        
        self._add_section_header(pdf, "EXECUTIVE SUMMARY")
        
        pdf.set_font("Arial", "", 11)
        pdf.set_text_color(33, 37, 41)
        
        summary = screening_results.get('summary', {})
        candidates = screening_results.get('candidates', [])
        
        # Overview paragraph
        overview_text = f"""This report presents the results of screening {summary.get('total_candidates', 0)} candidates for the specified position. Our AI-powered system evaluated each candidate across multiple dimensions including technical skills, experience level, qualifications, career progression, and cultural fit indicators.

Key Findings:
• Average candidate fit score: {summary.get('avg_fit_score', 0)}%
• {summary.get('candidates_above_75', 0)} candidates scored above 75% (recommended for interview)
• {summary.get('candidates_above_50', 0)} candidates scored above 50% (potential consideration)
• Top performing candidate: {summary.get('top_candidate', 'N/A')} with {summary.get('top_score', 0)}% fit score"""
        
        self._add_text_block(pdf, overview_text)
        
        # Top 3 candidates table
        if candidates:
            pdf.ln(15)
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "TOP CANDIDATES RANKING", 0, 1)
            
            # Table headers
            pdf.set_font("Arial", "B", 10)
            pdf.set_fill_color(52, 144, 220)
            pdf.set_text_color(255, 255, 255)
            
            col_widths = [10, 60, 25, 25, 70]
            headers = ["#", "Candidate Name", "Fit Score", "Emoji", "Recommendation"]
            
            for i, header in enumerate(headers):
                pdf.cell(col_widths[i], 10, header, 1, 0, 'C', True)
            pdf.ln()
            
            # Table rows (top 5 candidates)
            pdf.set_font("Arial", "", 9)
            pdf.set_text_color(33, 37, 41)
            
            for i, candidate in enumerate(candidates[:5]):
                if i % 2 == 0:
                    pdf.set_fill_color(248, 249, 250)
                else:
                    pdf.set_fill_color(255, 255, 255)
                
                row_data = [
                    str(i + 1),
                    candidate.get('candidate_name', 'Unknown')[:25],
                    f"{candidate.get('fit_score', 0)}%",
                    candidate.get('emoji', ''),
                    candidate.get('recommendation', '')[:30] + "..."
                ]
                
                for j, data in enumerate(row_data):
                    pdf.cell(col_widths[j], 8, str(data), 1, 0, 'C', True)
                pdf.ln()
    
    def _add_job_analysis(self, pdf: FPDF, job_analysis: Dict[str, Any]):
        """Add job analysis section"""
        pdf.add_page()
        
        self._add_section_header(pdf, "JOB REQUIREMENTS ANALYSIS")
        
        pdf.set_font("Arial", "", 11)
        
        # Required skills
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Required Skills:", 0, 1)
        
        pdf.set_font("Arial", "", 10)
        required_skills = job_analysis.get('required_skills', [])
        if required_skills:
            skills_text = "• " + "\n• ".join(required_skills[:15])  # Limit to 15 skills
            self._add_text_block(pdf, skills_text)
        else:
            pdf.cell(0, 8, "No specific required skills identified", 0, 1)
        
        pdf.ln(5)
        
        # Optional skills
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Preferred Skills:", 0, 1)
        
        pdf.set_font("Arial", "", 10)
        optional_skills = job_analysis.get('optional_skills', [])
        if optional_skills:
            skills_text = "• " + "\n• ".join(optional_skills[:10])
            self._add_text_block(pdf, skills_text)
        else:
            pdf.cell(0, 8, "No specific preferred skills identified", 0, 1)
        
        pdf.ln(5)
        
        # Experience requirements
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Experience Requirements:", 0, 1)
        
        pdf.set_font("Arial", "", 10)
        exp_text = f"• Minimum Experience: {job_analysis.get('min_experience_years', 0)} years\n"
        exp_text += f"• Experience Level: {job_analysis.get('experience_level', 'Not specified').title()}\n"
        exp_text += f"• Role Type: {job_analysis.get('role_type', 'Not specified').title()}"
        
        self._add_text_block(pdf, exp_text)
    
    def _add_candidate_page(self, pdf: FPDF, candidate: Dict[str, Any]):
        """Add detailed candidate analysis page"""
        pdf.add_page()
        
        # Candidate header
        candidate_name = candidate.get('candidate_name', 'Unknown Candidate')
        self._add_section_header(pdf, f"CANDIDATE: {candidate_name.upper()}")
        
        # Score overview box
        pdf.set_fill_color(248, 249, 250)
        pdf.rect(15, pdf.get_y(), 180, 35, 'F')
        
        pdf.ln(5)
        pdf.set_font("Arial", "B", 16)
        pdf.set_text_color(52, 144, 220)
        
        fit_score = candidate.get('fit_score', 0)
        emoji = candidate.get('emoji', '')
        
        pdf.cell(90, 10, f"Overall Fit Score: {fit_score}% {emoji}", 0, 0)
        
        # Skills match percentage
        skill_match = candidate.get('skill_match_percentage', 0)
        pdf.set_font("Arial", "", 12)
        pdf.set_text_color(33, 37, 41)
        pdf.cell(90, 10, f"Skills Match: {skill_match}%", 0, 1)
        
        pdf.ln(5)
        pdf.set_font("Arial", "", 10)
        recommendation = candidate.get('recommendation', '')
        self._add_text_block(pdf, f"Recommendation: {recommendation}")
        
        pdf.ln(10)
        
        # Candidate details in two columns
        cv_analysis = candidate.get('cv_analysis', {})
        
        # Left column - Basic info
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 8, "CANDIDATE PROFILE", 0, 1)
        
        pdf.set_font("Arial", "", 10)
        profile_text = f"Experience: {cv_analysis.get('experience_years', 0)} years\n"
        profile_text += f"Career Stage: {cv_analysis.get('career_progression', 'Unknown').replace('_', ' ').title()}\n"
        profile_text += f"Education: {len(cv_analysis.get('education', []))} qualification(s)\n"
        profile_text += f"Certifications: {len(cv_analysis.get('certifications', []))}\n"
        profile_text += f"Technical Skills: {len(cv_analysis.get('skills', []))}"
        
        self._add_text_block(pdf, profile_text)
        
        pdf.ln(10)
        
        # Skills analysis
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 8, "SKILLS ANALYSIS", 0, 1)
        
        # Matched skills
        pdf.set_font("Arial", "B", 10)
        pdf.set_text_color(40, 167, 69)
        pdf.cell(0, 6, "✓ Matched Skills:", 0, 1)
        
        pdf.set_font("Arial", "", 9)
        pdf.set_text_color(33, 37, 41)
        matched_skills = candidate.get('matched_skills', [])
        if matched_skills:
            skills_text = "\n".join([f"• {skill}" for skill in matched_skills[:10]])
            self._add_text_block(pdf, skills_text)
        else:
            pdf.cell(0, 6, "No skills matched", 0, 1)
        
        pdf.ln(5)
        
        # Missing skills
        pdf.set_font("Arial", "B", 10)
        pdf.set_text_color(220, 53, 69)
        pdf.cell(0, 6, "✗ Missing Skills:", 0, 1)
        
        pdf.set_font("Arial", "", 9)
        pdf.set_text_color(33, 37, 41)
        missing_skills = candidate.get('missing_skills', [])
        if missing_skills:
            skills_text = "\n".join([f"• {skill}" for skill in missing_skills[:10]])
            self._add_text_block(pdf, skills_text)
        else:
            pdf.cell(0, 6, "No critical skills missing", 0, 1)
        
        pdf.ln(10)
        
        # Strengths and weaknesses
        self._add_strengths_weaknesses(pdf, candidate)
        
        # Red flags if any
        red_flags = candidate.get('red_flags', [])
        if red_flags:
            pdf.ln(5)
            pdf.set_font("Arial", "B", 10)
            pdf.set_text_color(220, 53, 69)
            pdf.cell(0, 6, "⚠ Red Flags:", 0, 1)
            
            pdf.set_font("Arial", "", 9)
            pdf.set_text_color(33, 37, 41)
            flags_text = "\n".join([f"• {flag}" for flag in red_flags])
            self._add_text_block(pdf, flags_text)
    
    def _add_strengths_weaknesses(self, pdf: FPDF, candidate: Dict[str, Any]):
        """Add strengths and weaknesses section"""
        # Strengths
        strengths = candidate.get('strengths', [])
        if strengths:
            pdf.set_font("Arial", "B", 10)
            pdf.set_text_color(40, 167, 69)
            pdf.cell(0, 6, "💪 Key Strengths:", 0, 1)
            
            pdf.set_font("Arial", "", 9)
            pdf.set_text_color(33, 37, 41)
            strengths_text = "\n".join([f"• {strength}" for strength in strengths])
            self._add_text_block(pdf, strengths_text)
            
            pdf.ln(5)
        
        # Weaknesses
        weaknesses = candidate.get('weaknesses', [])
        if weaknesses:
            pdf.set_font("Arial", "B", 10)
            pdf.set_text_color(255, 193, 7)
            pdf.cell(0, 6, "⚡ Areas for Improvement:", 0, 1)
            
            pdf.set_font("Arial", "", 9)
            pdf.set_text_color(33, 37, 41)
            weaknesses_text = "\n".join([f"• {weakness}" for weakness in weaknesses])
            self._add_text_block(pdf, weaknesses_text)
    
    def _add_recommendations(self, pdf: FPDF, screening_results: Dict[str, Any]):
        """Add final recommendations section"""
        pdf.add_page()
        
        self._add_section_header(pdf, "HIRING RECOMMENDATIONS")
        
        candidates = screening_results.get('candidates', [])
        
        if not candidates:
            pdf.set_font("Arial", "", 12)
            pdf.cell(0, 10, "No candidates processed in this screening.", 0, 1)
            return
        
        pdf.set_font("Arial", "", 11)
        
        # Immediate interview recommendations
        high_score_candidates = [c for c in candidates if c.get('fit_score', 0) >= 75]
        if high_score_candidates:
            pdf.set_font("Arial", "B", 12)
            pdf.set_text_color(40, 167, 69)
            pdf.cell(0, 10, "🌟 RECOMMENDED FOR IMMEDIATE INTERVIEW", 0, 1)
            
            pdf.set_font("Arial", "", 10)
            pdf.set_text_color(33, 37, 41)
            for candidate in high_score_candidates[:3]:
                name = candidate.get('candidate_name', 'Unknown')
                score = candidate.get('fit_score', 0)
                pdf.cell(0, 6, f"• {name} - {score}% fit", 0, 1)
            
            pdf.ln(5)
        
        # Consider for interview
        medium_score_candidates = [c for c in candidates if 60 <= c.get('fit_score', 0) < 75]
        if medium_score_candidates:
            pdf.set_font("Arial", "B", 12)
            pdf.set_text_color(255, 193, 7)
            pdf.cell(0, 10, "👍 CONSIDER FOR INTERVIEW", 0, 1)
            
            pdf.set_font("Arial", "", 10)
            pdf.set_text_color(33, 37, 41)
            for candidate in medium_score_candidates[:3]:
                name = candidate.get('candidate_name', 'Unknown')
                score = candidate.get('fit_score', 0)
                pdf.cell(0, 6, f"• {name} - {score}% fit", 0, 1)
            
            pdf.ln(5)
        
        # Overall insights
        pdf.ln(10)
        pdf.set_font("Arial", "B", 12)
        pdf.set_text_color(33, 37, 41)
        pdf.cell(0, 10, "SCREENING INSIGHTS", 0, 1)
        
        summary = screening_results.get('summary', {})
        avg_score = summary.get('avg_fit_score', 0)
        
        insights_text = f"""Based on the screening of {summary.get('total_candidates', 0)} candidates:

• The average fit score was {avg_score}%, indicating {'good' if avg_score >= 70 else 'moderate' if avg_score >= 50 else 'limited'} overall candidate quality
• {summary.get('candidates_above_75', 0)} candidates exceeded the recommended threshold of 75%
• {summary.get('candidates_above_50', 0)} candidates showed reasonable potential for the role

Next Steps:
1. Schedule interviews with top-scoring candidates
2. Consider skill-specific assessments for technical roles
3. Verify experience claims through reference checks
4. Evaluate cultural fit through behavioral interviews"""
        
        self._add_text_block(pdf, insights_text)
        
        # Footer
        pdf.ln(20)
        pdf.set_font("Arial", "I", 9)
        pdf.set_text_color(108, 117, 125)
        pdf.cell(0, 8, "This report was generated using advanced AI algorithms for CV screening.", 0, 1, 'C')
        pdf.cell(0, 8, "Human judgment should be applied in final hiring decisions.", 0, 1, 'C')
    
    def _add_section_header(self, pdf: FPDF, title: str):
        """Add a formatted section header"""
        pdf.set_font("Arial", "B", 14)
        pdf.set_text_color(52, 144, 220)
        pdf.ln(5)
        pdf.cell(0, 12, title, 0, 1)
        
        # Add underline
        pdf.set_draw_color(52, 144, 220)
        pdf.line(15, pdf.get_y(), 195, pdf.get_y())
        pdf.ln(8)
    
    def _add_text_block(self, pdf: FPDF, text: str):
        """Add a block of text with proper formatting"""
        # Split text into lines
        lines = text.split('\n')
        
        for line in lines:
            if line.strip():
                # Handle long lines by wrapping
                if len(line) > 90:
                    words = line.split(' ')
                    current_line = ""
                    for word in words:
                        if len(current_line + word + " ") <= 90:
                            current_line += word + " "
                        else:
                            if current_line:
                                pdf.cell(0, 5, current_line.strip(), 0, 1)
                            current_line = word + " "
                    if current_line:
                        pdf.cell(0, 5, current_line.strip(), 0, 1)
                else:
                    pdf.cell(0, 5, line, 0, 1)
            else:
                pdf.ln(3)
