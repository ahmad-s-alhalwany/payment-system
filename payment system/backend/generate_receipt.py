import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Image
from reportlab.lib.units import inch
from reportlab.lib import colors

def create_receipt(transaction_id, sender, sender_governorate, sender_location,
                   receiver, receiver_governorate, receiver_location, amount, currency,
                   employee_name, branch_governorate):
    os.makedirs("receipts", exist_ok=True)
    filename = f"receipts/receipt_{transaction_id}.pdf"

    # Create a canvas
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Add a border
    c.setStrokeColor(colors.darkblue)
    c.setLineWidth(2)
    c.rect(30, 30, width-60, height-60, stroke=1, fill=0)
    
    # Add a header
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(colors.darkblue)
    c.drawCentredString(width/2, height-50, "Payment System Receipt")
    
    # Add a line under the header
    c.setStrokeColor(colors.darkblue)
    c.line(50, height-60, width-50, height-60)
    
    # Add transaction details
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.black)
    
    # Current date and time
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Transaction information
    y_position = height - 100
    line_height = 20
    
    c.drawString(50, y_position, f"Transaction ID: {transaction_id}")
    y_position -= line_height
    c.drawString(50, y_position, f"Date: {current_time}")
    y_position -= line_height * 1.5
    
    # Sender information
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_position, "Sender Information")
    y_position -= line_height
    c.setFont("Helvetica", 12)
    c.drawString(70, y_position, f"Name: {sender}")
    y_position -= line_height
    c.drawString(70, y_position, f"Mobile: {sender_mobile if 'sender_mobile' in locals() else 'N/A'}")
    y_position -= line_height
    c.drawString(70, y_position, f"Governorate: {sender_governorate}")
    y_position -= line_height
    c.drawString(70, y_position, f"Location: {sender_location}")
    y_position -= line_height * 1.5
    
    # Receiver information
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_position, "Receiver Information")
    y_position -= line_height
    c.setFont("Helvetica", 12)
    c.drawString(70, y_position, f"Name: {receiver}")
    y_position -= line_height
    c.drawString(70, y_position, f"Mobile: {receiver_mobile if 'receiver_mobile' in locals() else 'N/A'}")
    y_position -= line_height
    c.drawString(70, y_position, f"Governorate: {receiver_governorate}")
    y_position -= line_height
    c.drawString(70, y_position, f"Location: {receiver_location}")
    y_position -= line_height * 1.5
    
    # Transaction details
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_position, "Transaction Details")
    y_position -= line_height
    c.setFont("Helvetica", 12)
    c.drawString(70, y_position, f"Amount: {amount} {currency}")
    y_position -= line_height
    c.drawString(70, y_position, f"Employee: {employee_name}")
    y_position -= line_height
    c.drawString(70, y_position, f"Branch Governorate: {branch_governorate}")
    y_position -= line_height * 2
    
    # Signature
    c.drawString(50, y_position, "Signature: ____________________")
    
    # Add a footer
    c.setFont("Helvetica", 8)  # Changed from Helvetica-Italic to Helvetica
    c.drawCentredString(width/2, 40, "This is an official receipt from the Payment System")
    
    c.save()
    return filename
