from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
import requests

class PasswordResetDialog(QDialog):
    def __init__(self, is_admin=False, token=None):
        super().__init__()
        self.is_admin = is_admin
        self.token = token
        self.setWindowTitle("إعادة تعيين كلمة المرور")
        self.setGeometry(250, 250, 400, 250)  # Increased height slightly
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                font-family: Arial;
            }
            QLabel {
                color: #333;
                font-size: 14px;
            }
            QPushButton {
                background-color: #2c3e50;
                color: white;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 8px;
                background-color: white;
                font-size: 14px;
            }
        """)

        layout = QVBoxLayout()

        # Username field
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("اسم المستخدم")
        layout.addWidget(QLabel("👤 اسم المستخدم:"))
        layout.addWidget(self.username_input)

        # New password field
        self.new_password_input = QLineEdit()
        self.new_password_input.setPlaceholderText("كلمة المرور الجديدة (8 أحرف على الأقل)")
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(QLabel("🔑 كلمة المرور الجديدة:"))
        layout.addWidget(self.new_password_input)

        # Confirm password field (new addition)
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("تأكيد كلمة المرور الجديدة")
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(QLabel("🔏 تأكيد كلمة المرور:"))
        layout.addWidget(self.confirm_password_input)

        # Reset button
        self.reset_button = QPushButton("إعادة تعيين")
        self.reset_button.clicked.connect(self.reset_password)
        self.reset_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
                font-size: 14px;
                margin-top: 20px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        layout.addWidget(self.reset_button)

        self.setLayout(layout)

    def reset_password(self):
        """Reset the user's password with validation."""
        username = self.username_input.text().strip()
        new_password = self.new_password_input.text()
        confirm_password = self.confirm_password_input.text()

        if not username or not new_password or not confirm_password:
            QMessageBox.warning(self, "خطأ", "يرجى ملء جميع الحقول!")
            return

        if new_password != confirm_password:
            QMessageBox.warning(self, "خطأ", "كلمتا المرور غير متطابقتين!")
            return

        if len(new_password) < 8:
            QMessageBox.warning(self, "خطأ", "كلمة المرور يجب أن تكون 8 أحرف على الأقل!")
            return

        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            
            response = requests.post(
                "http://127.0.0.1:8000/reset-password/", 
                json={
                    "username": username,
                    "new_password": new_password
                },
                headers=headers,
                timeout=5  # Added timeout
            )

            if response.status_code == 200:
                QMessageBox.information(self, "نجاح", "تمت إعادة تعيين كلمة المرور بنجاح!")
                self.accept()
            else:
                error_msg = response.json().get('detail', response.text)
                QMessageBox.warning(self, "خطأ", f"حدث خطأ أثناء إعادة تعيين كلمة المرور!\n{error_msg}")
        except requests.exceptions.RequestException as e:
            QMessageBox.warning(self, "خطأ", f"تعذر الاتصال بالخادم: {str(e)}")