from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import requests

class ChangePasswordDialog(QDialog):
    def __init__(self, token=None):
        super().__init__()
        self.token = token
        self.setWindowTitle("تغيير كلمة المرور")
        self.setFixedSize(400, 250)  # Fixed size for consistency
        
        # Modernized styling with better spacing
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Arial;
            }
            QLabel {
                color: #495057;
                font-size: 14px;
                margin-bottom: 5px;
            }
            QLineEdit {
                border: 1px solid #ced4da;
                border-radius: 6px;
                padding: 10px;
                background-color: white;
                font-size: 14px;
                margin-bottom: 15px;
            }
            QLineEdit:focus {
                border: 1px solid #80bdff;
                box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(10)

        # Title
        title = QLabel("تغيير كلمة المرور")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(title)

        # Current password
        self.old_password_input = QLineEdit()
        self.old_password_input.setPlaceholderText("كلمة المرور الحالية")
        self.old_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(QLabel("🔑 كلمة المرور الحالية:"))
        layout.addWidget(self.old_password_input)

        # New password
        self.new_password_input = QLineEdit()
        self.new_password_input.setPlaceholderText("كلمة المرور الجديدة")
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(QLabel("🔑 كلمة المرور الجديدة:"))
        layout.addWidget(self.new_password_input)

        # Change button with improved styling
        self.change_button = QPushButton("تغيير كلمة المرور")
        self.change_button.clicked.connect(self.change_password)
        self.change_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border-radius: 6px;
                padding: 12px;
                font-weight: bold;
                font-size: 14px;
                margin-top: 10px;
                border: none;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        layout.addWidget(self.change_button)

        self.setLayout(layout)

    def change_password(self):
        """Change the user's password (unchanged functionality)."""
        old_password = self.old_password_input.text()
        new_password = self.new_password_input.text()

        if not old_password or not new_password:
            QMessageBox.warning(self, "خطأ", "يرجى ملء جميع الحقول!")
            return

        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            
            response = requests.post(
                "http://127.0.0.1:8000/change-password/", 
                json={
                    "old_password": old_password,
                    "new_password": new_password
                },
                headers=headers
            )

            if response.status_code == 200:
                QMessageBox.information(self, "نجاح", "تم تغيير كلمة المرور بنجاح!")
                self.accept()
            else:
                error_msg = response.json().get("detail", response.text)
                QMessageBox.warning(self, "خطأ", f"فشل تغيير كلمة المرور: {error_msg}")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"تعذر الاتصال بالخادم: {str(e)}")