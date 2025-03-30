import sys
import requests
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, 
    QComboBox, QFormLayout, QGroupBox, QHBoxLayout
)
from PyQt6.QtGui import QFont, QDoubleValidator
from PyQt6.QtCore import Qt

class ModernGroupBox(QGroupBox):
    """Custom styled group box."""
    def __init__(self, title, color="#3498db"):
        super().__init__(title)
        self.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {color};
                border-radius: 5px;
                margin-top: 1em;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: {color};
            }}
        """)

class ModernButton(QPushButton):
    """Custom styled button with dynamic colors."""
    def __init__(self, text, color="#3498db"):
        super().__init__(text)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {self._adjust_color(color, 20)};
            }}
            QPushButton:pressed {{
                background-color: {self._adjust_color(color, -20)};
            }}
            QPushButton:disabled {{
                background-color: #95a5a6;
            }}
        """)
    
    def _adjust_color(self, hex_color, delta):
        """Lighten/darken a hex color."""
        # Fixed list comprehension syntax
        rgb = [
            min(255, max(0, int(hex_color[i:i+2], 16) + delta))
            for i in range(1, 6, 2)  # Positions 1, 3, 5 (R, G, B)
        ]
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

class AddBranchDialog(QDialog):
    def __init__(self, token=None, parent=None):
        super().__init__(parent)
        self.token = token
        self.setWindowTitle("إضافة فرع جديد")
        self.setGeometry(300, 300, 450, 400)
        
        # Main layout
        layout = QVBoxLayout()
        
        # Form group
        form_group = ModernGroupBox("معلومات الفرع")
        form_layout = QFormLayout()
        
        # Branch ID
        self.branch_id_input = QLineEdit()
        self.branch_id_input.setPlaceholderText("أدخل رقم الفرع")
        form_layout.addRow("🆔 رقم الفرع:", self.branch_id_input)
        
        # Branch Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("أدخل اسم الفرع")
        form_layout.addRow("🏢 اسم الفرع:", self.name_input)
        
        # Location
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("أدخل الموقع")
        form_layout.addRow("📍 الموقع:", self.location_input)
        
        # Governorate
        self.governorate_input = QComboBox()
        self.governorate_input.addItems([
            "دمشق", "ريف دمشق", "حلب", "حمص", "حماة", "اللاذقية", "طرطوس", 
            "إدلب", "دير الزور", "الرقة", "الحسكة", "السويداء", "درعا", "القنيطرة"
        ])
        form_layout.addRow("محافظة الفرع:", self.governorate_input)
        
        # Financial Value (optional)
        self.financial_input = QLineEdit()
        self.financial_input.setPlaceholderText("القيمة المالية (اختياري)")
        self.financial_input.setValidator(QDoubleValidator())  # Only allow numbers
        form_layout.addRow("💲 القيمة المالية:", self.financial_input)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.cancel_button = ModernButton("إلغاء", "#e74c3c")
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)
        
        self.save_button = ModernButton("حفظ", "#27ae60")
        self.save_button.clicked.connect(self.save_branch)
        self.save_button.setEnabled(False)  # Disabled by default
        buttons_layout.addWidget(self.save_button)
        
        layout.addLayout(buttons_layout)
        
        # Input validation
        self.branch_id_input.textChanged.connect(self.validate_inputs)
        self.name_input.textChanged.connect(self.validate_inputs)
        self.location_input.textChanged.connect(self.validate_inputs)
        
        self.setLayout(layout)
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
                font-family: Arial;
            }
            QLabel {
                color: #333;
                font-size: 14px;
            }
            QLineEdit, QComboBox {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                background: white;
            }
        """)

    def validate_inputs(self):
        """Enable save button only when mandatory fields are filled."""
        mandatory_filled = all([
            self.branch_id_input.text().strip(),
            self.name_input.text().strip(),
            self.location_input.text().strip()
        ])
        self.save_button.setEnabled(mandatory_filled)

    def save_branch(self):
        """Send branch data to API."""
        data = {
            "branch_id": self.branch_id_input.text(),
            "name": self.name_input.text(),
            "location": self.location_input.text(),
            "governorate": self.governorate_input.currentText(),
            "financial_value": float(self.financial_input.text()) if self.financial_input.text() else None
        }

        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            response = requests.post(
                "http://127.0.0.1:8000/branches/",
                json=data,
                headers=headers
            )

            if response.status_code in (200, 201):
                QMessageBox.information(self, "نجاح", "تمت إضافة الفرع بنجاح!")
                self.accept()
            else:
                error_msg = response.json().get("detail", f"خطأ غير معروف (رمز {response.status_code})")
                QMessageBox.warning(self, "خطأ", f"فشل الإضافة: {error_msg}")
                
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"تعذر الاتصال بالخادم: {str(e)}")

class BranchManagement(QDialog):
    """Main branch management window."""
    def __init__(self, token=None):
        super().__init__()
        self.token = token
        self.setWindowTitle("إدارة الفروع")
        self.setGeometry(200, 200, 600, 400)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("🏢 إدارة الفروع")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Add Branch Button
        self.add_button = ModernButton("➕ إضافة فرع جديد", "#27ae60")
        self.add_button.clicked.connect(self.show_add_dialog)
        layout.addWidget(self.add_button)
        
        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                font-family: Arial;
            }
        """)

    def show_add_dialog(self):
        """Show the add branch dialog."""
        dialog = AddBranchDialog(self.token, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Refresh branch list if needed
            pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BranchManagement()
    window.show()
    sys.exit(app.exec())