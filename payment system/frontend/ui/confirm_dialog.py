from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, 
                            QHBoxLayout, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

class ConfirmTransactionDialog(QDialog):
    """Modern confirmation dialog for money transfers with enhanced styling."""
    
    def __init__(self, parent, sender, sender_mobile, sender_governorate, sender_location,
                 receiver, receiver_mobile, receiver_governorate, receiver_location, 
                 amount, currency, message, employee_name, branch_governorate):
        super().__init__(parent)
        
        # Store transaction data
        self.transaction_data = {
            'sender': sender,
            'sender_mobile': sender_mobile,
            'sender_governorate': sender_governorate,
            'sender_location': sender_location,
            'receiver': receiver,
            'receiver_mobile': receiver_mobile,
            'receiver_governorate': receiver_governorate,
            'receiver_location': receiver_location,
            'amount': amount,
            'currency': currency,
            'message': message,
            'employee_name': employee_name,
            'branch_governorate': branch_governorate
        }
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the dialog UI with modern styling."""
        self.setWindowTitle("تأكيد التحويل")
        self.setFixedSize(500, 550)  # Fixed size for consistency
        
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("تأكيد تفاصيل التحويل")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Format amount with commas
        try:
            amount = float(self.transaction_data.get('amount', 0))
            formatted_amount = f"{amount:,.2f}"
        except (ValueError, TypeError):
            formatted_amount = "0.00"
        
        # Create info sections with modern styling
        sections = [
            {
                'title': "معلومات المرسل",
                'fields': [
                    ("الاسم", self.transaction_data.get('sender', '')),
                    ("رقم الهاتف", self.transaction_data.get('sender_mobile', '')),
                    ("المحافظة", self.transaction_data.get('sender_governorate', '')),
                    ("الموقع", self.transaction_data.get('sender_location', ''))
                ],
                'color': "#e74c3c"
            },
            {
                'title': "معلومات المستلم",
                'fields': [
                    ("الاسم", self.transaction_data.get('receiver', '')),
                    ("رقم الهاتف", self.transaction_data.get('receiver_mobile', '')),
                    ("المحافظة", self.transaction_data.get('receiver_governorate', '')),
                    ("الموقع", self.transaction_data.get('receiver_location', ''))
                ],
                'color': "#3498db"
            },
            {
                'title': "تفاصيل التحويل",
                'fields': [
                    ("المبلغ", f"{formatted_amount} {self.transaction_data.get('currency', '')}"),
                    ("الرسالة", self.transaction_data.get('message', 'لا توجد رسالة')),
                    ("اسم الموظف", self.transaction_data.get('employee_name', '')),
                    ("محافظة الفرع", self.transaction_data.get('branch_governorate', ''))
                ],
                'color': "#2ecc71"
            }
        ]
        
        # Add sections to layout
        for section in sections:
            section_group = self.create_section_group(section['title'], section['color'])
            section_layout = QVBoxLayout()
            section_layout.setSpacing(8)
            
            for field_name, field_value in section['fields']:
                field_layout = QHBoxLayout()
                
                name_label = QLabel(f"<b>{field_name}:</b>")
                name_label.setStyleSheet("color: #555;")
                name_label.setFixedWidth(100)
                
                value_label = QLabel(field_value)
                value_label.setStyleSheet("color: #333; font-weight: bold;")
                value_label.setWordWrap(True)
                
                field_layout.addWidget(name_label)
                field_layout.addWidget(value_label)
                section_layout.addLayout(field_layout)
            
            section_group.setLayout(section_layout)
            layout.addWidget(section_group)
        
        # Warning message
        warning_label = QLabel(
            "⚠️ تنبيه: بعد تأكيد التحويل، لا يمكن التراجع عنه. يرجى التأكد من صحة جميع المعلومات."
        )
        warning_label.setStyleSheet("""
            QLabel {
                color: #e74c3c;
                font-weight: bold;
                background-color: #ffeeee;
                border: 1px solid #ffcccc;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        warning_label.setWordWrap(True)
        layout.addWidget(warning_label)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        # Edit button
        self.edit_button = QPushButton("تعديل")
        self.edit_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        self.edit_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.edit_button)
        
        # Confirm button
        self.confirm_button = QPushButton("تأكيد وإرسال")
        self.confirm_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        self.confirm_button.clicked.connect(self.validate_and_accept)
        buttons_layout.addWidget(self.confirm_button)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
    
    def create_section_group(self, title, color):
        """Create a styled section group."""
        group = QGroupBox(title)
        group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {color};
                border-radius: 5px;
                margin-top: 1em;
                padding-top: 15px;
                background-color: #f9f9f9;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {color};
            }}
        """)
        return group
    
    def validate_and_accept(self):
        """Validate the transaction before accepting."""
        if not self.validate_transaction():
            return
        
        self.accept()
    
    def validate_transaction(self):
        """Validate transaction data."""
        # Check required fields
        required_fields = [
            ('sender', 'اسم المرسل'),
            ('sender_mobile', 'رقم هاتف المرسل'),
            ('receiver', 'اسم المستلم'),
            ('receiver_mobile', 'رقم هاتف المستلم'),
            ('amount', 'المبلغ')
        ]
        
        for field, name in required_fields:
            if not self.transaction_data.get(field):
                QMessageBox.warning(
                    self,
                    "بيانات ناقصة",
                    f"الحقل '{name}' مطلوب لإتمام التحويل"
                )
                return False
        
        # Validate amount
        try:
            amount = float(self.transaction_data['amount'])
            if amount <= 0:
                QMessageBox.warning(
                    self,
                    "قيمة غير صالحة",
                    "يجب أن يكون المبلغ أكبر من صفر"
                )
                return False
        except ValueError:
            QMessageBox.warning(
                self,
                "قيمة غير صالحة",
                "المبلغ يجب أن يكون رقماً صحيحاً"
            )
            return False
        
        return True