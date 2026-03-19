"""
PDF Report Generator Service
Generates professional PDF reports from dashboard data
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import io
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend


class PDFGenerator:
    """Generate professional PDF reports from analytics data"""
    
    def __init__(self):
        self.pagesize = letter
        self.styles = getSampleStyleSheet()
        self._setup_styles()
    
    def _setup_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2563eb'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#0f172a'),
            spaceAfter=8,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            spaceAfter=6
        ))
    
    def generate_pdf(self, dashboard_data):
        """
        Generate PDF report from dashboard data
        
        Args:
            dashboard_data (dict): Dashboard data containing stats, charts, etc.
        
        Returns:
            bytes: PDF file content
        """
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=self.pagesize,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        elements = []
        
        # Title
        title = Paragraph("Analytics Dashboard Report", self.styles['CustomTitle'])
        elements.append(title)
        
        # Report Date
        date_text = f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
        date_para = Paragraph(date_text, self.styles['Normal'])
        elements.append(date_para)
        elements.append(Spacer(1, 0.3*inch))
        
        # Statistics Section
        if 'statistics' in dashboard_data:
            elements.append(Paragraph("Data Statistics", self.styles['CustomHeading']))
            stats = dashboard_data['statistics']
            
            stats_data = [
                ['Metric', 'Value'],
                ['Total Records', str(stats.get('total_records', 0))],
                ['Total Columns', str(stats.get('total_columns', 0))],
                ['Missing Values', str(stats.get('missing_values', 0))],
                ['Duplicate Rows', str(stats.get('duplicate_rows', 0))],
                ['Data Quality Score', f"{stats.get('quality_score', 0):.1f}%"]
            ]
            
            stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f4f8')]),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ]))
            elements.append(stats_table)
            elements.append(Spacer(1, 0.3*inch))
        
        # Data Quality Section
        if 'issues' in dashboard_data and dashboard_data['issues']:
            elements.append(Paragraph("Data Quality Issues", self.styles['CustomHeading']))
            
            issues_data = [['Type', 'Issue', 'Impact']]
            for issue in dashboard_data['issues']:
                issues_data.append([
                    issue.get('type', 'Unknown'),
                    issue.get('message', ''),
                    issue.get('severity', 'Low')
                ])
            
            issues_table = Table(issues_data, colWidths=[1.5*inch, 3*inch, 1.5*inch])
            issues_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ef4444')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fee2e2')]),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ]))
            elements.append(issues_table)
            elements.append(Spacer(1, 0.3*inch))
        else:
            validation_text = "No data quality issues detected. Dataset is clean and ready for analysis."
            elements.append(Paragraph(validation_text, self.styles['CustomBody']))
            elements.append(Spacer(1, 0.3*inch))
        
        # Summary Section
        elements.append(PageBreak())
        elements.append(Paragraph("Summary", self.styles['CustomHeading']))
        
        summary_items = []
        if dashboard_data.get('statistics', {}).get('total_records', 0) > 0:
            summary_items.append(
                f"• Dataset contains {dashboard_data['statistics']['total_records']} records "
                f"with {dashboard_data['statistics']['total_columns']} columns"
            )
        
        if dashboard_data.get('statistics', {}).get('missing_values', 0) > 0:
            summary_items.append(
                f"• {dashboard_data['statistics']['missing_values']} missing values detected"
            )
        
        if dashboard_data.get('statistics', {}).get('duplicate_rows', 0) > 0:
            summary_items.append(
                f"• {dashboard_data['statistics']['duplicate_rows']} duplicate rows found"
            )
        
        quality_score = dashboard_data.get('statistics', {}).get('quality_score', 0)
        summary_items.append(f"• Overall data quality score: {quality_score:.1f}%")
        
        for item in summary_items:
            elements.append(Paragraph(item, self.styles['CustomBody']))
        
        elements.append(Spacer(1, 0.2*inch))
        
        # Recommendations
        elements.append(Paragraph("Recommendations", self.styles['CustomHeading']))
        
        recommendations = []
        if dashboard_data.get('statistics', {}).get('missing_values', 0) > 0:
            recommendations.append("• Address missing values through imputation or removal")
        
        if dashboard_data.get('statistics', {}).get('duplicate_rows', 0) > 0:
            recommendations.append("• Review and remove duplicate records")
        
        if quality_score < 80:
            recommendations.append("• Consider additional data cleaning and transformation")
        
        if not recommendations:
            recommendations.append("• Dataset is ready for advanced analytics")
        
        for rec in recommendations:
            elements.append(Paragraph(rec, self.styles['CustomBody']))
        
        # Footer
        elements.append(Spacer(1, 0.3*inch))
        footer_text = "This report was automatically generated by the Advanced Analytics Platform"
        footer = Paragraph(footer_text, self.styles['Normal'])
        elements.append(footer)
        
        # Build PDF
        doc.build(elements)
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()
    
    def generate_chart_image(self, chart_type, data, width=6, height=4):
        """
        Generate chart as image bytes
        
        Args:
            chart_type (str): Type of chart (bar, pie, line, etc.)
            data (dict): Data for the chart
            width (int): Chart width in inches
            height (int): Chart height in inches
        
        Returns:
            bytes: PNG image bytes
        """
        plt.figure(figsize=(width, height), dpi=100)
        
        if chart_type == 'bar':
            labels = data.get('labels', [])
            values = data.get('values', [])
            plt.bar(labels, values, color=colors.HexColor('#2563eb'))
            plt.ylabel('Count')
        
        elif chart_type == 'pie':
            labels = data.get('labels', [])
            values = data.get('values', [])
            plt.pie(values, labels=labels, autopct='%1.1f%%')
        
        elif chart_type == 'line':
            labels = data.get('labels', [])
            values = data.get('values', [])
            plt.plot(labels, values, marker='o', color='#2563eb')
            plt.ylabel('Value')
        
        plt.tight_layout()
        
        # Save to bytes buffer
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        plt.close()
        
        return buffer.getvalue()
