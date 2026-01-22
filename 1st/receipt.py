"""
Receipt generation module for Hotel Room Billing System
Generates professional PDF receipts using reportlab
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import os
import subprocess
import platform
import html


class ReceiptGenerator:
    def __init__(self):
        """Initialize receipt generator"""
        self.hotel_name = "CAPITAL 409"
        self.address = "Megha Road, Abhanpur, Chhattisgarh, India"
        self.gstin = "22IOLPS6709M1Z6"
        self.phone = "+91 74149 83156"
    
    def generate_receipt(self, bill_data, output_path='receipts'):
        """
        Generate PDF receipt for the bill
        
        Args:
            bill_data: Dictionary containing bill information
            output_path: Directory to save receipts
        """
        # Create receipts directory if it doesn't exist
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        # Generate filename
        filename = f"{bill_data['bill_no']}.pdf"
        filepath = os.path.join(output_path, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(filepath, pagesize=letter,
                               rightMargin=0.75*inch, leftMargin=0.75*inch,
                               topMargin=0.75*inch, bottomMargin=0.75*inch)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#333333'),
            alignment=TA_CENTER,
            spaceAfter=3
        )
        
        info_style = ParagraphStyle(
            'CustomInfo',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#555555'),
            alignment=TA_LEFT
        )
        
        # Hotel Header
        elements.append(Paragraph(self.hotel_name, title_style))
        elements.append(Spacer(1, 0.1*inch))
        
        elements.append(Paragraph(self.address, header_style))
        elements.append(Paragraph(f"GSTIN: {self.gstin}", header_style))
        elements.append(Paragraph(f"Phone: {self.phone}", header_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Receipt Number and Date
        receipt_date = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        receipt_info = [
            [Paragraph(f"<b>Receipt No:</b> {bill_data['bill_no']}", info_style),
             Paragraph(f"<b>Date & Time:</b> {receipt_date}", info_style)]
        ]
        receipt_table = Table(receipt_info, colWidths=[3.5*inch, 3.5*inch])
        receipt_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(receipt_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Line separator
        elements.append(Paragraph("_" * 80, styles['Normal']))
        elements.append(Spacer(1, 0.15*inch))
        
        # Guest Information (escape HTML special characters)
        guest_name_escaped = html.escape(str(bill_data['guest_name']))
        room_number_escaped = html.escape(str(bill_data['room_number']))
        checkin_date_escaped = html.escape(str(bill_data['check_in_date']))
        checkout_date_escaped = html.escape(str(bill_data.get('checkout_date', '')))
        
        guest_info = [
            [Paragraph("<b>Guest Name:</b>", info_style),
             Paragraph(guest_name_escaped, info_style)],
            [Paragraph("<b>Room Number:</b>", info_style),
             Paragraph(f"Room {room_number_escaped}", info_style)],
            [Paragraph("<b>Check-in Date:</b>", info_style),
             Paragraph(checkin_date_escaped, info_style)],
            [Paragraph("<b>Check-out Date:</b>", info_style),
             Paragraph(checkout_date_escaped, info_style)],
        ]
        guest_table = Table(guest_info, colWidths=[2*inch, 5*inch])
        guest_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(guest_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Billing Details Table
        # Use 'nights' if available, otherwise fall back to 'days' for backward compatibility
        nights = bill_data.get('nights', bill_data.get('days', 1))
        billing_data = [
            ['Description', 'Quantity', 'Rate', 'Amount'],
            ['Room Charges', f"{nights} Nights", 
             f"Rs{bill_data['rate']:.2f}", f"Rs{bill_data['subtotal']:.2f}"],
        ]
        
        billing_table = Table(billing_data, colWidths=[3*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        billing_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 10),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(billing_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Tax and Total Section
        tax_data = [
            ['Subtotal:', f"Rs{bill_data['subtotal']:.2f}"],
            ['CGST (9%):', f"Rs{bill_data['cgst']:.2f}"],
            ['SGST (9%):', f"Rs{bill_data['sgst']:.2f}"],
            ['TOTAL AMOUNT:', f"Rs{bill_data['total']:.2f}"],
        ]
        
        tax_table = Table(tax_data, colWidths=[5*inch, 2*inch])
        tax_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (0, -2), 10),
            ('FONTSIZE', (1, 0), (1, -2), 10),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('FONTSIZE', (1, -1), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#c0392b')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(tax_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Footer
        footer_style = ParagraphStyle(
            'CustomFooter',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_CENTER,
            spaceAfter=6,
            fontName='Helvetica-Bold'
        )
        
        elements.append(Paragraph("Thank you for staying with us!", footer_style))
        elements.append(Paragraph("Visit Again", footer_style))
        elements.append(Spacer(1, 0.1*inch))
        
        # Build PDF
        doc.build(elements)
        
        return filepath
    
    def open_pdf(self, filepath):
        """Open PDF file using system default application"""
        try:
            if platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', filepath])
            elif platform.system() == 'Windows':
                os.startfile(filepath)
            else:  # Linux
                subprocess.call(['xdg-open', filepath])
        except Exception as e:
            print(f"Error opening PDF: {e}")
    
    def print_pdf(self, filepath):
        """Print PDF using system print command"""
        try:
            if platform.system() == 'Darwin':  # macOS
                subprocess.call(['lpr', filepath])
            elif platform.system() == 'Windows':
                os.startfile(filepath, 'print')
            else:  # Linux
                subprocess.call(['lpr', filepath])
        except Exception as e:
            print(f"Error printing PDF: {e}")

