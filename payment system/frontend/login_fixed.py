from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QComboBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import requests
import jwt
import datetime

# Secret key for generating local tokens - should match the one in backend/security.py
SECRET_KEY = "929b15e43fd8f1cf4df79d86eb93ca426ab58ae53386c7a91ac4adb45832773b"
ALGORITHM = "HS256"

# Test users for local login
TEST_USERS = {
    "admin": {
        "password": "password123",
        "role": "director",
        "branch_id": 1,
        "user_id": 1
    },
    "branch_manager": {
        "password": "password123",
        "role": "branch_manager",
        "branch_id": 2,
        "user_id": 2
    },
    "employee": {
        "password": "password123",
        "role": "employee",
        "branch_id": 3,
        "user_id": 3
    }
}

def get_common_styles():
    """Return common stylesheets to reduce duplication."""
    return """
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
        QLineEdit, QComboBox {
            border: 1px solid #ccc;
            border-radius: 5px;
            padding: 8px;
            background-color: white;
            font-size: 14px;
        }
    """

class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("تسجيل الدخول")
        self.setGeometry(200, 200, 400, 300)
        self.setStyleSheet(get_common_styles())

        # Initialize UI components
        self.layout = QVBoxLayout()
        self.setup_ui()
        self.setLayout(self.layout)

        # User data
        self.user_role = None
        self.branch_id = None
        self.user_id = None
        self.token = None

    def setup_ui(self):
        """Initialize UI components."""
        # Title
        title = QLabel("نظام تحويل الأموال الداخلي")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        self.layout.addWidget(title)

        # Username and password fields
        self.username_input = QLineEdit(self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.layout.addWidget(QLabel("اسم المستخدم:"))
        self.layout.addWidget(self.username_input)
        self.layout.addWidget(QLabel("كلمة المرور:"))
        self.layout.addWidget(self.password_input)

        # Login button
        self.login_button = QPushButton("تسجيل الدخول")
        self.login_button.clicked.connect(self.check_login)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px;
                font-size: 14px;
                margin-top: 20px;
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        self.layout.addWidget(self.login_button)

        # Create user button (hidden by default)
        self.create_user_button = QPushButton("إنشاء مستخدم جديد")
        self.create_user_button.clicked.connect(self.open_create_user_dialog)
        self.create_user_button.setVisible(False)
        self.layout.addWidget(self.create_user_button)

    def check_login(self):
        """Check credentials via local test or backend API."""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "خطأ", "يرجى إدخال البيانات المطلوبة!")
            return

        if self.local_login_test(username, password):
            return  # Local login successful

        self.backend_login(username, password)

    def local_login_test(self, username, password):
        """Authenticate using test users."""
        user = TEST_USERS.get(username)
        if user and user["password"] == password:
            self.user_role = user["role"]
            self.branch_id = user["branch_id"]
            self.user_id = user["user_id"]
            self.token = self.create_local_token(username, user["role"], user["branch_id"], user["user_id"])
            
            # Show create button for admins and branch managers
            self.create_user_button.setVisible(self.user_role in ("director", "branch_manager"))
            QMessageBox.information(self, "نجاح", f"تم التسجيل كـ {self.user_role}!")
            self.accept()
            return True
        return False

    def create_local_token(self, username, role, branch_id, user_id):
        """Generate a JWT token for local testing."""
        payload = {
            "username": username,
            "role": role,
            "branch_id": branch_id,
            "user_id": user_id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    def backend_login(self, username, password):
        """Authenticate via backend API and validate token."""
        try:
            response = requests.post(
                "http://127.0.0.1:8000/login/",
                json={"username": username, "password": password},
                timeout=5
            )
            response.raise_for_status()  # Raise HTTP errors

            data = response.json()
            token = data.get("token")
            if not token:
                raise ValueError("No token received")

            # Decode token to validate and extract data
            decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            self.user_role = decoded.get("role")
            self.branch_id = decoded.get("branch_id")
            self.user_id = decoded.get("user_id")
            self.token = token

            # Update UI based on role
            self.create_user_button.setVisible(self.user_role in ("director", "branch_manager"))
            QMessageBox.information(self, "نجاح", f"مرحبًا {self.user_role}!")
            self.accept()

        except requests.exceptions.RequestException as e:
            QMessageBox.warning(self, "خطأ", f"فشل الاتصال: {str(e)}")
        except (jwt.InvalidTokenError, ValueError) as e:
            QMessageBox.warning(self, "خطأ", f"فشل المصادقة: {str(e)}")

    def open_create_user_dialog(self):
        """Open user creation dialog."""
        dialog = CreateUserDialog(self.user_role, self.branch_id, self.token, self)
        dialog.exec()

class CreateUserDialog(QDialog):
    def __init__(self, user_role, branch_id, token, parent=None):
        super().__init__(parent)
        self.setWindowTitle("إنشاء مستخدم جديد")
        self.setGeometry(250, 250, 400, 350)
        self.setStyleSheet(get_common_styles())

        self.user_role = user_role
        self.branch_id = branch_id
        self.token = token

        # Initialize UI
        layout = QVBoxLayout()
        title = QLabel("إنشاء مستخدم جديد")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(title)

        # Username and password fields
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(QLabel("اسم المستخدم:"))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel("كلمة المرور:"))
        layout.addWidget(self.password_input)

        # Role selection
        self.role_input = QComboBox()
        layout.addWidget(QLabel("الوظيفة:"))
        layout.addWidget(self.role_input)
        if self.user_role == "director":
            self.role_input.addItem("مدير فرع", "branch_manager")
            self.role_input.addItem("موظف", "employee")
        else:
            self.role_input.addItem("موظف", "employee")

        # Branch selection (for directors)
        if self.user_role == "director":
            self.branch_input = QComboBox()
            layout.addWidget(QLabel("الفرع:"))
            layout.addWidget(self.branch_input)
            self.load_branches()

        # Create button
        self.create_button = QPushButton("إنشاء مستخدم")
        self.create_button.clicked.connect(self.create_user)
        self.create_button.setStyleSheet("""
            QPushButton { background-color: #27ae60; padding: 10px; }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        layout.addWidget(self.create_button)

        self.setLayout(layout)

    def load_branches(self):
        """Load branches from API."""
        try:
            response = requests.get(
                "http://127.0.0.1:8000/branches/",
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=5
            )
            response.raise_for_status()
            branches = response.json()
            self.branch_input.clear()
            for branch in branches:
                self.branch_input.addItem(branch["name"], branch["id"])
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل تحميل الفروع: {str(e)}")

    def create_user(self):
        """Send user creation request to backend."""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        role = self.role_input.currentData()
        branch_id = (self.branch_input.currentData() 
                    if self.user_role == "director" 
                    else self.branch_id)

        if not username or not password:
            QMessageBox.warning(self, "خطأ", "يرجى ملء جميع الحقول!")
            return

        try:
            response = requests.post(
                "http://127.0.0.1:8000/register/",
                json={
                    "username": username,
                    "password": password,
                    "role": role,
                    "branch_id": branch_id
                },
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=5
            )
            response.raise_for_status()
            QMessageBox.information(self, "نجاح", "تم إنشاء المستخدم!")
            self.accept()
        except requests.exceptions.HTTPError as e:
            error_msg = response.json().get("detail", "Unknown error")
            QMessageBox.warning(self, "خطأ", f"فشل الإنشاء: {error_msg}")
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"خطأ في الاتصال: {str(e)}")