import sys
import requests
from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QWidget, QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QDialog, QLineEdit, QFormLayout, QComboBox, QGroupBox,
    QFrame, QSizePolicy
)
from PyQt6.QtGui import QFont, QColor, QIcon, QPixmap, QPalette
from PyQt6.QtCore import Qt, QTimer, QSize

class ModernGroupBox(QGroupBox):
    """Enhanced group box with consistent styling from both versions."""
    def __init__(self, title, color="#3498db"):
        super().__init__(title)
        self.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                font-size: 14px;
                border: 2px solid {color};
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 10px;
                background-color: rgba(255, 255, 255, 0.7);
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: {color};
            }}
        """)

class ModernButton(QPushButton):
    """Unified button styling with better hover effects."""
    def __init__(self, text, color="#2980b9", icon_name=None):
        super().__init__(text)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border-radius: 8px;
                padding: 10px 15px;
                font-weight: bold;
                font-size: 13px;
                text-align: center;
                border: none;
                min-width: 100px;
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
        if icon_name:
            self.setIcon(QIcon(icon_name))
            self.setIconSize(QSize(20, 20))
    
    def _adjust_color(self, hex_color, delta):
        """Improved color adjustment from old version."""
        if hex_color.startswith('#'):
            hex_color = hex_color[1:]
        r = min(255, max(0, int(hex_color[0:2], 16) + delta))
        g = min(255, max(0, int(hex_color[2:4], 16) + delta))
        b = min(255, max(0, int(hex_color[4:6], 16) + delta))
        return f"#{r:02x}{g:02x}{b:02x}"

class ModernTable(QTableWidget):
    """Enhanced table widget with better styling and performance."""
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f9f9f9;
                border-radius: 8px;
                border: 1px solid #ddd;
                gridline-color: #f0f0f0;
                selection-background-color: #3498db;
                selection-color: white;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #f0f0f0;
            }
        """)
        self.setAlternatingRowColors(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.verticalHeader().setVisible(False)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSortingEnabled(True)

class BranchManagerDashboard(QMainWindow):
    """Optimized branch manager dashboard combining both versions."""
    
    def __init__(self, branch_id, token=None, api_url="http://127.0.0.1:8000"):
        super().__init__()
        self.branch_id = branch_id
        self.token = token
        self.api_url = api_url
        
        # Window setup
        self.setWindowTitle("لوحة تحكم مدير الفرع")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                color: #2c3e50;
            }
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 8px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                color: #2c3e50;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 10px 15px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
                font-weight: bold;
            }
            QTabBar::tab:hover:!selected {
                background-color: #d6eaf8;
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # Header with gradient background (from old version)
        self.header_frame = QFrame()
        self.header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2c3e50, stop:1 #3498db);
                border-radius: 10px;
                min-height: 100px;
            }
        """)
        header_layout = QHBoxLayout(self.header_frame)
        
        # Title with branch info
        self.title = QLabel(f"👨‍💼 لوحة تحكم مدير الفرع | الفرع: {self.branch_id}")
        self.title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("color: white; margin: 10px;")
        header_layout.addWidget(self.title)
        
        main_layout.addWidget(self.header_frame)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_employees_tab()
        self.create_transactions_tab()
        self.create_settings_tab()
        
        main_layout.addWidget(self.tab_widget)
        
        # Footer (from old version)
        footer = QLabel("© 2025 نظام تحويل الأموال - جميع الحقوق محفوظة")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        main_layout.addWidget(footer)
        
        # Initialize data
        self.load_branch_info()
        self.refresh_data()
        
        # Set up refresh timer (every 5 minutes)
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(300000)  # 5 minutes
    
    def create_stat_card(self, title, value, color):
        """Create a statistics card widget (from old version)."""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 8px;
                border-left: 5px solid {color};
                padding: 10px;
                min-height: 100px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 16px;")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label)
        
        return card
    
    def create_dashboard_tab(self):
        """Create the dashboard tab with stats and recent transactions."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Stats row
        stats_layout = QHBoxLayout()
        
        # Employee stats
        self.employee_stats = self.create_stat_card("الموظفين", "0", "#3498db")
        stats_layout.addWidget(self.employee_stats)
        
        # Transaction stats
        self.transaction_stats = self.create_stat_card("التحويلات", "0", "#2ecc71")
        stats_layout.addWidget(self.transaction_stats)
        
        # Amount stats
        self.amount_stats = self.create_stat_card("إجمالي المبالغ", "0", "#e74c3c")
        stats_layout.addWidget(self.amount_stats)
        
        layout.addLayout(stats_layout)
        
        # Quick actions (from new version)
        actions_group = ModernGroupBox("إجراءات سريعة", "#9b59b6")
        actions_layout = QHBoxLayout()
        
        self.manage_employees_btn = ModernButton("إدارة الموظفين", color="#3498db")
        self.manage_employees_btn.clicked.connect(self.manage_employees)
        actions_layout.addWidget(self.manage_employees_btn)
        
        self.add_employee_btn = ModernButton("إضافة موظف جديد", color="#2ecc71")
        self.add_employee_btn.clicked.connect(self.add_employee)
        actions_layout.addWidget(self.add_employee_btn)
        
        self.new_transfer_btn = ModernButton("تحويل جديد", color="#e67e22")
        self.new_transfer_btn.clicked.connect(self.new_transfer)
        actions_layout.addWidget(self.new_transfer_btn)
        
        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)
        
        # Recent transactions
        recent_group = ModernGroupBox("أحدث التحويلات", "#3498db")
        recent_layout = QVBoxLayout()
        
        # Filter (from old version)
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("تصفية:"))
        
        self.dashboard_filter = QComboBox()
        self.dashboard_filter.addItems([
            "جميع التحويلات", 
            "التحويلات الواردة", 
            "التحويلات الصادرة",
            "التحويلات المتعلقة بالفرع"
        ])
        self.dashboard_filter.setCurrentIndex(3)
        self.dashboard_filter.currentIndexChanged.connect(self.load_recent_transactions)
        filter_layout.addWidget(self.dashboard_filter)
        
        filter_layout.addStretch()
        recent_layout.addLayout(filter_layout)
        
        # Transactions table
        self.recent_transactions_table = ModernTable()
        self.recent_transactions_table.setColumnCount(7)
        self.recent_transactions_table.setHorizontalHeaderLabels([
            "ID", "المرسل", "المستلم", "المبلغ", "العملة", "نوع التحويل", "التاريخ"
        ])
        recent_layout.addWidget(self.recent_transactions_table)
        
        recent_group.setLayout(recent_layout)
        layout.addWidget(recent_group)
        
        self.dashboard_tab = tab
        self.tab_widget.addTab(tab, "الرئيسية")
    
    def create_employees_tab(self):
        """Create the employees management tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Employees table
        employees_group = ModernGroupBox("إدارة الموظفين", "#2ecc71")
        employees_layout = QVBoxLayout()
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.refresh_employees_btn = ModernButton("تحديث البيانات", color="#3498db")
        self.refresh_employees_btn.clicked.connect(self.load_employees)
        controls_layout.addWidget(self.refresh_employees_btn)
        
        self.add_employee_tab_btn = ModernButton("إضافة موظف", color="#2ecc71")
        self.add_employee_tab_btn.clicked.connect(self.add_employee)
        controls_layout.addWidget(self.add_employee_tab_btn)
        
        employees_layout.addLayout(controls_layout)
        
        # Table
        self.employees_table = ModernTable()
        self.employees_table.setColumnCount(4)
        self.employees_table.setHorizontalHeaderLabels(["ID", "اسم المستخدم", "الوظيفة", "الفرع"])
        employees_layout.addWidget(self.employees_table)
        
        employees_group.setLayout(employees_layout)
        layout.addWidget(employees_group)
        
        self.employees_tab = tab
        self.tab_widget.addTab(tab, "الموظفون")
    
    def create_transactions_tab(self):
        """Create the transactions management tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Transactions table
        transactions_group = ModernGroupBox("إدارة التحويلات", "#e67e22")
        transactions_layout = QVBoxLayout()
        
        # Controls with filter
        controls_layout = QHBoxLayout()
        
        self.refresh_transactions_btn = ModernButton("تحديث التحويلات", color="#3498db")
        self.refresh_transactions_btn.clicked.connect(self.load_transactions)
        controls_layout.addWidget(self.refresh_transactions_btn)
        
        self.view_all_btn = ModernButton("عرض جميع التحويلات", color="#9b59b6")
        self.view_all_btn.clicked.connect(self.view_all_transactions)
        controls_layout.addWidget(self.view_all_btn)
        
        controls_layout.addWidget(QLabel("تصفية:"))
        
        self.transactions_filter = QComboBox()
        self.transactions_filter.addItems([
            "جميع التحويلات", 
            "التحويلات الواردة", 
            "التحويلات الصادرة",
            "التحويلات المتعلقة بالفرع"
        ])
        self.transactions_filter.setCurrentIndex(3)
        self.transactions_filter.currentIndexChanged.connect(self.load_transactions)
        controls_layout.addWidget(self.transactions_filter)
        
        transactions_layout.addLayout(controls_layout)
        
        # Table
        self.transactions_table = ModernTable()
        self.transactions_table.setColumnCount(7)
        self.transactions_table.setHorizontalHeaderLabels([
            "ID", "المرسل", "المستلم", "المبلغ", "العملة", "نوع التحويل", "التاريخ"
        ])
        transactions_layout.addWidget(self.transactions_table)
        
        transactions_group.setLayout(transactions_layout)
        layout.addWidget(transactions_group)
        
        self.transactions_tab = tab
        self.tab_widget.addTab(tab, "التحويلات")
    
    def create_settings_tab(self):
        """Create the settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Branch info
        branch_group = ModernGroupBox("معلومات الفرع", "#3498db")
        branch_layout = QFormLayout()
        
        self.branch_id_label = QLabel("جاري التحميل...")
        branch_layout.addRow("🆔 رقم الفرع:", self.branch_id_label)
        
        self.branch_name_label = QLabel("جاري التحميل...")
        branch_layout.addRow("🏢 اسم الفرع:", self.branch_name_label)
        
        self.branch_location_label = QLabel("جاري التحميل...")
        branch_layout.addRow("📍 الموقع:", self.branch_location_label)
        
        self.branch_governorate_label = QLabel("جاري التحميل...")
        branch_layout.addRow("محافظة الفرع:", self.branch_governorate_label)
        
        branch_group.setLayout(branch_layout)
        layout.addWidget(branch_group)
        
        # Settings
        settings_group = ModernGroupBox("الإعدادات", "#9b59b6")
        settings_layout = QVBoxLayout()
        
        self.change_password_btn = ModernButton("تغيير كلمة المرور", color="#e74c3c")
        self.change_password_btn.clicked.connect(self.change_password)
        settings_layout.addWidget(self.change_password_btn)
        
        self.refresh_btn = ModernButton("تحديث البيانات", color="#3498db")
        self.refresh_btn.clicked.connect(self.refresh_data)
        settings_layout.addWidget(self.refresh_btn)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        self.settings_tab = tab
        self.tab_widget.addTab(tab, "الإعدادات")
    
    def load_branch_info(self):
        """Load branch information from API."""
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            response = requests.get(f"{self.api_url}/branches/{self.branch_id}", headers=headers)
            
            if response.status_code == 200:
                branch = response.json()
                self.branch_id_label.setText(branch.get("branch_id", ""))
                self.branch_name_label.setText(branch.get("name", ""))
                self.branch_location_label.setText(branch.get("location", ""))
                self.branch_governorate_label.setText(branch.get("governorate", ""))
                self.title.setText(f"👨‍💼 لوحة تحكم مدير الفرع | الفرع: {branch.get('name', self.branch_id)}")
        except Exception as e:
            print(f"Error loading branch info: {e}")
    
    def refresh_data(self):
        """Refresh all data in the dashboard."""
        self.load_branch_info()
        self.load_employees()
        self.load_transactions()
        self.load_recent_transactions()
        self.update_stats()
    
    def update_stats(self):
        """Update statistics cards."""
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            
            # Employee count
            response = requests.get(f"{self.api_url}/branches/{self.branch_id}/employees/count", headers=headers)
            if response.status_code == 200:
                count = response.json().get("count", 0)
                self.employee_stats.findChild(QLabel, None).setText(str(count))
            
            # Transaction stats
            response = requests.get(f"{self.api_url}/branches/{self.branch_id}/transactions/stats", headers=headers)
            if response.status_code == 200:
                stats = response.json()
                self.transaction_stats.findChild(QLabel, None).setText(str(stats.get("count", 0)))
                self.amount_stats.findChild(QLabel, None).setText(f"{stats.get('total_amount', 0):,.2f}")
        except Exception as e:
            print(f"Error updating stats: {e}")
    
    def load_employees(self):
        """Load employees data."""
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            response = requests.get(f"{self.api_url}/branches/{self.branch_id}/employees", headers=headers)
            
            if response.status_code == 200:
                employees = response.json()
                self.display_employees(employees)
        except Exception as e:
            print(f"Error loading employees: {e}")
            QMessageBox.warning(self, "خطأ", f"تعذر تحميل بيانات الموظفين: {str(e)}")
    
    def display_employees(self, employees):
        """Display employees in the table."""
        self.employees_table.setRowCount(len(employees))
        
        for row, employee in enumerate(employees):
            self.employees_table.setItem(row, 0, QTableWidgetItem(str(employee.get("id", ""))))
            self.employees_table.setItem(row, 1, QTableWidgetItem(employee.get("username", "")))
            self.employees_table.setItem(row, 2, QTableWidgetItem(employee.get("role", "")))
            self.employees_table.setItem(row, 3, QTableWidgetItem(str(employee.get("branch_id", ""))))
    
    def load_transactions(self):
        """Load transactions based on current filter."""
        try:
            filter_type = self.get_filter_type(self.transactions_filter.currentIndex())
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            
            response = requests.get(
                f"{self.api_url}/branches/{self.branch_id}/transactions",
                params={"filter": filter_type},
                headers=headers
            )
            
            if response.status_code == 200:
                transactions = response.json()
                self.display_transactions(transactions)
        except Exception as e:
            print(f"Error loading transactions: {e}")
            QMessageBox.warning(self, "خطأ", f"تعذر تحميل بيانات التحويلات: {str(e)}")
    
    def load_recent_transactions(self):
        """Load recent transactions for dashboard."""
        try:
            filter_type = self.get_filter_type(self.dashboard_filter.currentIndex())
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            
            response = requests.get(
                f"{self.api_url}/branches/{self.branch_id}/transactions/recent",
                params={"filter": filter_type, "limit": 5},
                headers=headers
            )
            
            if response.status_code == 200:
                transactions = response.json()
                self.display_recent_transactions(transactions)
        except Exception as e:
            print(f"Error loading recent transactions: {e}")
    
    def display_transactions(self, transactions):
        """Display transactions in the table."""
        self.transactions_table.setRowCount(len(transactions))
        
        for row, transaction in enumerate(transactions):
            self.fill_transaction_row(row, transaction)
    
    def display_recent_transactions(self, transactions):
        """Display recent transactions in dashboard table."""
        self.recent_transactions_table.setRowCount(len(transactions))
        
        for row, transaction in enumerate(transactions):
            self.fill_transaction_row(row, transaction, self.recent_transactions_table)
    
    def fill_transaction_row(self, row, transaction, table=None):
        """Fill a transaction row in the specified table."""
        if table is None:
            table = self.transactions_table
        
        table.setItem(row, 0, QTableWidgetItem(transaction.get("id", "")))
        table.setItem(row, 1, QTableWidgetItem(transaction.get("sender", "")))
        table.setItem(row, 2, QTableWidgetItem(transaction.get("receiver", "")))
        table.setItem(row, 3, QTableWidgetItem(str(transaction.get("amount", 0))))
        table.setItem(row, 4, QTableWidgetItem(transaction.get("currency", "")))
        
        # Determine transaction type
        transaction_type = self.determine_transaction_type(transaction)
        type_item = QTableWidgetItem(transaction_type)
        
        # Color code based on type
        if transaction_type == "وارد":
            type_item.setBackground(QColor("#d5f5e3"))  # Light green
        elif transaction_type == "صادر":
            type_item.setBackground(QColor("#fadbd8"))  # Light red
        
        table.setItem(row, 5, type_item)
        table.setItem(row, 6, QTableWidgetItem(transaction.get("date", "")))
    
    def determine_transaction_type(self, transaction):
        """Determine if transaction is incoming/outgoing (from old version)."""
        if str(transaction.get("branch_id", "")) == str(self.branch_id):
            return "صادر"
        elif transaction.get("receiver_governorate", "") == transaction.get("branch_governorate", ""):
            return "وارد"
        return "غير مرتبط"
    
    def get_filter_type(self, index):
        """Convert filter index to API parameter."""
        return ["all", "incoming", "outgoing", "branch_related"][index]
    
    def manage_employees(self):
        """Open employee management dialog."""
        from ui.user_management_improved import UserManagement
        dialog = UserManagement(self.branch_id, token=self.token)
        dialog.exec()
        self.load_employees()
    
    def add_employee(self):
        """Open add employee dialog."""
        from ui.user_management_improved import AddEmployeeDialog
        dialog = AddEmployeeDialog(self.branch_id, token=self.token)
        if dialog.exec():
            self.load_employees()
    
    def new_transfer(self):
        """Open new transfer dialog."""
        from ui.money_transfer_improved import MoneyTransferDialog
        dialog = MoneyTransferDialog(self.branch_id, token=self.token)
        if dialog.exec():
            self.load_transactions()
            self.load_recent_transactions()
            self.update_stats()
    
    def view_all_transactions(self):
        """Switch to transactions tab and load all transactions."""
        self.tab_widget.setCurrentWidget(self.transactions_tab)
        self.transactions_filter.setCurrentIndex(0)  # Show all
        self.load_transactions()
    
    def change_password(self):
        """Open change password dialog."""
        from ui.change_password import ChangePasswordDialog
        dialog = ChangePasswordDialog(token=self.token)
        dialog.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BranchManagerDashboard(branch_id="1", token="your_token_here")
    window.show()
    sys.exit(app.exec())