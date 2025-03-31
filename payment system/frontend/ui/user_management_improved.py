from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import requests

class UserManagement(QDialog):
    def __init__(self, branch_id, token=None):
        super().__init__()
        self.branch_id = branch_id  # Store the branch_id
        self.token = token  # Store the token
        self.setWindowTitle("إدارة الموظفين")
        self.setGeometry(200, 200, 900, 650)
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                font-family: Arial;
            }
            QLabel {
                color: #333;
                font-size: 14px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QLineEdit, QComboBox {
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 10px;
                background-color: white;
                font-size: 14px;
            }
            QTableWidget {
                border: 1px solid #e6e6e6;
                border-radius: 8px;
                background-color: white;
                gridline-color: #f0f0f0;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #2c3e50;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 12px;
                border: none;
                font-weight: bold;
                font-size: 14px;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                border-radius: 5px;
            }
        """)

        self.layout = QVBoxLayout()

        # Header section with card-like design
        header_widget = QWidget()
        header_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e6e6e6;
            }
        """)
        header_layout = QVBoxLayout(header_widget)
        
        self.title = QLabel(f"إدارة الموظفين للفرع: {self.branch_id}")
        self.title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("color: #2c3e50; margin: 10px 0;")
        header_layout.addWidget(self.title)
        
        # Subtitle
        subtitle = QLabel("قائمة الموظفين وإدارة الصلاحيات")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #7f8c8d; margin-bottom: 10px; font-size: 16px;")
        header_layout.addWidget(subtitle)
        
        self.layout.addWidget(header_widget)
        self.layout.addSpacing(15)
        
        # Employees table with card-like design
        table_container = QWidget()
        table_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e6e6e6;
                padding: 10px;
            }
        """)
        table_layout = QVBoxLayout(table_container)
        
        table_title = QLabel("قائمة الموظفين")
        table_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        table_title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        table_layout.addWidget(table_title)
        
        self.employees_table = QTableWidget()
        self.employees_table.setColumnCount(5)
        self.employees_table.setHorizontalHeaderLabels(["معرف", "اسم الموظف", "الوظيفة", "الفرع", "الإجراءات"])
        self.employees_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.employees_table.setAlternatingRowColors(True)
        self.employees_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.employees_table.setStyleSheet("""
            QTableWidget {
                border: none;
                border-radius: 8px;
                background-color: white;
            }
        """)
        table_layout.addWidget(self.employees_table)
        
        self.layout.addWidget(table_container)
        
        # Buttons section with card-like design
        buttons_container = QWidget()
        buttons_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e6e6e6;
                padding: 15px;
            }
        """)
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setSpacing(15)
        
        # Add employee button
        self.add_employee_button = QPushButton("➕ إضافة موظف جديد")
        self.add_employee_button.clicked.connect(self.add_employee)
        self.add_employee_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border-radius: 8px;
                padding: 12px;
                font-weight: bold;
                font-size: 14px;
                min-height: 45px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        buttons_layout.addWidget(self.add_employee_button)
        
        # Edit employee button
        self.edit_employee_button = QPushButton("✏️ تعديل الموظف المحدد")
        self.edit_employee_button.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border-radius: 8px;
                padding: 12px;
                font-weight: bold;
                font-size: 14px;
                min-height: 45px;
            }
            QPushButton:hover {
                background-color: #f1c40f;
            }
        """)
        buttons_layout.addWidget(self.edit_employee_button)
        
        # Delete employee button
        self.delete_employee_button = QPushButton("❌ حذف الموظف المحدد")
        self.delete_employee_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 8px;
                padding: 12px;
                font-weight: bold;
                font-size: 14px;
                min-height: 45px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        buttons_layout.addWidget(self.delete_employee_button)
        
        # Refresh button
        self.refresh_button = QPushButton("🔄 تحديث القائمة")
        self.refresh_button.clicked.connect(self.load_employees)
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 8px;
                padding: 12px;
                font-weight: bold;
                font-size: 14px;
                min-height: 45px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        buttons_layout.addWidget(self.refresh_button)
        
        self.layout.addSpacing(15)
        self.layout.addWidget(buttons_container)
        
        self.setLayout(self.layout)
        
        # Load employees data
        self.load_employees()

    def load_employees(self):
        """Load employees data for this branch."""
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            response = requests.get(f"http://127.0.0.1:8000/branches/{self.branch_id}/employees/", headers=headers)
            
            if response.status_code == 200:
                employees = response.json()
                self.employees_table.setRowCount(len(employees))
                
                for row, employee in enumerate(employees):
                    # ID
                    id_item = QTableWidgetItem(str(employee.get("id", "")))
                    self.employees_table.setItem(row, 0, id_item)
                    
                    # Name
                    name_item = QTableWidgetItem(employee.get("username", ""))
                    self.employees_table.setItem(row, 1, name_item)
                    
                    # Role
                    role_text = "مدير فرع" if employee.get("role") == "branch_manager" else "موظف تحويلات"
                    role_item = QTableWidgetItem(role_text)
                    self.employees_table.setItem(row, 2, role_item)
                    
                    # Branch
                    branch_item = QTableWidgetItem(str(employee.get("branch_id", "")))
                    self.employees_table.setItem(row, 3, branch_item)
                    
                    # Actions - placeholder for now
                    actions_item = QTableWidgetItem("...")
                    self.employees_table.setItem(row, 4, actions_item)
            else:
                QMessageBox.warning(self, "خطأ", f"فشل في تحميل الموظفين! الخطأ: {response.status_code}")
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"تعذر الاتصال بالخادم: {str(e)}")

    def add_employee(self):
        """Add a new employee."""
        self.add_employee_window = AddEmployeeDialog(is_admin=True, branch_id=self.branch_id, token=self.token)
        if self.add_employee_window.exec() == QDialog.DialogCode.Accepted:
            QMessageBox.information(self, "نجاح", "تمت إضافة الموظف بنجاح!")
            self.load_employees()  # Refresh the employee list

class AddEmployeeDialog(QDialog):
    def __init__(self, is_admin=False, branch_id=None, token=None):
        super().__init__()
        self.setWindowTitle("إضافة موظف جديد")
        self.setGeometry(250, 250, 450, 500)
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                font-family: Arial;
            }
            QLabel {
                color: #333;
                font-size: 14px;
                margin-top: 5px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QLineEdit, QComboBox {
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 12px;
                background-color: white;
                font-size: 14px;
                margin-bottom: 5px;
            }
        """)

        self.is_admin = is_admin
        self.branch_id = branch_id
        self.token = token  # Store the token

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title with card-like design
        title_container = QWidget()
        title_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e6e6e6;
                padding: 10px;
            }
        """)
        title_layout = QVBoxLayout(title_container)
        
        title = QLabel("إضافة موظف جديد")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin: 5px 0;")
        title_layout.addWidget(title)
        
        subtitle = QLabel("أدخل معلومات الموظف الجديد")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #7f8c8d; font-size: 14px;")
        title_layout.addWidget(subtitle)
        
        layout.addWidget(title_container)
        layout.addSpacing(15)

        # Form with card-like design
        form_container = QWidget()
        form_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e6e6e6;
                padding: 15px;
            }
        """)
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(12)

        # Employee name
        name_label = QLabel("👤 اسم الموظف:")
        name_label.setStyleSheet("font-weight: bold;")
        form_layout.addWidget(name_label)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("أدخل اسم الموظف")
        form_layout.addWidget(self.name_input)
        form_layout.addSpacing(5)

        # Password
        password_label = QLabel("🔑 كلمة المرور:")
        password_label.setStyleSheet("font-weight: bold;")
        form_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("أدخل كلمة المرور")
        form_layout.addWidget(self.password_input)
        form_layout.addSpacing(5)

        # Role
        role_label = QLabel("💼 الوظيفة:")
        role_label.setStyleSheet("font-weight: bold;")
        form_layout.addWidget(role_label)
        
        self.role_input = QComboBox()
        if self.is_admin:
            self.role_input.addItems(["مدير فرع", "موظف تحويلات"])
        else:
            self.role_input.addItems(["موظف تحويلات"])
        form_layout.addWidget(self.role_input)
        form_layout.addSpacing(5)

        # Branch
        branch_label = QLabel("🏢 الفرع:")
        branch_label.setStyleSheet("font-weight: bold;")
        form_layout.addWidget(branch_label)
        
        self.branch_input = QComboBox()
        form_layout.addWidget(self.branch_input)
        
        layout.addWidget(form_container)
        layout.addSpacing(15)

        # Save button
        self.save_button = QPushButton("✅ حفظ")
        self.save_button.clicked.connect(self.save_employee)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border-radius: 8px;
                padding: 12px;
                font-weight: bold;
                font-size: 15px;
                min-height: 50px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        layout.addWidget(self.save_button)

        self.name_input.textChanged.connect(self.validate_inputs)
        self.password_input.textChanged.connect(self.validate_inputs)

        self.setLayout(layout)
        
        # Initially disable save button
        self.save_button.setEnabled(False)
        
        # Load branches
        self.load_branches()

    def load_branches(self):
        """Load branches from the API."""
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            
            response = requests.get("http://127.0.0.1:8000/branches/", headers=headers)
            
            if response.status_code == 200:
                branches = response.json()
                self.branch_input.clear()
                
                for branch in branches:
                    self.branch_input.addItem(branch["name"], branch["id"])
            else:
                QMessageBox.warning(self, "خطأ", f"فشل في تحميل الفروع! الخطأ: {response.status_code} - {response.text}")
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"تعذر الاتصال بالخادم: {str(e)}")

    def validate_inputs(self):
        """Enable the save button only when all fields are filled."""
        name = self.name_input.text()
        password = self.password_input.text()

        if name and password:
            self.save_button.setEnabled(True)
        else:
            self.save_button.setEnabled(False)

    def save_employee(self):
        """Send employee data to the API for registration."""
        data = {
            "username": self.name_input.text(),
            "password": self.password_input.text(),
            "role": "branch_manager" if self.role_input.currentText() == "مدير فرع" else "employee",
            "branch_id": self.branch_input.currentData()
        }

        try:
            # Ensure token is properly formatted with Bearer prefix
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            print(f"Using token: {self.token}")
            print(f"Sending data: {data}")
            
            # Use /users/ endpoint instead of /register/ as it has the same functionality but with better error handling
            response = requests.post("http://127.0.0.1:8000/users/", json=data, headers=headers)

            if response.status_code == 200:
                QMessageBox.information(self, "نجاح", "تمت إضافة الموظف بنجاح!")
                self.accept()
            else:
                QMessageBox.warning(self, "خطأ", f"حدث خطأ أثناء إضافة الموظف! الخطأ: {response.status_code} - {response.text}")
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"تعذر الاتصال بالخادم: {str(e)}")
