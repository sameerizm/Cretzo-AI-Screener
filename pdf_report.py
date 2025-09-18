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
