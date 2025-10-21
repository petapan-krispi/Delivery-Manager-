"""
Web-compatible delivery slip printing utilities.
Generates PDFs for delivery slips and customer tables.
"""

import io
from datetime import datetime
from typing import List
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from models.customer import Customer


class DeliverySlipPrinter:
    """Handles PDF generation of delivery slips and customer tables for web app."""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom paragraph styles for the PDFs."""
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1,  # Center alignment
            textColor=colors.darkblue
        )
        
        # Section header style
        self.section_style = ParagraphStyle(
            'CustomSection',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        # Normal text style
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=6
        )
    
    def create_delivery_slip_pdf(self, customer: Customer) -> bytes:
        """Create a PDF delivery slip for a customer (SCH DEL removed)."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # Title
        story.append(Paragraph("DELIVERY SLIP", self.title_style))
        story.append(Spacer(1, 20))
        
        # Generation date
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        story.append(Paragraph(f"Generated: {current_datetime}", self.normal_style))
        story.append(Spacer(1, 20))
        
        # Customer Information Section
        story.append(Paragraph("CUSTOMER INFORMATION", self.section_style))
        
        # Customer details table (SCH DEL removed)
        customer_data = [
            ['Name:', customer.customer_name],
            ['Phone:', customer.phone],
            ['Address:', f"{customer.address}{', Apt ' + customer.apartment_no if customer.apartment_no and customer.apartment_no.strip() else ''}"],
            ['Location:', f"{customer.suburb}{' | Postal Code: ' + customer.postal_code if customer.postal_code and customer.postal_code.strip() else ''}"]
        ]
        
        customer_table = Table(customer_data, colWidths=[2*inch, 4*inch])
        customer_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(customer_table)
        story.append(Spacer(1, 20))
        
        # Delivery Instructions Section
        story.append(Paragraph("DELIVERY INSTRUCTIONS", self.section_style))
        story.append(Paragraph("_________________________________________________", self.normal_style))
        story.append(Paragraph("_________________________________________________", self.normal_style))
        story.append(Paragraph("_________________________________________________", self.normal_style))
        story.append(Paragraph("_________________________________________________", self.normal_style))
        story.append(Spacer(1, 30))
        
        # Footer
        story.append(Paragraph("Thank you for choosing our delivery service!", self.normal_style))
        story.append(Paragraph("For questions, contact: support@deliverymanager.com", self.normal_style))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def create_customer_table_pdf(self, customers: list, search_query: str = "") -> bytes:
        """Create a PDF with customer table (SCH DEL removed)."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # Title
        story.append(Paragraph("CUSTOMER LIST", self.title_style))
        story.append(Spacer(1, 10))
        
        # Generation info
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        story.append(Paragraph(f"Generated: {current_datetime}", self.normal_style))
        
        if search_query:
            story.append(Paragraph(f"Search Query: \"{search_query}\"", self.normal_style))
        
        story.append(Spacer(1, 20))
        
        # Customer table
        if customers:
            # Table headers (SCH DEL removed)
            headers = ['#', 'Phone', 'Customer Name', 'Apt No', 'Address', 'Suburb', 'Postal Code']
            
            # Table data
            table_data = [headers]
            for i, customer in enumerate(customers, 1):
                row = [
                    str(i),
                    customer.phone,
                    customer.customer_name,
                    customer.apartment_no or '',
                    customer.address,
                    customer.suburb,
                    customer.postal_code
                ]
                table_data.append(row)
            
            # Create table
            customer_table = Table(table_data, colWidths=[0.5*inch, 1.2*inch, 2*inch, 0.8*inch, 2.5*inch, 1.2*inch, 0.8*inch])
            customer_table.setStyle(TableStyle([
                # Header row
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                
                # Data rows
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            
            story.append(customer_table)
            story.append(Spacer(1, 20))
            
            # Summary
            story.append(Paragraph(f"Total Customers: {len(customers)}", self.normal_style))
        else:
            story.append(Paragraph("No customers found.", self.normal_style))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def get_delivery_slip_filename(self, customer: Customer) -> str:
        """Get filename for delivery slip PDF."""
        safe_name = customer.customer_name.replace(' ', '_').replace('/', '_')
        return f"delivery_slip_{safe_name}.pdf"
    
    def get_customer_table_filename(self, search_query: str = "") -> str:
        """Get filename for customer table PDF."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        query_part = f"_{search_query.replace(' ', '_')}" if search_query else ""
        return f"customer_table{query_part}_{timestamp}.pdf"
    
    def create_batch_delivery_slip_pdf(self, customers: List[Customer]) -> bytes:
        """Create a PDF with delivery slips for multiple customers (SCH DEL removed)."""
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch)
            story = []
            
            # Add title
            title = Paragraph("Selected Customers Delivery Report", self.title_style)
            story.append(title)
            story.append(Spacer(1, 12))
            
            # Add timestamp
            timestamp = Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", self.normal_style)
            story.append(timestamp)
            story.append(Spacer(1, 20))
            
            # Create table data (SCH DEL removed)
            table_data = [['Phone', 'Customer Name', 'Apt No', 'Address', 'Suburb', 'Postal Code']]
            
            for customer in customers:
                table_data.append([
                    customer.phone,
                    customer.customer_name,
                    customer.apartment_no or '',
                    customer.address,
                    customer.suburb,
                    customer.postal_code
                ])
            
            # Create table
            table = Table(table_data, colWidths=[1.2*inch, 1.8*inch, 0.7*inch, 2.2*inch, 1.2*inch, 0.9*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            story.append(table)
            
            # Build PDF
            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            print(f"Error creating batch delivery slip PDF: {e}")
            return b""