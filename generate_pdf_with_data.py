#!/usr/bin/env python3
"""Generate PDF with real contract data"""

import os
import sys
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'clm_backend.settings'
django.setup()

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from datetime import datetime

from contracts.models import ESignatureContract, SigningAuditLog

def generate_signed_pdf():
    """Generate PDF with actual contract data"""
    
    # Get contract from database
    try:
        contract = ESignatureContract.objects.get(id='aae65358-f709-4994-ab28-f4e2874c35e3')
    except ESignatureContract.DoesNotExist:
        print("Contract not found")
        return False
    
    # Create PDF
    pdf_file = '/Users/vishaljha/CLM_Backend/signed_nda.pdf'
    doc = SimpleDocTemplate(pdf_file, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=30,
        alignment=1  # Center
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    normal_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=11,
        leading=14,
        spaceAfter=6
    )
    
    # Title
    story.append(Paragraph("✓ SIGNED NDA CONTRACT", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Contract Info Section
    story.append(Paragraph("Contract Information", heading_style))
    
    contract_data = [
        ['Field', 'Value'],
        ['Contract ID', str(contract.id)],
        ['Title', contract.title or 'N/A'],
        ['Status', contract.status.upper()],
        ['Version', str(contract.current_version)],
        ['Created Date', contract.created_at.strftime('%B %d, %Y %H:%M:%S UTC') if contract.created_at else 'N/A'],
        ['Completed Date', contract.completed_at.strftime('%B %d, %Y %H:%M:%S UTC') if contract.completed_at else 'N/A'],
    ]
    
    contract_table = Table(contract_data, colWidths=[2*inch, 4*inch])
    contract_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    
    story.append(contract_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Signers Section
    story.append(Paragraph("Signatories", heading_style))
    
    signers = list(contract.signers.all())
    if signers:
        signer_data = [['Email', 'Status', 'Signed Date']]
        for signer in signers:
            signer_data.append([
                signer.email,
                signer.status.upper(),
                signer.signed_at.strftime('%B %d, %Y %H:%M:%S UTC') if signer.signed_at else 'Pending'
            ])
        
        signer_table = Table(signer_data, colWidths=[2.5*inch, 1.5*inch, 2*inch])
        signer_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgreen]),
        ]))
        story.append(signer_table)
    
    story.append(Spacer(1, 0.3*inch))
    
    # Audit Trail Section
    story.append(Paragraph("Signature Audit Trail", heading_style))
    
    logs = list(SigningAuditLog.objects.filter(esignature_contract=contract).order_by('created_at'))
    if logs:
        audit_data = [['Event', 'Message', 'Status', 'Timestamp']]
        for log in logs:
            audit_data.append([
                log.event.replace('_', ' ').title(),
                log.message,
                log.new_status.upper() if log.new_status else 'N/A',
                log.created_at.strftime('%H:%M:%S UTC')
            ])
        
        audit_table = Table(audit_data, colWidths=[1.3*inch, 2*inch, 1*inch, 1.7*inch])
        audit_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7c3aed')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lavender),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lavender]),
        ]))
        story.append(audit_table)
    
    story.append(Spacer(1, 0.3*inch))
    
    # Footer
    story.append(Paragraph(
        f"<i>This is a digitally signed contract. Generated on {datetime.now().strftime('%B %d, %Y at %H:%M:%S UTC')}</i>",
        normal_style
    ))
    
    # Build PDF
    try:
        doc.build(story)
        print(f"✅ PDF Generated Successfully: {pdf_file}")
        print(f"   Size: {os.path.getsize(pdf_file)} bytes")
        return True
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        return False

if __name__ == '__main__':
    generate_signed_pdf()
