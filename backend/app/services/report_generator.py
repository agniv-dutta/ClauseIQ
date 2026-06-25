from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from typing import List
from app.models.contract import Contract
from app.models.analysis import Analysis
from app.models.clause import Clause
from app.utils.logging_config import logger


class ReportGenerator:
    """Service for generating PDF reports from contract analysis."""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._add_custom_styles()
    
    def _add_custom_styles(self):
        """Add custom styles for the report."""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=10
        ))
    
    def generate_report(
        self,
        contract: Contract,
        analysis: Analysis,
        clauses: List[Clause]
    ) -> bytes:
        """Generate a PDF report for the contract analysis."""
        from io import BytesIO
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        story = []
        
        # Title
        title = Paragraph(f"Contract Analysis Report<br/>{contract.filename}", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.2 * inch))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", self.styles['CustomHeading']))
        summary_text = analysis.executive_summary or "No summary available."
        story.append(Paragraph(summary_text, self.styles['CustomBody']))
        story.append(Spacer(1, 0.2 * inch))
        
        # Risk Score
        story.append(Paragraph("Overall Risk Score", self.styles['CustomHeading']))
        risk_score = analysis.overall_risk_score
        risk_color = self._get_risk_color(risk_score)
        story.append(Paragraph(
            f"<font color='{risk_color}' size='18'>{risk_score}/100</font>",
            self.styles['CustomBody']
        ))
        story.append(Spacer(1, 0.2 * inch))
        
        # Risk Statistics
        story.append(Paragraph("Risk Statistics", self.styles['CustomHeading']))
        stats_data = [
            ["High Risk Clauses", str(analysis.high_risk_clause_count)],
            ["Medium Risk Clauses", str(analysis.medium_risk_clause_count)],
            ["Total Clauses Analyzed", str(len(clauses))]
        ]
        stats_table = Table(stats_data, colWidths=[2.5 * inch, 1.5 * inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(stats_table)
        story.append(Spacer(1, 0.3 * inch))
        
        # Clause Analysis
        story.append(Paragraph("Clause Analysis", self.styles['CustomHeading']))
        
        for clause in clauses:
            # Clause type and risk level
            clause_header = f"{clause.clause_type.value.replace('_', ' ')} - {clause.risk_level.value} RISK"
            clause_color = self._get_risk_color_for_level(clause.risk_level)
            story.append(Paragraph(
                f"<font color='{clause_color}' size='12'><b>{clause_header}</b></font>",
                self.styles['CustomBody']
            ))
            
            # Clause text (truncated)
            clause_text = clause.extracted_text[:200] + "..." if len(clause.extracted_text) > 200 else clause.extracted_text
            story.append(Paragraph(f"<i>Text:</i> {clause_text}", self.styles['CustomBody']))
            
            # Risk explanation
            if clause.risk_explanation:
                story.append(Paragraph(f"<i>Risk Explanation:</i> {clause.risk_explanation}", self.styles['CustomBody']))
            
            # Market comparison
            if clause.market_standard_comparison:
                story.append(Paragraph(f"<i>Market Comparison:</i> {clause.market_standard_comparison}", self.styles['CustomBody']))
            
            # Negotiation suggestion
            if clause.negotiation_suggestion:
                story.append(Paragraph(
                    f"<i>Negotiation Suggestion:</i> {clause.negotiation_suggestion}",
                    self.styles['CustomBody']
                ))
            
            story.append(Spacer(1, 0.15 * inch))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        logger.info(f"Generated PDF report for contract {contract.id}")
        return pdf_bytes
    
    def _get_risk_color(self, score: int) -> str:
        """Get color based on risk score."""
        if score >= 70:
            return "#e74c3c"  # Red
        elif score >= 40:
            return "#f39c12"  # Orange
        else:
            return "#27ae60"  # Green
    
    def _get_risk_color_for_level(self, risk_level) -> str:
        """Get color based on risk level."""
        from app.models.clause import RiskLevel
        if risk_level == RiskLevel.HIGH:
            return "#e74c3c"
        elif risk_level == RiskLevel.MEDIUM:
            return "#f39c12"
        elif risk_level == RiskLevel.LOW:
            return "#f1c40f"
        else:
            return "#27ae60"
