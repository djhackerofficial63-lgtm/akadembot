from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
from datetime import datetime
from pathlib import Path
import qrcode
import logging
import os

logger = logging.getLogger(__name__)

class DocumentGenerator:
    """Generate documents with different styles"""
    
    def __init__(self):
        self.output_dir = Path("documents")
        self.output_dir.mkdir(exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for different templates"""
        
        # APA Style
        self.styles.add(ParagraphStyle(
            name='APA_Title',
            parent=self.styles['Heading1'],
            fontSize=14,
            bold=True,
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='APA_Author',
            parent=self.styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER,
            spaceAfter=24,
            fontName='Helvetica'
        ))
        
        self.styles.add(ParagraphStyle(
            name='APA_Body',
            parent=self.styles['Normal'],
            fontSize=12,
            leading=24,
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            fontName='Helvetica',
            firstLineIndent=36
        ))
        
        # Harvard Style
        self.styles.add(ParagraphStyle(
            name='Harvard_Title',
            parent=self.styles['Heading1'],
            fontSize=16,
            bold=True,
            spaceAfter=18,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='Harvard_Body',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=22,
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            fontName='Helvetica'
        ))
        
        # Uzbek Style
        self.styles.add(ParagraphStyle(
            name='Uzbek_Title',
            parent=self.styles['Heading1'],
            fontSize=14,
            bold=True,
            spaceAfter=14,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='Uzbek_Body',
            parent=self.styles['Normal'],
            fontSize=12,
            leading=24,
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            fontName='Helvetica'
        ))
    
    def _generate_qr_code(self, data, filename):
        """Generate QR code image"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=2,
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(filename)
            return filename
        except Exception as e:
            logger.error(f"Error generating QR code: {e}")
            return None
    
    def generate_document(self, doc_type, style, title, content, user_id):
        """Generate document based on type and style"""
        
        try:
            # Create filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.output_dir}/{user_id}_{doc_type}_{timestamp}.pdf"
            
            # Create PDF
            doc = SimpleDocTemplate(
                filename,
                pagesize=A4,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=1*inch,
                bottomMargin=0.75*inch
            )
            
            # Content list
            story = []
            
            # Generate content based on style
            if style == "apa":
                story = self._generate_apa_style(title, content, user_id)
            elif style == "harvard":
                story = self._generate_harvard_style(title, content, user_id)
            elif style == "uzbek":
                story = self._generate_uzbek_style(title, content, user_id)
            else:
                story = self._generate_default_style(title, content, user_id)
            
            # Build PDF
            doc.build(story)
            logger.info(f"✅ Document generated: {filename}")
            
            return filename
        
        except Exception as e:
            logger.error(f"Error generating document: {e}")
            return None
    
    def _generate_apa_style(self, title, content, user_id):
        """Generate APA style document"""
        story = []
        
        # Title (centered, double-spaced)
        story.append(Paragraph(title, self.styles['APA_Title']))
        story.append(Spacer(1, 0.5*inch))
        
        # Author/Date
        author_date = f"Prepared on {datetime.now().strftime('%B %d, %Y')}"
        story.append(Paragraph(author_date, self.styles['APA_Author']))
        
        # Content
        paragraphs = content.split('\n\n')
        for para in paragraphs:
            if para.strip():
                story.append(Paragraph(para.strip(), self.styles['APA_Body']))
                story.append(Spacer(1, 0.2*inch))
        
        # QR Code
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph("Document Information", self.styles['Heading3']))
        
        qr_file = f"{self.output_dir}/qr_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        self._generate_qr_code(f"User: {user_id}, Generated: {datetime.now()}", qr_file)
        
        if os.path.exists(qr_file):
            story.append(Image(qr_file, width=1*inch, height=1*inch))
        
        return story
    
    def _generate_harvard_style(self, title, content, user_id):
        """Generate Harvard style document"""
        story = []
        
        # Title
        story.append(Paragraph(title, self.styles['Harvard_Title']))
        story.append(Spacer(1, 0.3*inch))
        
        # Content
        paragraphs = content.split('\n\n')
        for para in paragraphs:
            if para.strip():
                story.append(Paragraph(para.strip(), self.styles['Harvard_Body']))
                story.append(Spacer(1, 0.2*inch))
        
        # References section
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph("References", self.styles['Heading2']))
        story.append(Paragraph(f"Generated on {datetime.now().strftime('%d %B %Y')}", self.styles['Normal']))
        
        # QR Code
        story.append(Spacer(1, 0.5*inch))
        qr_file = f"{self.output_dir}/qr_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        self._generate_qr_code(f"User: {user_id}, Generated: {datetime.now()}", qr_file)
        
        if os.path.exists(qr_file):
            story.append(Image(qr_file, width=1*inch, height=1*inch))
        
        return story
    
    def _generate_uzbek_style(self, title, content, user_id):
        """Generate Uzbek style document"""
        story = []
        
        # Header
        header_data = [
            ["DAVLAT STANDARTLARI BO'YICHA YARATILGAN HUJJAT"],
        ]
        header_table = Table(header_data, colWidths=[7*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Title
        story.append(Paragraph(title, self.styles['Uzbek_Title']))
        story.append(Spacer(1, 0.3*inch))
        
        # Content
        paragraphs = content.split('\n\n')
        for para in paragraphs:
            if para.strip():
                story.append(Paragraph(para.strip(), self.styles['Uzbek_Body']))
                story.append(Spacer(1, 0.2*inch))
        
        # Footer
        story.append(Spacer(1, 0.5*inch))
        footer_data = [
            [f"Yaratilgan sana: {datetime.now().strftime('%d.%m.%Y')}"],
            [f"Foydalanuvchi ID: {user_id}"],
        ]
        footer_table = Table(footer_data, colWidths=[7*inch])
        footer_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(footer_table)
        
        # QR Code
        story.append(Spacer(1, 0.3*inch))
        qr_file = f"{self.output_dir}/qr_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        self._generate_qr_code(f"Foydalanuvchi: {user_id}, Vaqti: {datetime.now()}", qr_file)
        
        if os.path.exists(qr_file):
            story.append(Image(qr_file, width=1*inch, height=1*inch))
        
        return story
    
    def _generate_default_style(self, title, content, user_id):
        """Generate default style document"""
        story = []
        
        story.append(Paragraph(title, self.styles['Heading1']))
        story.append(Spacer(1, 0.3*inch))
        
        paragraphs = content.split('\n\n')
        for para in paragraphs:
            if para.strip():
                story.append(Paragraph(para.strip(), self.styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
        
        return story
