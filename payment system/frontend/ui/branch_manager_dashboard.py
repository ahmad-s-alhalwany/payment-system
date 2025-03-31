import sys
import requests
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QWidget, QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QDialog, QLineEdit, QFormLayout, QComboBox, QGroupBox,
    QGridLayout, QSpacerItem, QSizePolicy
)
from PyQt6.QtGui import QFont, QColor, QIcon
from PyQt6.QtCore import Qt, QTimer

from ui.money_transfer_improved import MoneyTransferApp
from ui.branch_management_improved import AddBranchDialog, EditBranchDialog
from ui.user_search import UserSearchDialog
from ui.user_management_improved import AddEmployeeDialog

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
                padding: 0 5px 0 5px;
                color: {color};
            }}
        """)

class ModernButton(QPushButton):
    """Custom styled button."""
    
    def __init__(self, text, color="#3498db"):
        super().__init__(text)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.lighten_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(color)};
            }}
        """)
    
    def lighten_color(self, color):
        """Lighten a hex color."""
        # Simple implementation - not perfect but works for our needs
        if color.startswith('#'):
            color = color[1:]
        r = min(255, int(color[0:2], 16) + 20)
        g = min(255, int(color[2:4], 16) + 20)
        b = min(255, int(color[4:6], 16) + 20)
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def darken_color(self, color):
        """Darken a hex color."""
        if color.startswith('#'):
            color = color[1:]
        r = max(0, int(color[0:2], 16) - 20)
        g = max(0, int(color[2:4], 16) - 20)
        b = max(0, int(color[4:6], 16) - 20)
        return f"#{r:02x}{g:02x}{b:02x}"

