from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
    QComboBox, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QWidget, QStyledItemDelegate, QAbstractItemView
)
from PyQt6.QtCore import Qt, QMargins
from PyQt6.QtGui import QFont, QColor, QIcon
import requests

class UserManagementDialog(QDialog):
    """Enhanced user management dialog with modern design and full functionality."""
    
    def __init__(self, branch_id=None, token=None, user_role="employee"):
        super().__init__()
        self.branch_id = branch_id
        self.token = token
        self.user_role = user_role
        
        self.setWindowTitle("إدارة الموظفين")
        self.setMinimumSize(900, 650)
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                font-family: Arial;
            }
            QLabel {
                color: #333;
            }
            QPushButton {
                border-radius: 8px;
                padding: 10px 15px;
                font-weight: bold;
                font-size: 14px;
                min-height: 40px;
                border: none;
            }
            QLineEdit, QComboBox {
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                min-height: 40px;
            }
            QTableWidget {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background-color: white;
                gridline-color: #f0f0f0;
                alternate-background-color: #f9f9f9;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 12px;
                font-weight: bold;
                border: none;
            }
            Card {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
        """)
        
        self.setup_ui()
        self.load_employees()
        
    def setup_ui(self):
        """Initialize all UI components."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Header Card
        header_card = QWidget()
        header_card.setObjectName("Card")
        header_card.setStyleSheet("QWidget#Card {padding: 15px;}")
        header_layout = QVBoxLayout(header_card)
        
        title = QLabel(f"إدارة الموظفين - الفرع {self.branch_id}" if self.branch_id else "إدارة الموظفين")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
        
        subtitle = QLabel("إضافة وتعديل وحذف موظفي النظام")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #7f8c8d; font-size: 14px;")
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        main_layout.addWidget(header_card)
        
        # Employees Table Card
        table_card = QWidget()
        table_card.setObjectName("Card")
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(15, 15, 15, 15)
        
        self.employees_table = QTableWidget()
        self.employees_table.setColumnCount(6)
        self.employees_table.setHorizontalHeaderLabels([
            "ID", "اسم الموظف", "الدور", "الفرع", "الحالة", "الإجراءات"
        ])
        self.employees_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.employees_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.employees_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.employees_table.setAlternatingRowColors(True)
        self.employees_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        # Set custom delegate for the actions column
        self.employees_table.setItemDelegateForColumn(5, ActionButtonsDelegate(self))
        
        table_layout.addWidget(self.employees_table)
        main_layout.addWidget(table_card)
        
        # Action Buttons Card
        buttons_card = QWidget()
        buttons_card.setObjectName("Card")
        buttons_layout = QHBoxLayout(buttons_card)
        buttons_layout.setContentsMargins(15, 15, 15, 15)
        buttons_layout.setSpacing(15)
        
        self.add_button = self.create_button("➕ إضافة موظف", "#27ae60", "#2ecc71")
        self.add_button.clicked.connect(self.add_employee)
        
        self.edit_button = self.create_button("✏️ تعديل", "#f39c12", "#f1c40f")
        self.edit_button.clicked.connect(self.edit_employee)
        self.edit_button.setEnabled(False)
        
        self.delete_button = self.create_button("🗑️ حذف", "#e74c3c", "#c0392b")
        self.delete_button.clicked.connect(self.delete_employee)
        self.delete_button.setEnabled(False)
        
        self.refresh_button = self.create_button("🔄 تحديث", "#3498db", "#2980b9")
        self.refresh_button.clicked.connect(self.load_employees)
        
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.edit_button)
        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.refresh_button)
        
        main_layout.addWidget(buttons_card)
        self.setLayout(main_layout)
        
        # Connect table selection changes
        self.employees_table.selectionModel().selectionChanged.connect(self.toggle_action_buttons)
    
    def create_button(self, text, color, hover_color):
        """Helper to create styled buttons."""
        button = QPushButton(text)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:disabled {{
                background-color: #95a5a6;
            }}
        """)
        return button
    
    def toggle_action_buttons(self):
        """Enable/disable action buttons based on selection."""
        has_selection = len(self.employees_table.selectedItems()) > 0
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
    
    def load_employees(self):
        """Load employees data from API."""
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            url = f"http://127.0.0.1:8000/branches/{self.branch_id}/employees/" if self.branch_id else "http://127.0.0.1:8000/users/"
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                employees = response.json()
                self.populate_employee_table(employees)
            else:
                QMessageBox.warning(self, "خطأ", f"فشل تحميل الموظفين: {response.text}")
                
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"تعذر الاتصال بالخادم: {str(e)}")
    
    def populate_employee_table(self, employees):
        """Populate the table with employee data."""
        self.employees_table.setRowCount(len(employees))
        
        for row, employee in enumerate(employees):
            # ID
            self.employees_table.setItem(row, 0, QTableWidgetItem(str(employee.get("id", ""))))
            
            # Username
            self.employees_table.setItem(row, 1, QTableWidgetItem(employee.get("username", "")))
            
            # Role
            role = "مدير فرع" if employee.get("role") == "branch_manager" else "موظف"
            self.employees_table.setItem(row, 2, QTableWidgetItem(role))
            
            # Branch
            branch = str(employee.get("branch_id", "")) if self.branch_id else employee.get("branch_name", "")
            self.employees_table.setItem(row, 3, QTableWidgetItem(branch))
            
            # Status
            status = "نشط" if employee.get("is_active", True) else "غير نشط"
            status_item = QTableWidgetItem(status)
            status_item.setBackground(QColor("#d5f5e3") if status == "نشط" else QColor("#fadbd8"))
            self.employees_table.setItem(row, 4, status_item)
            
            # Actions (will be handled by delegate)
            self.employees_table.setItem(row, 5, QTableWidgetItem("تعديل | حذف"))
    
    def add_employee(self):
        """Open add employee dialog."""
        dialog = EmployeeDialog(is_admin=self.user_role == "admin", 
                              branch_id=self.branch_id, 
                              token=self.token)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_employees()
    
    def edit_employee(self):
        """Open edit employee dialog for selected employee."""
        selected_row = self.employees_table.currentRow()
        employee_id = self.employees_table.item(selected_row, 0).text()
        
        dialog = EmployeeDialog(is_admin=self.user_role == "admin",
                              branch_id=self.branch_id,
                              token=self.token,
                              employee_id=employee_id,
                              edit_mode=True)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_employees()
    
    def delete_employee(self):
        """Delete selected employee after confirmation."""
        selected_row = self.employees_table.currentRow()
        employee_id = self.employees_table.item(selected_row, 0).text()
        employee_name = self.employees_table.item(selected_row, 1).text()
        
        reply = QMessageBox.question(
            self,
            "تأكيد الحذف",
            f"هل أنت متأكد من حذف الموظف {employee_name}؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
                response = requests.delete(
                    f"http://127.0.0.1:8000/users/{employee_id}/",
                    headers=headers
                )
                
                if response.status_code == 204:
                    QMessageBox.information(self, "نجاح", "تم حذف الموظف بنجاح")
                    self.load_employees()
                else:
                    QMessageBox.warning(self, "خطأ", f"فشل حذف الموظف: {response.text}")
                    
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"تعذر الاتصال بالخادم: {str(e)}")

class EmployeeDialog(QDialog):
    """Dialog for adding/editing employees."""
    
    def __init__(self, is_admin=False, branch_id=None, token=None, employee_id=None, edit_mode=False):
        super().__init__()
        self.is_admin = is_admin
        self.branch_id = branch_id
        self.token = token
        self.employee_id = employee_id
        self.edit_mode = edit_mode
        
        self.setWindowTitle("تعديل موظف" if edit_mode else "إضافة موظف جديد")
        self.setMinimumSize(450, 500)
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            QLabel {
                color: #333;
                font-size: 14px;
                margin-top: 5px;
            }
            QLineEdit, QComboBox {
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }
            Card {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
        """)
        
        self.setup_ui()
        if edit_mode:
            self.load_employee_data()
    
    def setup_ui(self):
        """Initialize dialog UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header Card
        header_card = QWidget()
        header_card.setObjectName("Card")
        header_layout = QVBoxLayout(header_card)
        header_layout.setContentsMargins(15, 15, 15, 15)
        
        title = QLabel("تعديل موظف" if self.edit_mode else "إضافة موظف جديد")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
        
        header_layout.addWidget(title)
        layout.addWidget(header_card)
        
        # Form Card
        form_card = QWidget()
        form_card.setObjectName("Card")
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(15, 15, 15, 15)
        form_layout.setSpacing(10)
        
        # Username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("اسم المستخدم")
        form_layout.addWidget(QLabel("اسم الموظف:"))
        form_layout.addWidget(self.username_input)
        
        # Password (only for new employees)
        if not self.edit_mode:
            self.password_input = QLineEdit()
            self.password_input.setPlaceholderText("كلمة المرور")
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            form_layout.addWidget(QLabel("كلمة المرور:"))
            form_layout.addWidget(self.password_input)
        
        # Role
        self.role_combo = QComboBox()
        if self.is_admin:
            self.role_combo.addItems(["موظف تحويلات", "مدير فرع"])
        else:
            self.role_combo.addItem("موظف تحويلات")
        form_layout.addWidget(QLabel("الدور:"))
        form_layout.addWidget(self.role_combo)
        
        # Branch (only for admins)
        if self.is_admin:
            self.branch_combo = QComboBox()
            form_layout.addWidget(QLabel("الفرع:"))
            form_layout.addWidget(self.branch_combo)
            self.load_branches()
        
        # Status (only for admins in edit mode)
        if self.edit_mode and self.is_admin:
            self.status_combo = QComboBox()
            self.status_combo.addItems(["نشط", "غير نشط"])
            form_layout.addWidget(QLabel("الحالة:"))
            form_layout.addWidget(self.status_combo)
        
        layout.addWidget(form_card)
        
        # Save Button
        self.save_button = QPushButton("حفظ التغييرات" if self.edit_mode else "إضافة الموظف")
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                padding: 12px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.save_button.clicked.connect(self.save_employee)
        layout.addWidget(self.save_button)
        
        self.setLayout(layout)
        
        # Enable/disable save button based on input
        if not self.edit_mode:
            self.username_input.textChanged.connect(self.validate_inputs)
            self.password_input.textChanged.connect(self.validate_inputs)
            self.save_button.setEnabled(False)
    
    def load_branches(self):
        """Load branches for admin to assign."""
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            response = requests.get("http://127.0.0.1:8000/branches/", headers=headers)
            
            if response.status_code == 200:
                branches = response.json()
                self.branch_combo.clear()
                
                for branch in branches:
                    self.branch_combo.addItem(branch["name"], branch["id"])
                
                # Select current branch if not in edit mode
                if not self.edit_mode and self.branch_id:
                    index = self.branch_combo.findData(self.branch_id)
                    if index >= 0:
                        self.branch_combo.setCurrentIndex(index)
            else:
                QMessageBox.warning(self, "خطأ", "فشل تحميل قائمة الفروع")
                
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"تعذر الاتصال بالخادم: {str(e)}")
    
    def load_employee_data(self):
        """Load employee data for editing."""
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            response = requests.get(
                f"http://127.0.0.1:8000/users/{self.employee_id}/", 
                headers=headers
            )
            
            if response.status_code == 200:
                employee = response.json()
                
                self.username_input.setText(employee.get("username", ""))
                
                # Set role
                role_index = 1 if employee.get("role") == "branch_manager" else 0
                self.role_combo.setCurrentIndex(role_index)
                
                # Set branch if admin
                if self.is_admin:
                    branch_id = employee.get("branch_id")
                    index = self.branch_combo.findData(branch_id)
                    if index >= 0:
                        self.branch_combo.setCurrentIndex(index)
                
                # Set status if admin
                if hasattr(self, 'status_combo'):
                    status_index = 0 if employee.get("is_active", True) else 1
                    self.status_combo.setCurrentIndex(status_index)
            
            else:
                QMessageBox.warning(self, "خطأ", "فشل تحميل بيانات الموظف")
                self.reject()
                
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"تعذر الاتصال بالخادم: {str(e)}")
            self.reject()
    
    def validate_inputs(self):
        """Enable save button only when required fields are filled."""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip() if hasattr(self, 'password_input') else True
        
        self.save_button.setEnabled(bool(username) and bool(password))
    
    def save_employee(self):
        """Save employee data to API."""
        data = {
            "username": self.username_input.text(),
            "role": "branch_manager" if self.role_combo.currentText() == "مدير فرع" else "employee",
            "branch_id": self.branch_combo.currentData() if self.is_admin else self.branch_id
        }
        
        # Add password for new employees
        if not self.edit_mode:
            data["password"] = self.password_input.text()
        
        # Add status for admins editing
        if self.edit_mode and self.is_admin and hasattr(self, 'status_combo'):
            data["is_active"] = self.status_combo.currentText() == "نشط"
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            
            if self.edit_mode:
                response = requests.patch(
                    f"http://127.0.0.1:8000/users/{self.employee_id}/",
                    json=data,
                    headers=headers
                )
            else:
                response = requests.post(
                    "http://127.0.0.1:8000/users/",
                    json=data,
                    headers=headers
                )
            
            if response.status_code in (200, 201):
                QMessageBox.information(self, "نجاح", "تم حفظ البيانات بنجاح")
                self.accept()
            else:
                QMessageBox.warning(self, "خطأ", f"فشل حفظ البيانات: {response.text}")
                
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"تعذر الاتصال بالخادم: {str(e)}")

class ActionButtonsDelegate(QStyledItemDelegate):
    """Custom delegate for action buttons in table."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
    
    def paint(self, painter, option, index):
        """Paint buttons in the cell."""
        super().paint(painter, option, index)
        
        if index.column() == 5:  # Actions column
            # Draw edit button
            edit_rect = option.rect.adjusted(10, 5, -60, -5)
            painter.save()
            painter.setBrush(QColor("#3498db"))
            painter.setPen(QColor("#3498db"))
            painter.drawRoundedRect(edit_rect, 5, 5)
            painter.setPen(QColor("white"))
            painter.drawText(edit_rect, Qt.AlignmentFlag.AlignCenter, "تعديل")
            painter.restore()
            
            # Draw delete button
            delete_rect = option.rect.adjusted(70, 5, -10, -5)
            painter.save()
            painter.setBrush(QColor("#e74c3c"))
            painter.setPen(QColor("#e74c3c"))
            painter.drawRoundedRect(delete_rect, 5, 5)
            painter.setPen(QColor("white"))
            painter.drawText(delete_rect, Qt.AlignmentFlag.AlignCenter, "حذف")
            painter.restore()
    
    def editorEvent(self, event, model, option, index):
        """Handle button clicks."""
        if (event.type() == event.Type.MouseButtonRelease and 
            index.column() == 5):
            
            # Check if edit button was clicked
            edit_rect = option.rect.adjusted(10, 5, -60, -5)
            if edit_rect.contains(event.pos()):
                self.parent.edit_employee()
                return True
            
            # Check if delete button was clicked
            delete_rect = option.rect.adjusted(70, 5, -10, -5)
            if delete_rect.contains(event.pos()):
                self.parent.delete_employee()
                return True
        
        return super().editorEvent(event, model, option, index)

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    dialog = UserManagementDialog(branch_id=1)
    dialog.show()
    sys.exit(app.exec())