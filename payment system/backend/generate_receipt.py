import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register Arabic font (make sure 'arial.ttf' supports Arabic characters)
pdfmetrics.registerFont(TTFont('Arabic', 'arial.ttf'))

def create_receipt(transaction_id, sender, sender_governorate, sender_location,
                   receiver, receiver_governorate, receiver_location, amount, currency,
                   employee_name, branch_governorate):
    """Generate Arabic-style receipt with RTL support and optimized layout"""
    
    # Create output directory once
    os.makedirs("receipts", exist_ok=True)
    filename = f"receipts/receipt_{transaction_id}.pdf"

    # Initialize canvas with optimized settings
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    right_margin = width - 50  # RTL alignment
    
    # Set global font and direction
    c.setFont('Arabic', 12)
    c._doc.setLanguage('ar')  # Set document language to Arabic

    # ----------------------
    # Helper functions
    # ----------------------
    def draw_rtl_text(y, text, font_size=12, is_bold=False):
        """Draw right-aligned text with font styling"""
        font_name = 'Arabic-Bold' if is_bold else 'Arabic'
        c.setFont(font_name, font_size)
        text_width = c.stringWidth(text, font_name, font_size)
        c.drawString(right_margin - text_width, y, text)

    def draw_section_header(y, title):
        """Draw section headers with consistent styling"""
        c.setFillColor(colors.darkblue)
        draw_rtl_text(y, title, 14, is_bold=True)
        c.setFillColor(colors.black)
        return y - 25

    # ----------------------
    # Main content
    # ----------------------
    
    # Border and header
    c.setStrokeColor(colors.darkblue)
    c.setLineWidth(2)
    c.rect(30, 30, width-60, height-60)
    
    # Title with Arabic text
    draw_rtl_text(height-50, "إيصال تحويل أموال", 18, is_bold=True)
    
    # Transaction info
    y_position = height - 100
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    draw_rtl_text(y_position, f"رقم المعاملة: {transaction_id}")
    y_position -= 25
    draw_rtl_text(y_position, f"التاريخ والوقت: {current_date}")
    y_position -= 35

    # Sender information
    y_position = draw_section_header(y_position, "معلومات المرسل")
    y_position = draw_detail_lines(y_position, [
        f"الاسم: {sender}",
        f"المحافظة: {sender_governorate}",
        f"الموقع: {sender_location}"
    ])

    # Receiver information
    y_position = draw_section_header(y_position, "معلومات المستلم")
    y_position = draw_detail_lines(y_position, [
        f"الاسم: {receiver}",
        f"المحافظة: {receiver_governorate}",
        f"الموقع: {receiver_location}"
    ])

    # Transaction details
    y_position = draw_section_header(y_position, "تفاصيل المعاملة")
    y_position = draw_detail_lines(y_position, [
        f"المبلغ: {amount} {currency}",
        f"الموظف: {employee_name}",
        f"محافظة الفرع: {branch_governorate}"
    ])

    # Signature and footer
    draw_rtl_text(60, "التوقيع: ____________________", is_bold=True)
    draw_rtl_text(40, "هذا إيصال رسمي من نظام التحويلات المالية", 8)

    c.save()
    return filename

def draw_detail_lines(y, lines):
    """Draw multiple detail lines with consistent spacing"""
    for line in lines:
        draw_rtl_text(y, line)
        y -= 20
    return y - 10  # Extra spacing after section