class BranchManagerDashboard(QMainWindow):
    """Branch Manager Dashboard for the Internal Payment System."""
    
    def __init__(self, branch_id, token=None, api_url="http://127.0.0.1:8000"):
        super().__init__()
        self.branch_id = branch_id
        self.token = token
        self.api_url = api_url
        
        self.setWindowTitle("لوحة تحكم مدير الفرع - نظام التحويلات المالية")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
                font-family: Arial;
            }
        """)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        header_layout = QHBoxLayout()
        
        # Logo/Title
        title_label = QLabel("نظام التحويلات المالية - لوحة تحكم مدير الفرع")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #2c3e50;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)
        
        main_layout.addLayout(header_layout)
        
        # Tab widget for different sections
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #ddd;
                padding: 8px 12px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: #2c3e50;
                color: white;
            }
        """)
        
        # Create tabs
        self.dashboard_tab = QWidget()
        self.employees_tab = QWidget()
        self.transfers_tab = QWidget()
        self.reports_tab = QWidget()
        self.settings_tab = QWidget()
        
        # Set up tabs
        self.setup_dashboard_tab()
        self.setup_employees_tab()
        self.setup_transfers_tab()
        self.setup_reports_tab()
        self.setup_settings_tab()
        
        # Add tabs to widget
        self.tab_widget.addTab(self.dashboard_tab, "الرئيسية")
        self.tab_widget.addTab(self.employees_tab, "إدارة الموظفين")
        self.tab_widget.addTab(self.transfers_tab, "التحويلات")
        self.tab_widget.addTab(self.reports_tab, "التقارير")
        self.tab_widget.addTab(self.settings_tab, "الإعدادات")
        
        main_layout.addWidget(self.tab_widget)
        
        # Status bar
        self.statusBar().showMessage("جاهز")
        
        # Load branch info
        self.load_branch_info()
        
        # Refresh data initially
        self.refresh_dashboard_data()
        
        # Set up refresh timer (every 5 minutes)
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_dashboard_data)
        self.refresh_timer.start(300000)  # 5 minutes in milliseconds
    
    def setup_dashboard_tab(self):
        """Set up the main dashboard tab."""
        layout = QVBoxLayout()
        
        # Welcome message
        welcome_group = ModernGroupBox("لوحة المعلومات", "#e74c3c")
        welcome_layout = QVBoxLayout()
        
        welcome_label = QLabel("مرحباً بك في لوحة تحكم مدير الفرع")
        welcome_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet("color: #2c3e50; margin: 10px 0;")
        welcome_layout.addWidget(welcome_label)
        
        self.branch_name_label = QLabel("الفرع: جاري التحميل...")
        self.branch_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(self.branch_name_label)
        
        date_label = QLabel("تاريخ اليوم: جاري التحميل...")
        date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(date_label)
        self.date_label = date_label
        
        welcome_group.setLayout(welcome_layout)
        layout.addWidget(welcome_group)
        
        # Statistics
        stats_layout = QHBoxLayout()
        
        # Employees stats
        employees_group = ModernGroupBox("إحصائيات الموظفين", "#2ecc71")
        employees_layout = QVBoxLayout()
        
        self.employees_count = QLabel("عدد الموظفين: جاري التحميل...")
        self.employees_count.setFont(QFont("Arial", 12))
        employees_layout.addWidget(self.employees_count)
        
        self.active_employees = QLabel("الموظفين النشطين: جاري التحميل...")
        self.active_employees.setFont(QFont("Arial", 12))
        employees_layout.addWidget(self.active_employees)
        
        employees_group.setLayout(employees_layout)
        stats_layout.addWidget(employees_group)
        
        # Transactions stats
        transactions_group = ModernGroupBox("إحصائيات التحويلات", "#e67e22")
        transactions_layout = QVBoxLayout()
        
        self.transactions_count = QLabel("عدد التحويلات: جاري التحميل...")
        self.transactions_count.setFont(QFont("Arial", 12))
        transactions_layout.addWidget(self.transactions_count)
        
        self.transactions_amount = QLabel("إجمالي مبالغ التحويلات: جاري التحميل...")
        self.transactions_amount.setFont(QFont("Arial", 12))
        transactions_layout.addWidget(self.transactions_amount)
        
        transactions_group.setLayout(transactions_layout)
        stats_layout.addWidget(transactions_group)
        
        layout.addLayout(stats_layout)
        
        # Quick actions
        actions_group = ModernGroupBox("إجراءات سريعة", "#9b59b6")
        actions_layout = QHBoxLayout()
        
        add_employee_button = ModernButton("إضافة موظف جديد", color="#2ecc71")
        add_employee_button.clicked.connect(self.add_employee)
        actions_layout.addWidget(add_employee_button)
        
        search_user_button = ModernButton("بحث عن مستخدم", color="#e67e22")
        search_user_button.clicked.connect(self.search_user)
        actions_layout.addWidget(search_user_button)
        
        new_transfer_button = ModernButton("تحويل جديد", color="#3498db")
        new_transfer_button.clicked.connect(self.new_transfer)
        actions_layout.addWidget(new_transfer_button)
        
        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)
        
        # Recent transactions
        recent_group = ModernGroupBox("أحدث التحويلات", "#3498db")
        recent_layout = QVBoxLayout()
        
        self.recent_transactions_table = QTableWidget()
        self.recent_transactions_table.setColumnCount(5)
        self.recent_transactions_table.setHorizontalHeaderLabels([
            "رقم التحويل", "المرسل", "المستلم", "المبلغ", "التاريخ"
        ])
        self.recent_transactions_table.horizontalHeader().setStretchLastSection(True)
        self.recent_transactions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.recent_transactions_table.setStyleSheet("""
            QTableWidget {
                border: none;
                background-color: white;
                gridline-color: #ddd;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 8px;
                border: 1px solid #1a2530;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        recent_layout.addWidget(self.recent_transactions_table)
        
        view_all_button = ModernButton("عرض جميع التحويلات", color="#3498db")
        view_all_button.clicked.connect(lambda: self.tab_widget.setCurrentIndex(2))  # Switch to transfers tab
        recent_layout.addWidget(view_all_button)
        
        recent_group.setLayout(recent_layout)
        layout.addWidget(recent_group)
        
        self.dashboard_tab.setLayout(layout)
        
        # Load recent transactions
        self.load_recent_transactions()
    
    def setup_employees_tab(self):
        """Set up the employees management tab."""
        layout = QVBoxLayout()
        
        # Employees table
        employees_group = ModernGroupBox("قائمة الموظفين", "#2ecc71")
        employees_layout = QVBoxLayout()
        
        self.employees_table = QTableWidget()
        self.employees_table.setColumnCount(5)
        self.employees_table.setHorizontalHeaderLabels([
            "اسم المستخدم", "الدور", "الحالة", "تاريخ الإنشاء", "الإجراءات"
        ])
        self.employees_table.horizontalHeader().setStretchLastSection(True)
        self.employees_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.employees_table.setStyleSheet("""
            QTableWidget {
                border: none;
                background-color: white;
                gridline-color: #ddd;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 8px;
                border: 1px solid #1a2530;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        employees_layout.addWidget(self.employees_table)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        add_employee_button = ModernButton("إضافة موظف جديد", color="#2ecc71")
        add_employee_button.clicked.connect(self.add_employee)
        buttons_layout.addWidget(add_employee_button)
        
        refresh_button = ModernButton("تحديث البيانات", color="#3498db")
        refresh_button.clicked.connect(self.load_employees)
        buttons_layout.addWidget(refresh_button)
        
        employees_layout.addLayout(buttons_layout)
        employees_group.setLayout(employees_layout)
        layout.addWidget(employees_group)
        
        self.employees_tab.setLayout(layout)
        
        # Load employees data
        self.load_employees()
    
    def setup_transfers_tab(self):
        """Set up the transfers tab."""
        layout = QVBoxLayout()
        
        # Create money transfer component
        self.money_transfer = MoneyTransferApp(self.token, self.api_url)
        layout.addWidget(self.money_transfer)
        
        self.transfers_tab.setLayout(layout)
    
    def setup_reports_tab(self):
        """Set up the reports tab."""
        layout = QVBoxLayout()
        
        # Reports options
        reports_group = ModernGroupBox("تقارير الفرع", "#9b59b6")
        reports_layout = QVBoxLayout()
        
        # Report types
        report_types_layout = QHBoxLayout()
        
        transactions_report_button = ModernButton("تقرير التحويلات", color="#3498db")
        transactions_report_button.clicked.connect(lambda: self.generate_report("transactions"))
        report_types_layout.addWidget(transactions_report_button)
        
        employees_report_button = ModernButton("تقرير الموظفين", color="#2ecc71")
        employees_report_button.clicked.connect(lambda: self.generate_report("employees"))
        report_types_layout.addWidget(employees_report_button)
        
        reports_layout.addLayout(report_types_layout)
        
        # Report filters
        filters_group = ModernGroupBox("تصفية التقارير", "#34495e")
        filters_layout = QFormLayout()
        
        self.date_from_input = QLineEdit()
        self.date_from_input.setPlaceholderText("YYYY-MM-DD")
        filters_layout.addRow("من تاريخ:", self.date_from_input)
        
        self.date_to_input = QLineEdit()
        self.date_to_input.setPlaceholderText("YYYY-MM-DD")
        filters_layout.addRow("إلى تاريخ:", self.date_to_input)
        
        filters_group.setLayout(filters_layout)
        reports_layout.addWidget(filters_group)
        
        # Report preview
        preview_group = ModernGroupBox("معاينة التقرير", "#e74c3c")
        preview_layout = QVBoxLayout()
        
        self.report_preview = QTableWidget()
        self.report_preview.setColumnCount(5)
        self.report_preview.setHorizontalHeaderLabels([
            "المعرف", "التاريخ", "النوع", "القيمة", "الحالة"
        ])
        self.report_preview.horizontalHeader().setStretchLastSection(True)
        self.report_preview.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        preview_layout.addWidget(self.report_preview)
        
        export_button = ModernButton("تصدير التقرير", color="#27ae60")
        export_button.clicked.connect(self.export_report)
        preview_layout.addWidget(export_button)
        
        preview_group.setLayout(preview_layout)
        reports_layout.addWidget(preview_group)
        
        reports_group.setLayout(reports_layout)
        layout.addWidget(reports_group)
        
        self.reports_tab.setLayout(layout)
    
    def setup_settings_tab(self):
        """Set up the settings tab."""
        layout = QVBoxLayout()
        
        # Branch settings
        branch_group = ModernGroupBox("معلومات الفرع", "#3498db")
        branch_layout = QFormLayout()
        
        self.branch_id_label = QLabel("جاري التحميل...")
        branch_layout.addRow("رمز الفرع:", self.branch_id_label)
        
        self.branch_name_field = QLabel("جاري التحميل...")
        branch_layout.addRow("اسم الفرع:", self.branch_name_field)
        
        self.branch_location_label = QLabel("جاري التحميل...")
        branch_layout.addRow("موقع الفرع:", self.branch_location_label)
        
        self.branch_governorate_label = QLabel("جاري التحميل...")
        branch_layout.addRow("المحافظة:", self.branch_governorate_label)
        
        branch_group.setLayout(branch_layout)
        layout.addWidget(branch_group)
        
        # Security settings
        security_group = ModernGroupBox("إعدادات الأمان", "#e74c3c")
        security_layout = QVBoxLayout()
        
        change_password_button = ModernButton("تغيير كلمة المرور", color="#3498db")
        change_password_button.clicked.connect(self.change_password)
        security_layout.addWidget(change_password_button)
        
        security_group.setLayout(security_layout)
        layout.addWidget(security_group)
        
        self.settings_tab.setLayout(layout)
    
    def refresh_dashboard_data(self):
        """Refresh all dashboard data."""
        from datetime import datetime
        
        # Update date
        current_date = datetime.now().strftime("%Y-%m-%d")
        self.date_label.setText(f"تاريخ اليوم: {current_date}")
        
        # Load statistics
        self.load_employee_stats()
        self.load_transaction_stats()
        self.load_recent_transactions()
    
    def load_branch_info(self):
        """Load branch information."""
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            print(f"Loading branch info for branch_id: {self.branch_id}")
            print(f"Using token: {self.token}")
            print(f"API URL: {self.api_url}/branches/{self.branch_id}")
            
            response = requests.get(f"{self.api_url}/branches/{self.branch_id}", headers=headers)
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.text}")
            
            if response.status_code == 200:
                branch = response.json()
                self.branch_name_label.setText(f"الفرع: {branch.get('name', '')}")
                self.branch_id_label.setText(branch.get('branch_id', ''))
                self.branch_name_field.setText(branch.get('name', ''))
                self.branch_location_label.setText(branch.get('location', ''))
                self.branch_governorate_label.setText(branch.get('governorate', ''))
            else:
                # Use empty values instead of hardcoded examples
                self.branch_name_label.setText("الفرع: ")
                self.branch_id_label.setText("")
                self.branch_name_field.setText("")
                self.branch_location_label.setText("")
                self.branch_governorate_label.setText("")
        except Exception as e:
            print(f"Error loading branch info: {e}")
            # Use empty values instead of hardcoded examples
            self.branch_name_label.setText("الفرع: ")
            self.branch_id_label.setText("")
            self.branch_name_field.setText("")
            self.branch_location_label.setText("")
            self.branch_governorate_label.setText("")
    
    def load_employee_stats(self):
        """Load employee statistics for this branch."""
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            response = requests.get(f"{self.api_url}/branches/{self.branch_id}/employees/stats/", headers=headers)
            
            if response.status_code == 200:
                stats = response.json()
                self.employees_count.setText(f"عدد الموظفين: {stats.get('total', 0)}")
                self.active_employees.setText(f"الموظفين النشطين: {stats.get('active', 0)}")
            else:
                # For testing/demo, use placeholder data
                self.employees_count.setText("عدد الموظفين: 0")
                self.active_employees.setText("الموظفين النشطين: 0")
        except Exception as e:
            print(f"Error loading employee stats: {e}")
            # For testing/demo, use placeholder data
            self.employees_count.setText("عدد الموظفين: 0")
            self.active_employees.setText("الموظفين النشطين: 0")
    
    def load_transaction_stats(self):
        """Load transaction statistics for this branch."""
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            response = requests.get(f"{self.api_url}/branches/{self.branch_id}/transactions/stats/", headers=headers)
            
            if response.status_code == 200:
                stats = response.json()
                self.transactions_count.setText(f"عدد التحويلات: {stats.get('total', 0)}")
                self.transactions_amount.setText(f"إجمالي مبالغ التحويلات: {stats.get('total_amount', 0)} ليرة سورية")
            else:
                # For testing/demo, use placeholder data
                self.transactions_count.setText("عدد التحويلات: 0")
                self.transactions_amount.setText("إجمالي مبالغ التحويلات: 0 ليرة سورية")
        except Exception as e:
            print(f"Error loading transaction stats: {e}")
            # For testing/demo, use placeholder data
            self.transactions_count.setText("عدد التحويلات: 0")
            self.transactions_amount.setText("إجمالي مبالغ التحويلات: 0 ليرة سورية")
    
    def load_recent_transactions(self):
        """Load recent transactions for this branch."""
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            response = requests.get(f"{self.api_url}/branches/{self.branch_id}/transactions/recent/", headers=headers)
            
            if response.status_code == 200:
                transactions = response.json()
                
                self.recent_transactions_table.setRowCount(len(transactions))
                
                for row, transaction in enumerate(transactions):
                    # Transaction ID
                    id_item = QTableWidgetItem(transaction.get("id", "")[:8] + "...")
                    self.recent_transactions_table.setItem(row, 0, id_item)
                    
                    # Sender
                    sender_item = QTableWidgetItem(transaction.get("sender", ""))
                    self.recent_transactions_table.setItem(row, 1, sender_item)
                    
                    # Receiver
                    receiver_item = QTableWidgetItem(transaction.get("receiver", ""))
                    self.recent_transactions_table.setItem(row, 2, receiver_item)
                    
                    # Amount
                    amount_item = QTableWidgetItem(f"{transaction.get('amount', 0)} {transaction.get('currency', '')}")
                    self.recent_transactions_table.setItem(row, 3, amount_item)
                    
                    # Date
                    date_item = QTableWidgetItem(transaction.get("date", ""))
                    self.recent_transactions_table.setItem(row, 4, date_item)
            else:
                # For testing/demo, use placeholder data
                self.load_placeholder_transactions()
        except Exception as e:
            print(f"Error loading recent transactions: {e}")
            # For testing/demo, use placeholder data
            self.load_placeholder_transactions()
    
    def load_placeholder_transactions(self):
        """Load placeholder transaction data for testing/demo."""
        placeholder_transactions = []
        
        self.recent_transactions_table.setRowCount(len(placeholder_transactions))
        
        for row, transaction in enumerate(placeholder_transactions):
            # Transaction ID
            id_item = QTableWidgetItem(transaction.get("id", ""))
            self.recent_transactions_table.setItem(row, 0, id_item)
            
            # Sender
            sender_item = QTableWidgetItem(transaction.get("sender", ""))
            self.recent_transactions_table.setItem(row, 1, sender_item)
            
            # Receiver
            receiver_item = QTableWidgetItem(transaction.get("receiver", ""))
            self.recent_transactions_table.setItem(row, 2, receiver_item)
            
            # Amount
            amount_item = QTableWidgetItem(f"{transaction.get('amount', 0)} {transaction.get('currency', '')}")
            self.recent_transactions_table.setItem(row, 3, amount_item)
            
            # Date
            date_item = QTableWidgetItem(transaction.get("date", ""))
            self.recent_transactions_table.setItem(row, 4, date_item)
    
    def add_employee(self):
        """Add a new employee."""
        # Use the AddEmployeeDialog from user_management_improved.py
        dialog = AddEmployeeDialog(is_admin=True, branch_id=self.branch_id, token=self.token)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            QMessageBox.information(self, "نجاح", "تمت إضافة الموظف بنجاح!")
            self.load_employees()  # Refresh the employee list
    
    def load_employees(self):
        """Load employees data for this branch."""
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            response = requests.get(f"{self.api_url}/branches/{self.branch_id}/employees/", headers=headers)
            
            if response.status_code == 200:
                employees = response.json()
                
                self.employees_table.setRowCount(len(employees))
                
                for row, employee in enumerate(employees):
                    # Username
                    username_item = QTableWidgetItem(employee.get("username", ""))
                    self.employees_table.setItem(row, 0, username_item)
                    
                    # Role
                    role_text = "موظف"
                    role_item = QTableWidgetItem(role_text)
                    self.employees_table.setItem(row, 1, role_item)
                    
                    # Status
                    status_item = QTableWidgetItem("نشط")
                    status_item.setForeground(QColor("#27ae60"))
                    self.employees_table.setItem(row, 2, status_item)
                    
                    # Creation date
                    date_item = QTableWidgetItem(employee.get("created_at", ""))
                    self.employees_table.setItem(row, 3, date_item)
                    
                    # Actions
                    actions_widget = QWidget()
                    actions_layout = QHBoxLayout(actions_widget)
                    actions_layout.setContentsMargins(0, 0, 0, 0)
                    
                    edit_button = QPushButton("تعديل")
                    edit_button.setStyleSheet("""
                        QPushButton {
                            background-color: #3498db;
                            color: white;
                            border-radius: 3px;
                            padding: 3px;
                        }
                        QPushButton:hover {
                            background-color: #2980b9;
                        }
                    """)
                    edit_button.clicked.connect(lambda checked, e=employee: self.edit_employee(e))
                    actions_layout.addWidget(edit_button)
                    
                    delete_button = QPushButton("حذف")
                    delete_button.setStyleSheet("""
                        QPushButton {
                            background-color: #e74c3c;
                            color: white;
                            border-radius: 3px;
                            padding: 3px;
                        }
                        QPushButton:hover {
                            background-color: #c0392b;
                        }
                    """)
                    delete_button.clicked.connect(lambda checked, e=employee: self.delete_employee(e))
                    actions_layout.addWidget(delete_button)
                    
                    self.employees_table.setCellWidget(row, 4, actions_widget)
            else:
                # For testing/demo, use placeholder data
                self.load_placeholder_employees()
        except Exception as e:
            print(f"Error loading employees: {e}")
            # For testing/demo, use placeholder data
            self.load_placeholder_employees()
    
    def load_placeholder_employees(self):
        """Load placeholder employee data for testing/demo."""
        placeholder_employees = []
        
        self.employees_table.setRowCount(len(placeholder_employees))
        
        for row, employee in enumerate(placeholder_employees):
            # Username
            username_item = QTableWidgetItem(employee.get("username", ""))
            self.employees_table.setItem(row, 0, username_item)
            
            # Role
            role_text = "موظف"
            role_item = QTableWidgetItem(role_text)
            self.employees_table.setItem(row, 1, role_item)
            
            # Status
            status_item = QTableWidgetItem("نشط")
            status_item.setForeground(QColor("#27ae60"))
            self.employees_table.setItem(row, 2, status_item)
            
            # Creation date
            date_item = QTableWidgetItem(employee.get("created_at", ""))
            self.employees_table.setItem(row, 3, date_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_button = QPushButton("تعديل")
            edit_button.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border-radius: 3px;
                    padding: 3px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            edit_button.clicked.connect(lambda checked, e=employee: self.edit_employee(e))
            actions_layout.addWidget(edit_button)
            
            delete_button = QPushButton("حذف")
            delete_button.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border-radius: 3px;
                    padding: 3px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            delete_button.clicked.connect(lambda checked, e=employee: self.delete_employee(e))
            actions_layout.addWidget(delete_button)
            
            self.employees_table.setCellWidget(row, 4, actions_widget)
    
    def edit_employee(self, employee):
        """Edit an employee."""
        QMessageBox.information(self, "تعديل موظف", f"سيتم فتح نافذة تعديل الموظف: {employee.get('username', '')}")
    
    def delete_employee(self, employee):
        """Delete an employee."""
        reply = QMessageBox.question(
            self, "تأكيد الحذف",
            f"هل أنت متأكد من حذف الموظف {employee.get('username', '')}؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
                response = requests.delete(f"{self.api_url}/users/{employee.get('id')}", headers=headers)
                
                if response.status_code == 200:
                    QMessageBox.information(self, "نجاح", "تم حذف الموظف بنجاح!")
                    self.load_employees()  # Refresh the list
                else:
                    QMessageBox.warning(self, "خطأ", f"فشل حذف الموظف: {response.status_code}")
            except Exception as e:
                print(f"Error deleting employee: {e}")
                QMessageBox.warning(self, "خطأ", f"تعذر حذف الموظف: {str(e)}")
    
    def search_user(self):
        """Open user search dialog."""
        dialog = UserSearchDialog(self.token, self.api_url, self)
        dialog.exec()
    
    def new_transfer(self):
        """Switch to transfers tab for a new transfer."""
        self.tab_widget.setCurrentIndex(2)  # Switch to transfers tab
    
    def generate_report(self, report_type):
        """Generate a report based on the selected type and filters."""
        date_from = self.date_from_input.text()
        date_to = self.date_to_input.text()
        
        # Clear previous report
        self.report_preview.setRowCount(0)
        
        # Set up columns based on report type
        if report_type == "transactions":
            self.report_preview.setColumnCount(6)
            self.report_preview.setHorizontalHeaderLabels([
                "رقم التحويل", "التاريخ", "المرسل", "المستلم", "المبلغ", "الحالة"
            ])
        elif report_type == "employees":
            self.report_preview.setColumnCount(4)
            self.report_preview.setHorizontalHeaderLabels([
                "اسم المستخدم", "الدور", "تاريخ الإنشاء", "الحالة"
            ])
        
        # Load report data
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            params = {
                "date_from": date_from if date_from else None,
                "date_to": date_to if date_to else None,
                "branch_id": self.branch_id
            }
            
            response = requests.get(f"{self.api_url}/reports/{report_type}/", params=params, headers=headers)
            
            if response.status_code == 200:
                report_data = response.json()
                items = report_data.get("items", [])
                
                self.report_preview.setRowCount(len(items))
                
                if report_type == "transactions":
                    for row, item in enumerate(items):
                        self.report_preview.setItem(row, 0, QTableWidgetItem(item.get("id", "")))
                        self.report_preview.setItem(row, 1, QTableWidgetItem(item.get("date", "")))
                        self.report_preview.setItem(row, 2, QTableWidgetItem(item.get("sender", "")))
                        self.report_preview.setItem(row, 3, QTableWidgetItem(item.get("receiver", "")))
                        self.report_preview.setItem(row, 4, QTableWidgetItem(f"{item.get('amount', 0)} {item.get('currency', '')}"))
                        
                        status_item = QTableWidgetItem(item.get("status", ""))
                        if item.get("status") == "completed":
                            status_item.setForeground(QColor("#27ae60"))
                        elif item.get("status") == "processing":
                            status_item.setForeground(QColor("#f39c12"))
                        else:
                            status_item.setForeground(QColor("#e74c3c"))
                        self.report_preview.setItem(row, 5, status_item)
                
                elif report_type == "employees":
                    for row, item in enumerate(items):
                        self.report_preview.setItem(row, 0, QTableWidgetItem(item.get("username", "")))
                        
                        role_text = "موظف"
                        self.report_preview.setItem(row, 1, QTableWidgetItem(role_text))
                        
                        self.report_preview.setItem(row, 2, QTableWidgetItem(item.get("created_at", "")))
                        
                        status_item = QTableWidgetItem("نشط")
                        status_item.setForeground(QColor("#27ae60"))
                        self.report_preview.setItem(row, 3, status_item)
            else:
                # For testing/demo, load placeholder data
                self.load_placeholder_report(report_type)
        except Exception as e:
            print(f"Error generating report: {e}")
            # For testing/demo, load placeholder data
            self.load_placeholder_report(report_type)
    
    def load_placeholder_report(self, report_type):
        """Load placeholder report data for testing/demo."""
        if report_type == "transactions":
            placeholder_items = []
            
            self.report_preview.setRowCount(len(placeholder_items))
            
            for row, item in enumerate(placeholder_items):
                self.report_preview.setItem(row, 0, QTableWidgetItem(item.get("id", "")))
                self.report_preview.setItem(row, 1, QTableWidgetItem(item.get("date", "")))
                self.report_preview.setItem(row, 2, QTableWidgetItem(item.get("sender", "")))
                self.report_preview.setItem(row, 3, QTableWidgetItem(item.get("receiver", "")))
                self.report_preview.setItem(row, 4, QTableWidgetItem(f"{item.get('amount', 0)} {item.get('currency', '')}"))
                
                status_item = QTableWidgetItem(item.get("status", ""))
                if item.get("status") == "completed":
                    status_item.setForeground(QColor("#27ae60"))
                elif item.get("status") == "processing":
                    status_item.setForeground(QColor("#f39c12"))
                else:
                    status_item.setForeground(QColor("#e74c3c"))
                self.report_preview.setItem(row, 5, status_item)
        
        elif report_type == "employees":
            placeholder_items = []
            
            self.report_preview.setRowCount(len(placeholder_items))
            
            for row, item in enumerate(placeholder_items):
                self.report_preview.setItem(row, 0, QTableWidgetItem(item.get("username", "")))
                
                role_text = "موظف"
                self.report_preview.setItem(row, 1, QTableWidgetItem(role_text))
                
                self.report_preview.setItem(row, 2, QTableWidgetItem(item.get("created_at", "")))
                
                status_item = QTableWidgetItem("نشط")
                status_item.setForeground(QColor("#27ae60"))
                self.report_preview.setItem(row, 3, status_item)
    
    def export_report(self):
        """Export the current report to a file."""
        QMessageBox.information(self, "تصدير التقرير", "سيتم تصدير التقرير إلى ملف")
    
    def change_password(self):
        """Change user password."""
        QMessageBox.information(self, "تغيير كلمة المرور", "سيتم فتح نافذة تغيير كلمة المرور")
