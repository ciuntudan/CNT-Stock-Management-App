from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os

class InvoiceGenerator:
    def __init__(self, invoice_data):
        """
        Initialize the invoice generator with invoice data.
        
        invoice_data should be a dictionary containing:
        - issuer (company details)
        - customer (customer details)
        - items (list of items)
        - invoice_number
        - invoice_series
        - invoice_date
        """
        self.data = invoice_data
        self.styles = getSampleStyleSheet()
        self.setup_styles()
    
    def setup_styles(self):
        """Set up custom styles for the invoice"""
        self.styles.add(ParagraphStyle(
            name='RightAlign',
            parent=self.styles['Normal'],
            alignment=2  # right alignment
        ))
        
        self.styles.add(ParagraphStyle(
            name='CenterAlign',
            parent=self.styles['Normal'],
            alignment=1  # center alignment
        ))
    
    def format_currency(self, amount):
        """Format currency values with RON suffix"""
        return f"{amount:,.2f} RON".replace(",", " ")
    
    def generate(self, output_path):
        """Generate the invoice PDF"""
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=1.5*cm,
            bottomMargin=1.5*cm
        )
        
        elements = []
        
        # Add header
        elements.extend(self.create_header())
        elements.append(Spacer(1, 20))
        
        # Add company details
        elements.extend(self.create_company_section())
        elements.append(Spacer(1, 20))
        
        # Add items table
        elements.extend(self.create_items_table())
        elements.append(Spacer(1, 30))
        
        # Add footer
        elements.extend(self.create_footer())
        
        # Build the document
        doc.build(elements)
        return output_path
    
    def create_header(self):
        """Create the invoice header section"""
        elements = []
        
        # Invoice title and number
        header_data = [
            [Paragraph("<b>FACTURĂ FISCALĂ</b>", self.styles['Heading1']), ""],
            [
                f"Seria {self.data['invoice_series']} Nr. {self.data['invoice_number']:04d}",
                f"Data: {self.data['invoice_date'].strftime('%d.%m.%Y')}"
            ],
        ]
        
        header_table = Table(header_data, colWidths=[10*cm]*2)
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        
        elements.append(header_table)
        return elements
    
    def create_company_section(self):
        """Create the company details section"""
        elements = []
        
        company_data = [
            ["Furnizor:", "Client:"],
            [
                Paragraph(f"""
                <b>{self.data['issuer'].name}</b><br/>
                CUI: {self.data['issuer'].registration_number or ''}<br/>
                Nr. Reg. Com.: {self.data['issuer'].vat_number or ''}<br/>
                Adresa: {self.data['issuer'].address or ''}<br/>
                Banca: {self.data['issuer'].bank_name or ''}<br/>
                IBAN: {self.data['issuer'].bank_account or ''}<br/>
                Tel: {self.data['issuer'].phone or ''}<br/>
                Email: {self.data['issuer'].email or ''}
                """, self.styles['Normal']),
                
                Paragraph(f"""
                <b>{self.data['customer'].name}</b><br/>
                {'Companie: ' + self.data['customer'].company_name + '<br/>' if self.data['customer'].company_name else ''}
                Adresa: {self.data['customer'].address or ''}<br/>
                Tel: {self.data['customer'].phone or ''}<br/>
                Email: {self.data['customer'].email or ''}
                """, self.styles['Normal'])
            ]
        ]
        
        company_table = Table(company_data, colWidths=[10*cm]*2)
        company_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 1), (-1, 1), 0),
        ]))
        
        elements.append(company_table)
        return elements
    
    def create_items_table(self):
        """Create the items table section"""
        elements = []
        
        # Table header
        items_data = [
            ['Nr.', 'Denumire Produs/Serviciu', 'U.M.', 'Cant.', 'Preț Unitar', 'Valoare', 'TVA']
        ]
        
        # Add items
        subtotal = 0
        for idx, item in enumerate(self.data['items'], 1):
            item_subtotal = item.quantity * item.unit_price
            item_vat = item_subtotal * 0.19  # 19% VAT
            subtotal += item_subtotal
            
            items_data.append([
                str(idx),
                item.description,
                item.product.measure_unit.value if item.product else 'buc',
                f"{item.quantity:g}",
                self.format_currency(item.unit_price),
                self.format_currency(item_subtotal),
                self.format_currency(item_vat)
            ])
        
        # Calculate totals
        vat = subtotal * 0.19
        total = subtotal + vat
        
        # Add totals rows
        items_data.extend([
            ['', '', '', '', 'Subtotal:', self.format_currency(subtotal), ''],
            ['', '', '', '', 'Total TVA:', self.format_currency(vat), ''],
            ['', '', '', '', 'Total de plată:', self.format_currency(total), ''],
        ])
        
        # Set column widths
        col_widths = [
            2*cm,   # Nr
            8*cm,   # Denumire
            2*cm,   # UM
            2*cm,   # Cant
            3*cm,   # Pret unitar
            3*cm,   # Valoare
            3*cm,   # TVA
        ]
        
        # Create and style the table
        items_table = Table(items_data, colWidths=col_widths)
        items_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Nr. column
            ('ALIGN', (2, 1), (2, -4), 'CENTER'),  # U.M. column
            ('ALIGN', (3, 1), (3, -4), 'RIGHT'),   # Cant. column
            ('ALIGN', (4, 1), (-1, -1), 'RIGHT'),  # Amount columns
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -4), 0.5, colors.black),
            ('LINEABOVE', (4, -3), (-1, -3), 0.5, colors.black),  # Line above subtotal
            ('LINEABOVE', (4, -1), (-1, -1), 1, colors.black),    # Double line above total
            ('LINEBELOW', (4, -1), (-1, -1), 1, colors.black),
            ('FONTNAME', (4, -3), (4, -1), 'Helvetica-Bold'),     # Bold labels for totals
        ]))
        
        elements.append(items_table)
        return elements
    
    def create_footer(self):
        """Create the footer section"""
        elements = []
        
        footer_data = [
            ['Întocmit de:', 'Delegat:', 'Semnătură și ștampilă:'],
            ['', '', ''],
            ['', '', ''],
        ]
        
        footer_table = Table(footer_data, colWidths=[7*cm]*3)
        footer_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 20),
        ]))
        
        elements.append(footer_table)
        return elements 