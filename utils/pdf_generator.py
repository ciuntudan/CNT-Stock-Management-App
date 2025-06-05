from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Frame
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime

def format_currency(amount):
    return f"{amount:.2f}"  # Just the number with 2 decimals

def generate_invoice_pdf(invoice, output_path):
    # Set up the document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=15*mm,
        leftMargin=15*mm,
        topMargin=15*mm,
        bottomMargin=15*mm
    )
    
    elements = []
    
    # Header section with company details and title
    header_left = [
        ["S.C. ANDY-M COPY CENTER S.R.L."],
        ["Sediu: N. Romanescu, nr. 145, Loc. Rozovu, Jud."],
        ["Neamt, Romania"],
        ["CIF: RO 41118934"],
        ["Nr Reg Com: J27/637/2019"],
        ["Banca: TREZORERIE"],
        ["Cont: RO73TREZ4945069XXX017205"],
        ["TVA la Incasare"]
    ]
    
    header_right = [
        ["Cumparator: " + invoice.customer.name],
        ["Sediu: " + (invoice.customer.address or "")],
        ["CIF: " + (invoice.customer.registration_number or "")],
        ["Nr Reg Com: " + (invoice.customer.trade_register_number or "")],
        ["Cont: " + (invoice.customer.bank_account or "")],
        ["Banca: " + (invoice.customer.bank_name or "")]
    ]
    
    # Create the header table
    header_data = []
    max_rows = max(len(header_left), len(header_right))
    for i in range(max_rows):
        row = []
        row.extend(header_left[i] if i < len(header_left) else [""])
        row.extend(header_right[i] if i < len(header_right) else [""])
        header_data.append(row)
    
    header_table = Table(header_data, colWidths=[doc.width/2, doc.width/2])
    header_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('LEADING', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(header_table)
    
    # FACTURA title and details in a box
    title_data = [
        ["FACTURA"],
        [f"Serie: {invoice.series}"],
        [f"Numar: {invoice.number}"],
        [f"Data: {invoice.date.strftime('%d-%m-%Y')}"]
    ]
    
    title_table = Table(title_data, colWidths=[60*mm])
    title_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (0, 0), 12),  # Title larger
        ('FONTSIZE', (0, 1), (-1, -1), 8),  # Details smaller
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
    ]))
    
    # Position the title box in the center top
    title_position = [
        [None, title_table, None],
    ]
    title_position_table = Table(title_position, colWidths=[doc.width/3]*3)
    elements.append(title_position_table)
    elements.append(Spacer(1, 5*mm))
    
    # Items table
    items_data = [
        ['Nr.\nCrt.', 'Denumirea produselor sau serviciilor', 'U.M.', 'Canti-\ntatea', 'Pretul unitar\n(fara TVA)\n-LEI-', 'Valoarea\n-LEI-', 'Cota\nTVA', 'Valoarea TVA\n-LEI-']
    ]
    
    for idx, item in enumerate(invoice.items, 1):
        subtotal = item.quantity * item.unit_price
        vat = subtotal * (item.vat_rate / 100) if item.vat_rate > 0 else 0
        vat_text = "SCUTIT" if item.vat_rate == 0 else f"{item.vat_rate}%"
        
        items_data.append([
            str(idx),
            item.description,
            'BUC',
            str(int(item.quantity)),
            format_currency(item.unit_price),
            format_currency(subtotal),
            vat_text,
            format_currency(vat) if vat > 0 else "0.00"
        ])
    
    # Calculate remaining space and add empty rows
    available_height = doc.height - 150*mm  # Approximate space taken by headers and footers
    row_height = 5*mm  # Approximate height per row
    max_rows = int(available_height / row_height)
    
    while len(items_data) < max_rows:
        items_data.append([''] * 8)
    
    col_widths = [
        15*mm,   # Nr. Crt
        70*mm,   # Denumire
        15*mm,   # U.M.
        20*mm,   # Cantitate
        25*mm,   # Pret unitar
        25*mm,   # Valoare
        15*mm,   # Cota TVA
        25*mm,   # Valoare TVA
    ]
    
    items_table = Table(items_data, colWidths=col_widths, repeatRows=1)
    items_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # Header alignment
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Nr. column
        ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # U.M. column
        ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),  # Numeric columns
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, 0), 0.5, colors.black),  # Only header has grid
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black),  # Border around entire table
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.black),  # Line below header
    ]))
    elements.append(items_table)
    
    # Footer with totals and signatures
    footer_left = [
        ['Semnatura si stampila'],
        ['furnizorului'],
        [''],
        [''],
    ]
    
    footer_middle = [
        ['Date privind expeditia'],
        ['Numele delegatului: CORESPONDENTA'],
        ['Buletinul / Cartea de identitate'],
        ['Seria .......... nr ............'],
        ['Mijlocul de transport ........... nr .........'],
        ['Expedierea s-a efectuat in prezenta noastra la'],
        ['data de ..................... ora .............'],
        ['Semnatura .....................................'],
    ]
    
    footer_right = [
        [f"Total: {format_currency(invoice.subtotal)}"],
        [f"Valoarea TVA: {format_currency(invoice.vat_amount)}"],
        [''],
        [f"Total de plata: {format_currency(invoice.total)} LEI"],
    ]
    
    # Create separate tables for each footer section
    footer_left_table = Table(footer_left)
    footer_middle_table = Table(footer_middle)
    footer_right_table = Table(footer_right)
    
    # Combine footer sections
    footer_data = [[footer_left_table, footer_middle_table, footer_right_table]]
    footer_table = Table(footer_data, colWidths=[doc.width/3]*3)
    footer_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    # Add signature area
    signature_data = [
        ['', 'Semnatura de primire', ''],
    ]
    signature_table = Table(signature_data, colWidths=[doc.width/3]*3)
    signature_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
    ]))
    
    elements.append(footer_table)
    elements.append(signature_table)
    
    # Build the document
    doc.build(elements)
    return output_path 