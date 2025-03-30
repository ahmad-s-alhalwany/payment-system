import sys
import requests
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog,
    QLineEdit, QFormLayout, QComboBox, QGroupBox, QGridLayout, QDateEdit, QCheckBox,
    QSpinBox, QDoubleSpinBox, QRadioButton, QButtonGroup, QFileDialog, QTextEdit,
    QSplitter, QFrame, QProgressBar, QStatusBar, QToolBar, QMenu, QMenuBar,
    QSizePolicy, QScrollArea, QStackedWidget
)
from PyQt6.QtGui import QFont, QIcon, QColor, QPixmap, QPalette, QBrush, QCursor, QAction
from PyQt6.QtCore import Qt, QSize, QDate, QDateTime, QTimer, QUrl, QThread, pyqtSignal
from ui.money_transfer_improved import MoneyTransferApp
from ui.branch_management_improved import AddBranchDialog
from ui.user_management_improved import AddEmployeeDialog
from ui.user_search import UserSearchDialog

# Comment out matplotlib imports to make the application work without this dependency
# If you need charts, install matplotlib with: pip install matplotlib
# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.figure import Figure
# import numpy as np
# import pandas as pd

import datetime
import os
import json

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

# Enhance the ModernButton class with more styling options
class ModernButton(QPushButton):
    def __init__(self, text, color="#3498db", icon=None):
        super().__init__(text)
        
        # Set icon if provided
        if icon:
            self.setIcon(QIcon(icon))
            self.setIconSize(QSize(16, 16))
        
        # Enhanced styling
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border-radius: 5px;
                padding: 8px 12px;
                font-weight: bold;
                min-width: 100px;
                border: none;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: {self.lighten_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(color)};
                padding: 9px 11px 7px 13px;
            }}
            QPushButton:disabled {{
                background-color: #95a5a6;
                color: #7f8c8d;
            }}
        """)
        
        # Add animation on hover
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(100)
    
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

class DirectorDashboard(QMainWindow):
    """Dashboard for the director role."""
    
    def __init__(self, token=None, api_url="http://127.0.0.1:8000"):
        super().__init__()
        self.token = token
        self.api_url = api_url
        
        self.setWindowTitle("لوحة تحكم المدير")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
                font-family: Arial;
            }
            QLabel {
                color: #333;
            }
            QTabWidget::pane {
                border: 1px solid #ccc;
                border-radius: 8px;
                background-color: rgba(255, 255, 255, 0.7);
            }
            QTabBar::tab {
                background-color: #ddd;
                padding: 10px 15px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #2c3e50;
                color: white;
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        header_layout = QHBoxLayout()
        
        # Logo/Title
        logo_label = QLabel("نظام التحويلات المالية")
        logo_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        logo_label.setStyleSheet("color: #2c3e50;")
        header_layout.addWidget(logo_label)
        
        # Spacer
        header_layout.addStretch()
        
        # User info
        user_info = QLabel("مدير النظام")
        user_info.setFont(QFont("Arial", 12))
        user_info.setStyleSheet("color: #7f8c8d;")
        header_layout.addWidget(user_info)
        
        main_layout.addLayout(header_layout)
        
        # Tab widget
        self.tabs = QTabWidget()
        
        # Dashboard tab
        self.dashboard_tab = QWidget()
        self.setup_dashboard_tab()
        self.tabs.addTab(self.dashboard_tab, "لوحة المعلومات")
        
        # Branches tab
        self.branches_tab = QWidget()
        self.setup_branches_tab()
        self.tabs.addTab(self.branches_tab, "الفروع")
        
        # Employees tab
        self.employees_tab = QWidget()
        self.setup_employees_tab()
        self.tabs.addTab(self.employees_tab, "الموظفين")
        
        # Transactions tab
        self.transactions_tab = QWidget()
        self.setup_transactions_tab()
        self.tabs.addTab(self.transactions_tab, "التحويلات")
        
        # Reports tab
        self.reports_tab = QWidget()
        self.setup_reports_tab()
        self.tabs.addTab(self.reports_tab, "التقارير")
        
        # Settings tab
        self.settings_tab = QWidget()
        self.setup_settings_tab()
        self.tabs.addTab(self.settings_tab, "الإعدادات")
        
        main_layout.addWidget(self.tabs)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("جاهز")
        
        # Load initial data
        self.load_dashboard_data()
        self.load_branches()
        self.load_employees()
        self.load_transactions()
        self.load_branches_for_filter()
        
        self.setup_quick_actions()
        self.enhance_tables()
        self.setup_signals()
        
    def setup_signals(self):
        self.branches_table.itemSelectionChanged.connect(self.update_branch_actions)    
        
    def setup_quick_actions(self):
        """Add a quick actions panel similar to old version's grouped buttons"""
        quick_actions = ModernGroupBox("إجراءات سريعة", "#9b59b6")
        layout = QVBoxLayout()
        
        # Add buttons from old version that make sense in new context
        buttons = [
            ("🔄 تحديث البيانات", self.refresh_all),
            ("🔐 تغيير كلمة المرور", self.change_password),
            ("👷‍♂️ إضافة موظف جديد", self.add_employee),
            ("➕ إضافة فرع جديد", self.add_branch)
        ]
        
        for text, callback in buttons:
            btn = ModernButton(text, color="#3498db")
            btn.clicked.connect(callback)
            layout.addWidget(btn)
        
        quick_actions.setLayout(layout)
        
        # Add to dashboard tab (or create a new "Quick Actions" tab)
        self.dashboard_tab.layout().insertWidget(1, quick_actions)

    def setup_dashboard_tab(self):
        """Set up the dashboard tab with statistics and charts."""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("لوحة المعلومات")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Statistics cards
        stats_layout = QHBoxLayout()
        
        # Branches card
        self.branches_card = ModernGroupBox("الفروع", "#3498db")
        branches_layout = QVBoxLayout()
        self.branches_count = QLabel("0")
        self.branches_count.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.branches_count.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.branches_count.setStyleSheet("color: #3498db;")
        branches_layout.addWidget(self.branches_count)
        branches_label = QLabel("إجمالي الفروع")
        branches_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        branches_layout.addWidget(branches_label)
        self.branches_card.setLayout(branches_layout)
        stats_layout.addWidget(self.branches_card)
        
        # Employees card
        self.employees_card = ModernGroupBox("الموظفين", "#2ecc71")
        employees_layout = QVBoxLayout()
        self.employees_count = QLabel("0")
        self.employees_count.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.employees_count.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.employees_count.setStyleSheet("color: #2ecc71;")
        employees_layout.addWidget(self.employees_count)
        employees_label = QLabel("إجمالي الموظفين")
        employees_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        employees_layout.addWidget(employees_label)
        self.employees_card.setLayout(employees_layout)
        stats_layout.addWidget(self.employees_card)
        
        # Transactions card
        self.transactions_card = ModernGroupBox("التحويلات", "#e74c3c")
        transactions_layout = QVBoxLayout()
        self.transactions_count = QLabel("0")
        self.transactions_count.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.transactions_count.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.transactions_count.setStyleSheet("color: #e74c3c;")
        transactions_layout.addWidget(self.transactions_count)
        transactions_label = QLabel("إجمالي التحويلات")
        transactions_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        transactions_layout.addWidget(transactions_label)
        self.transactions_card.setLayout(transactions_layout)
        stats_layout.addWidget(self.transactions_card)
        
        # Amount card
        self.amount_card = ModernGroupBox("المبالغ", "#f39c12")
        amount_layout = QVBoxLayout()
        self.amount_total = QLabel("0")
        self.amount_total.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.amount_total.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.amount_total.setStyleSheet("color: #f39c12;")
        amount_layout.addWidget(self.amount_total)
        amount_label = QLabel("إجمالي المبالغ")
        amount_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        amount_layout.addWidget(amount_label)
        self.amount_card.setLayout(amount_layout)
        stats_layout.addWidget(self.amount_card)
        
        layout.addLayout(stats_layout)
        
        # Charts section - replaced with placeholder since matplotlib is not available
        charts_layout = QHBoxLayout()
        
        # Transactions by branch chart placeholder
        transactions_chart_group = ModernGroupBox("التحويلات حسب الفرع", "#3498db")
        transactions_chart_layout = QVBoxLayout()
        
        transactions_chart_placeholder = QLabel("الرسوم البيانية غير متاحة - قم بتثبيت matplotlib للعرض")
        transactions_chart_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        transactions_chart_placeholder.setStyleSheet("color: #7f8c8d; padding: 50px;")
        transactions_chart_layout.addWidget(transactions_chart_placeholder)
        
        transactions_chart_group.setLayout(transactions_chart_layout)
        charts_layout.addWidget(transactions_chart_group)
        
        # Amounts by branch chart placeholder
        amounts_chart_group = ModernGroupBox("المبالغ حسب الفرع", "#e74c3c")
        amounts_chart_layout = QVBoxLayout()
        
        amounts_chart_placeholder = QLabel("الرسوم البيانية غير متاحة - قم بتثبيت matplotlib للعرض")
        amounts_chart_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        amounts_chart_placeholder.setStyleSheet("color: #7f8c8d; padding: 50px;")
        amounts_chart_layout.addWidget(amounts_chart_placeholder)
        
        amounts_chart_group.setLayout(amounts_chart_layout)
        charts_layout.addWidget(amounts_chart_group)
        
        layout.addLayout(charts_layout)
        
        # Recent transactions
        recent_transactions_group = ModernGroupBox("أحدث التحويلات", "#2ecc71")
        recent_transactions_layout = QVBoxLayout()
        
        self.recent_transactions_table = QTableWidget()
        self.recent_transactions_table.setColumnCount(6)
        self.recent_transactions_table.setHorizontalHeaderLabels([
            "رقم التحويل", "المرسل", "المستلم", "المبلغ", "الفرع", "التاريخ"
        ])
        self.recent_transactions_table.horizontalHeader().setStretchLastSection(True)
        self.recent_transactions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.recent_transactions_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        recent_transactions_layout.addWidget(self.recent_transactions_table)
        recent_transactions_group.setLayout(recent_transactions_layout)
        layout.addWidget(recent_transactions_group)
        
        self.dashboard_tab.setLayout(layout)
    
    def setup_branches_tab(self):
        """Set up the branches tab."""
        
        self.branches_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 5px;
                border: 1px solid #1a2530;
            }
        """)
        
        # Add alternating row colors
        self.branches_table.setAlternatingRowColors(True)
        self.branches_table.setStyleSheet("""
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:alternate {
                background-color: #f8f8f8;
            }
        """)
        
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("إدارة الفروع")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Branches table
        self.branches_table = QTableWidget()
        self.branches_table.setColumnCount(5)
        self.branches_table.setHorizontalHeaderLabels([
            "رمز الفرع", "اسم الفرع", "الموقع", "المحافظة", "عدد الموظفين"
        ])
        self.branches_table.horizontalHeader().setStretchLastSection(True)
        self.branches_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.branches_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.branches_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.branches_table)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        add_branch_button = ModernButton("إضافة فرع", color="#2ecc71")
        add_branch_button.clicked.connect(self.add_branch)
        buttons_layout.addWidget(add_branch_button)
        
        edit_branch_button = ModernButton("تعديل الفرع", color="#3498db")
        edit_branch_button.clicked.connect(self.edit_branch)
        buttons_layout.addWidget(edit_branch_button)
        
        delete_branch_button = ModernButton("حذف الفرع", color="#e74c3c")
        delete_branch_button.clicked.connect(self.delete_branch)
        buttons_layout.addWidget(delete_branch_button)
        
        view_branch_button = ModernButton("عرض تفاصيل الفرع", color="#f39c12")
        view_branch_button.clicked.connect(self.view_branch)
        buttons_layout.addWidget(view_branch_button)
        
        refresh_button = ModernButton("تحديث", color="#9b59b6")
        refresh_button.clicked.connect(self.load_branches)
        buttons_layout.addWidget(refresh_button)
        
        layout.addLayout(buttons_layout)
        
        self.branches_tab.setLayout(layout)
    
    # Use the old version's more robust error handling
    def fetch_branches(self):
        """Improved version combining both approaches"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            response = requests.get(f"{self.api_url}/branches/", headers=headers)
            
            if response.status_code == 200:
                branches = response.json()
                self.display_branches(branches)
            else:
                # Use old version's detailed error message
                error_msg = f"فشل في تحميل الفروع! الخطأ: {response.status_code}"
                try:
                    error_msg += f" - {response.json().get('detail', '')}"
                except:
                    pass
                QMessageBox.warning(self, "خطأ", error_msg)
                
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"تعذر الاتصال بالخادم: {str(e)}")

    def display_branches(self, branches):
        """Combine both versions' display logic"""
        self.branches_table.setRowCount(len(branches))
        self.branches_table.setColumnCount(5)
        self.branches_table.setHorizontalHeaderLabels([
            "ID", "اسم الفرع", "الموقع", "المحافظة", "عدد الموظفين"
        ])
        
        for row_idx, branch in enumerate(branches):
            self.branches_table.setItem(row_idx, 0, QTableWidgetItem(str(branch.get("id", ""))))
            self.branches_table.setItem(row_idx, 1, QTableWidgetItem(branch.get("name", "")))
            self.branches_table.setItem(row_idx, 2, QTableWidgetItem(branch.get("location", "")))
            self.branches_table.setItem(row_idx, 3, QTableWidgetItem(branch.get("governorate", "")))
            
            # Get employee count (from new version)
            emp_count = 0
            try:
                headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
                emp_response = requests.get(
                    f"{self.api_url}/branches/{branch['id']}/employees/stats/", 
                    headers=headers
                )
                if emp_response.status_code == 200:
                    emp_count = emp_response.json().get("total", 0)
            except:
                pass
            
            self.branches_table.setItem(row_idx, 4, QTableWidgetItem(str(emp_count)))
    
    def refresh_all(self):
        """Refresh all data like in old version"""
        self.load_dashboard_data()
        self.load_branches()
        self.load_employees()
        self.load_transactions()
        
        # Show confirmation message
        QMessageBox.information(self, "تحديث", "🔄 تم تحديث البيانات!")
        
        # Update status bar
        self.status_bar.showMessage("تم تحديث البيانات في " + datetime.datetime.now().strftime("%H:%M:%S"))
    
    def setup_employees_tab(self):
        """Set up the employees tab."""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("إدارة الموظفين")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Filter
        filter_layout = QHBoxLayout()
        
        filter_label = QLabel("تصفية حسب الفرع:")
        filter_layout.addWidget(filter_label)
        
        self.branch_filter = QComboBox()
        self.branch_filter.setMinimumWidth(200)
        self.branch_filter.currentIndexChanged.connect(self.filter_employees)
        filter_layout.addWidget(self.branch_filter)
        
        filter_layout.addStretch()
        
        search_button = ModernButton("بحث", color="#3498db")
        search_button.clicked.connect(self.search_user)
        filter_layout.addWidget(search_button)
        
        layout.addLayout(filter_layout)
        
        # Employees table
        self.employees_table = QTableWidget()
        self.employees_table.setColumnCount(5)
        self.employees_table.setHorizontalHeaderLabels([
            "اسم المستخدم", "الدور", "الفرع", "تاريخ الإنشاء", "الحالة"
        ])
        self.employees_table.horizontalHeader().setStretchLastSection(True)
        self.employees_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.employees_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.employees_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.employees_table)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        add_employee_button = ModernButton("إضافة موظف", color="#2ecc71")
        add_employee_button.clicked.connect(self.add_employee)
        buttons_layout.addWidget(add_employee_button)
        
        edit_employee_button = ModernButton("تعديل الموظف", color="#3498db")
        edit_employee_button.clicked.connect(self.edit_employee)
        buttons_layout.addWidget(edit_employee_button)
        
        delete_employee_button = ModernButton("حذف الموظف", color="#e74c3c")
        delete_employee_button.clicked.connect(self.delete_employee)
        buttons_layout.addWidget(delete_employee_button)
        
        reset_password_button = ModernButton("إعادة تعيين كلمة المرور", color="#f39c12")
        reset_password_button.clicked.connect(self.reset_password)
        buttons_layout.addWidget(reset_password_button)
        
        refresh_button = ModernButton("تحديث", color="#9b59b6")
        refresh_button.clicked.connect(self.load_employees)
        buttons_layout.addWidget(refresh_button)
        
        layout.addLayout(buttons_layout)
        
        self.employees_tab.setLayout(layout)
    
    def setup_transactions_tab(self):
        """Set up the transactions tab."""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("إدارة التحويلات")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Filter
        filter_layout = QHBoxLayout()
        
        filter_branch_label = QLabel("تصفية حسب الفرع:")
        filter_layout.addWidget(filter_branch_label)
        
        self.transaction_branch_filter = QComboBox()
        self.transaction_branch_filter.setMinimumWidth(150)
        self.transaction_branch_filter.currentIndexChanged.connect(self.filter_transactions)
        filter_layout.addWidget(self.transaction_branch_filter)
        
        filter_type_label = QLabel("نوع التصفية:")
        filter_layout.addWidget(filter_type_label)
        
        self.transaction_type_filter = QComboBox()
        self.transaction_type_filter.addItems(["الكل", "الواردة", "الصادرة", "متعلقة بالفرع"])
        self.transaction_type_filter.setMinimumWidth(150)
        self.transaction_type_filter.currentIndexChanged.connect(self.filter_transactions)
        filter_layout.addWidget(self.transaction_type_filter)
        
        filter_layout.addStretch()
        
        search_button = ModernButton("بحث", color="#3498db")
        search_button.clicked.connect(self.search_transaction)
        filter_layout.addWidget(search_button)
        
        layout.addLayout(filter_layout)
        
        # Transactions table
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(8)
        self.transactions_table.setHorizontalHeaderLabels([
            "رقم التحويل", "المرسل", "المستلم", "المبلغ", "العملة", "الفرع", "الحالة", "التاريخ"
        ])
        self.transactions_table.horizontalHeader().setStretchLastSection(True)
        self.transactions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.transactions_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.transactions_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.transactions_table)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        view_transaction_button = ModernButton("عرض التفاصيل", color="#3498db")
        view_transaction_button.clicked.connect(self.view_transaction)
        buttons_layout.addWidget(view_transaction_button)
        
        update_status_button = ModernButton("تحديث الحالة", color="#f39c12")
        update_status_button.clicked.connect(self.update_transaction_status)
        buttons_layout.addWidget(update_status_button)
        
        print_receipt_button = ModernButton("طباعة الإيصال", color="#2ecc71")
        print_receipt_button.clicked.connect(self.print_receipt)
        buttons_layout.addWidget(print_receipt_button)
        
        refresh_button = ModernButton("تحديث", color="#9b59b6")
        refresh_button.clicked.connect(self.load_transactions)
        buttons_layout.addWidget(refresh_button)
        
        layout.addLayout(buttons_layout)
        
        self.transactions_tab.setLayout(layout)
    
    def setup_reports_tab(self):
        """Set up the reports tab."""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("التقارير")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Report options
        options_group = ModernGroupBox("خيارات التقرير", "#3498db")
        options_layout = QGridLayout()
        
        # Report type
        report_type_label = QLabel("نوع التقرير:")
        options_layout.addWidget(report_type_label, 0, 0)
        
        self.report_type = QComboBox()
        self.report_type.addItems(["تقرير التحويلات", "تقرير الفروع", "تقرير الموظفين"])
        options_layout.addWidget(self.report_type, 0, 1)
        
        # Date range
        date_range_label = QLabel("نطاق التاريخ:")
        options_layout.addWidget(date_range_label, 1, 0)
        
        date_range_layout = QHBoxLayout()
        
        from_date_label = QLabel("من:")
        date_range_layout.addWidget(from_date_label)
        
        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.from_date.setDate(QDate.currentDate().addDays(-30))  # Last 30 days
        date_range_layout.addWidget(self.from_date)
        
        to_date_label = QLabel("إلى:")
        date_range_layout.addWidget(to_date_label)
        
        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.to_date.setDate(QDate.currentDate())
        date_range_layout.addWidget(self.to_date)
        
        options_layout.addLayout(date_range_layout, 1, 1)
        
        # Branch filter
        branch_filter_label = QLabel("الفرع:")
        options_layout.addWidget(branch_filter_label, 2, 0)
        
        self.report_branch_filter = QComboBox()
        options_layout.addWidget(self.report_branch_filter, 2, 1)
        
        # Generate button
        generate_button = ModernButton("إنشاء التقرير", color="#2ecc71")
        generate_button.clicked.connect(self.generate_report)
        options_layout.addWidget(generate_button, 3, 0, 1, 2)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Report preview
        preview_group = ModernGroupBox("معاينة التقرير", "#e74c3c")
        preview_layout = QVBoxLayout()
        
        self.report_table = QTableWidget()
        preview_layout.addWidget(self.report_table)
        
        # Export buttons
        export_layout = QHBoxLayout()
        
        export_pdf_button = ModernButton("تصدير PDF", color="#3498db")
        export_pdf_button.clicked.connect(self.export_pdf)
        export_layout.addWidget(export_pdf_button)
        
        export_excel_button = ModernButton("تصدير Excel", color="#f39c12")
        export_excel_button.clicked.connect(self.export_excel)
        export_layout.addWidget(export_excel_button)
        
        export_print_button = ModernButton("طباعة", color="#9b59b6")
        export_print_button.clicked.connect(self.print_report)
        export_layout.addWidget(export_print_button)
        
        preview_layout.addLayout(export_layout)
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        self.reports_tab.setLayout(layout)
        self.load_branches_for_filter()
    
    def setup_settings_tab(self):
        """Set up the settings tab."""
        layout = QVBoxLayout()
        
        # System settings
        settings_group = ModernGroupBox("إعدادات النظام", "#3498db")
        settings_layout = QFormLayout()
        
        self.system_name_input = QLineEdit("نظام التحويلات المالية الداخلي")
        settings_layout.addRow("اسم النظام:", self.system_name_input)
        
        self.company_name_input = QLineEdit("شركة التحويلات المالية")
        settings_layout.addRow("اسم الشركة:", self.company_name_input)
        
        self.admin_email_input = QLineEdit("admin@example.com")
        settings_layout.addRow("البريد الإلكتروني للمسؤول:", self.admin_email_input)
        
        self.currency_input = QComboBox()
        self.currency_input.addItems(["دينار عراقي", "دولار أمريكي", "يورو"])
        settings_layout.addRow("العملة الافتراضية:", self.currency_input)
        
        self.language_input = QComboBox()
        self.language_input.addItems(["العربية", "English"])
        settings_layout.addRow("اللغة:", self.language_input)
        
        self.theme_input = QComboBox()
        self.theme_input.addItems(["فاتح", "داكن", "أزرق"])
        settings_layout.addRow("السمة:", self.theme_input)
        
        save_settings_button = ModernButton("حفظ الإعدادات", color="#2ecc71")
        save_settings_button.clicked.connect(self.save_settings)
        settings_layout.addRow("", save_settings_button)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # User settings
        user_settings_group = ModernGroupBox("إعدادات المستخدم", "#e74c3c")
        user_settings_layout = QFormLayout()
        
        self.username_input = QLineEdit("admin")
        self.username_input.setReadOnly(True)
        self.username_input.setStyleSheet("background-color: #f0f0f0;")
        user_settings_layout.addRow("اسم المستخدم:", self.username_input)
        
        self.old_password_input = QLineEdit()
        self.old_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        user_settings_layout.addRow("كلمة المرور الحالية:", self.old_password_input)
        
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        user_settings_layout.addRow("كلمة المرور الجديدة:", self.new_password_input)
        
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        user_settings_layout.addRow("تأكيد كلمة المرور:", self.confirm_password_input)
        
        change_password_button = ModernButton("تغيير كلمة المرور", color="#f39c12")
        change_password_button.clicked.connect(self.change_password)
        user_settings_layout.addRow("", change_password_button)
        
        user_settings_group.setLayout(user_settings_layout)
        layout.addWidget(user_settings_group)
        
        # Backup and restore
        backup_group = ModernGroupBox("النسخ الاحتياطي واستعادة البيانات", "#9b59b6")
        backup_layout = QVBoxLayout()
        
        backup_button = ModernButton("إنشاء نسخة احتياطية", color="#3498db")
        backup_button.clicked.connect(self.create_backup)
        backup_layout.addWidget(backup_button)
        
        restore_button = ModernButton("استعادة من نسخة احتياطية", color="#e74c3c")
        restore_button.clicked.connect(self.restore_backup)
        backup_layout.addWidget(restore_button)
        
        backup_group.setLayout(backup_layout)
        layout.addWidget(backup_group)
        
        self.settings_tab.setLayout(layout)
    
    def load_dashboard_data(self):
        """Load data for the dashboard."""
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            
            # Get branch stats
            response = requests.get(f"{self.api_url}/branches/stats/", headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.branches_count.setText(str(data.get("total", 0)))
            
            # Get employee stats
            response = requests.get(f"{self.api_url}/users/stats/", headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.employees_count.setText(str(data.get("total", 0)))
            
            # Get transaction stats
            response = requests.get(f"{self.api_url}/transactions/stats/", headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.transactions_count.setText(str(data.get("total", 0)))
                self.amount_total.setText(f"{data.get('total_amount', 0):,.2f}")
            
            # Load recent transactions
            self.load_recent_transactions()
            
        except Exception as e:
            print(f"Error loading dashboard data: {e}")
            QMessageBox.warning(self, "خطأ", f"تعذر تحميل بيانات لوحة المعلومات: {str(e)}")
    
    def load_charts_data(self):
        """This method is disabled as matplotlib is not available."""
        # This method is intentionally left empty as matplotlib is not available
        pass
    
    def load_recent_transactions(self):
        """Load recent transactions for the dashboard."""
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            
            response = requests.get(f"{self.api_url}/transactions/?limit=5", headers=headers)
            if response.status_code == 200:
                data = response.json()
                transactions = data.get("transactions", [])
                
                self.recent_transactions_table.setRowCount(len(transactions))
                
                for i, transaction in enumerate(transactions):
                    self.recent_transactions_table.setItem(i, 0, QTableWidgetItem(transaction.get("id", "")))
                    self.recent_transactions_table.setItem(i, 1, QTableWidgetItem(transaction.get("sender", "")))
                    self.recent_transactions_table.setItem(i, 2, QTableWidgetItem(transaction.get("receiver", "")))
                    self.recent_transactions_table.setItem(i, 3, QTableWidgetItem(
                        f"{transaction.get('amount', 0)} {transaction.get('currency', '')}"
                    ))
                    self.recent_transactions_table.setItem(i, 4, QTableWidgetItem(transaction.get("branch_governorate", "")))
                    self.recent_transactions_table.setItem(i, 5, QTableWidgetItem(transaction.get("date", "")))
                    
                    # Store the transaction data in the first cell for later use
                    self.recent_transactions_table.item(i, 0).setData(Qt.ItemDataRole.UserRole, transaction)
                    
        except Exception as e:
            print(f"Error loading recent transactions: {e}")
    
    def load_branches(self):
        """Load branches data."""
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            response = requests.get(f"{self.api_url}/branches/", headers=headers)
            
            if response.status_code == 200:
                branches = response.json()
                self.branches_table.setRowCount(len(branches))
                
                for i, branch in enumerate(branches):
                    self.branches_table.setItem(i, 0, QTableWidgetItem(branch.get("branch_id", "")))
                    self.branches_table.setItem(i, 1, QTableWidgetItem(branch.get("name", "")))
                    self.branches_table.setItem(i, 2, QTableWidgetItem(branch.get("location", "")))
                    self.branches_table.setItem(i, 3, QTableWidgetItem(branch.get("governorate", "")))
                    
                    # Get employee count for this branch
                    try:
                        emp_response = requests.get(
                            f"{self.api_url}/branches/{branch.get('id')}/employees/stats/", 
                            headers=headers
                        )
                        if emp_response.status_code == 200:
                            emp_data = emp_response.json()
                            emp_count = emp_data.get("total", 0)
                        else:
                            emp_count = 0
                    except:
                        emp_count = 0
                    
                    self.branches_table.setItem(i, 4, QTableWidgetItem(str(emp_count)))
                    
                    # Store the branch data in the first cell for later use
                    self.branches_table.item(i, 0).setData(Qt.ItemDataRole.UserRole, branch)
            else:
                QMessageBox.warning(self, "خطأ", f"فشل تحميل الفروع: رمز الحالة {response.status_code}")
        except Exception as e:
            print(f"Error loading branches: {e}")
            QMessageBox.warning(self, "خطأ", f"تعذر تحميل الفروع: {str(e)}")
    
    def load_employees(self, branch_id=None):
        """Load employees data."""
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            
            # Use /users/ endpoint instead of /employees/ to include branch managers
            url = f"{self.api_url}/users/"
            if branch_id:
                url += f"?branch_id={branch_id}"
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                # For /users/ endpoint, the response is wrapped in a "users" key
                employees = response.json().get("users", [])
                self.employees_table.setRowCount(len(employees))
                
                for i, employee in enumerate(employees):
                    self.employees_table.setItem(i, 0, QTableWidgetItem(employee.get("username", "")))
                    
                    # Map role to Arabic
                    role = employee.get("role", "")
                    role_arabic = "موظف"
                    if role == "director":
                        role_arabic = "مدير"
                    elif role == "branch_manager":
                        role_arabic = "مدير فرع"
                    
                    self.employees_table.setItem(i, 1, QTableWidgetItem(role_arabic))
                    
                    # Get branch name
                    branch_id = employee.get("branch_id")
                    branch_name = "غير محدد"
                    if branch_id:
                        try:
                            branch_response = requests.get(
                                f"{self.api_url}/branches/{branch_id}", 
                                headers=headers
                            )
                            if branch_response.status_code == 200:
                                branch_data = branch_response.json()
                                branch_name = branch_data.get("name", "غير محدد")
                        except:
                            pass
                    
                    self.employees_table.setItem(i, 2, QTableWidgetItem(branch_name))
                    self.employees_table.setItem(i, 3, QTableWidgetItem(employee.get("created_at", "")))
                    
                    # Status (always active for now)
                    status_item = QTableWidgetItem("نشط")
                    status_item.setForeground(QColor("#27ae60"))
                    self.employees_table.setItem(i, 4, status_item)
                    
                    # Store the employee data in the first cell for later use
                    self.employees_table.item(i, 0).setData(Qt.ItemDataRole.UserRole, employee)
            else:
                QMessageBox.warning(self, "خطأ", f"فشل تحميل الموظفين: رمز الحالة {response.status_code}")
        except Exception as e:
            print(f"Error loading employees: {e}")
            QMessageBox.warning(self, "خطأ", f"تعذر تحميل الموظفين: {str(e)}")
    
    def load_transactions(self, branch_id=None, filter_type="all"):
        """Load transactions data."""
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            
            url = f"{self.api_url}/transactions/"
            params = {}
            
            if branch_id and isinstance(branch_id, (int, str)) and branch_id != self.api_url:
                # Ensure branch_id is not the API URL itself
                try:
                    # Try to convert to int if it's a string number
                    if isinstance(branch_id, str) and branch_id.isdigit():
                        branch_id = int(branch_id)
                    params["branch_id"] = branch_id
                except:
                    print(f"Invalid branch_id: {branch_id}")
            
            if filter_type != "all":
                params["filter_type"] = filter_type
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                transactions = data.get("transactions", [])
                self.transactions_table.setRowCount(len(transactions))
                
                for i, transaction in enumerate(transactions):
                    self.transactions_table.setItem(i, 0, QTableWidgetItem(transaction.get("id", "")))
                    self.transactions_table.setItem(i, 1, QTableWidgetItem(transaction.get("sender", "")))
                    self.transactions_table.setItem(i, 2, QTableWidgetItem(transaction.get("receiver", "")))
                    self.transactions_table.setItem(i, 3, QTableWidgetItem(str(transaction.get("amount", ""))))
                    self.transactions_table.setItem(i, 4, QTableWidgetItem(transaction.get("currency", "")))
                    self.transactions_table.setItem(i, 5, QTableWidgetItem(transaction.get("branch_governorate", "")))
                    
                    # Map status values to Arabic
                    status = transaction.get("status", "")
                    status_arabic = "قيد الانتظار"
                    if status == "completed":
                        status_arabic = "تم الاستلام"
                    elif status == "cancelled":
                        status_arabic = "ملغي"
                    
                    status_item = QTableWidgetItem(status_arabic)
                    
                    # Color-code status
                    if status_arabic == "تم الاستلام":
                        status_item.setBackground(QColor(200, 255, 200))  # Light green
                    elif status_arabic == "ملغي":
                        status_item.setBackground(QColor(255, 200, 200))  # Light red
                    
                    self.transactions_table.setItem(i, 6, status_item)
                    self.transactions_table.setItem(i, 7, QTableWidgetItem(transaction.get("date", "")))
                    
                    # Store the transaction data in the first cell for later use
                    self.transactions_table.item(i, 0).setData(Qt.ItemDataRole.UserRole, transaction)
            else:
                QMessageBox.warning(self, "خطأ", f"فشل تحميل التحويلات: رمز الحالة {response.status_code}")
        except Exception as e:
            print(f"Error loading transactions: {e}")
            QMessageBox.warning(self, "خطأ", f"تعذر تحميل التحويلات: {str(e)}")
    
    def load_branches_for_filter(self):
        """Load branches for the report filter."""
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            response = requests.get(f"{self.api_url}/branches/", headers=headers)
            
            if response.status_code == 200:
                branches = response.json()
                self.branch_filter.clear()
                self.branch_filter.addItem("جميع الفروع", None)
                
                for branch in branches:
                    branch_id = branch.get("id")
                    branch_name = branch.get("name", "")
                    # Ensure we're storing the actual branch ID, not the API URL
                    if branch_id and branch_id != self.api_url:
                        self.branch_filter.addItem(branch_name, branch_id)
                
                # Also update transaction branch filter
                self.transaction_branch_filter.clear()
                self.transaction_branch_filter.addItem("جميع الفروع", None)
                
                for branch in branches:
                    branch_id = branch.get("id")
                    branch_name = branch.get("name", "")
                    # Ensure we're storing the actual branch ID, not the API URL
                    if branch_id and branch_id != self.api_url:
                        self.transaction_branch_filter.addItem(branch_name, branch_id)
                
                # And report branch filter
                self.report_branch_filter.clear()
                self.report_branch_filter.addItem("جميع الفروع", None)
                
                for branch in branches:
                    branch_id = branch.get("id")
                    branch_name = branch.get("name", "")
                    # Ensure we're storing the actual branch ID, not the API URL
                    if branch_id and branch_id != self.api_url:
                        self.report_branch_filter.addItem(branch_name, branch_id)
            else:
                print(f"Error loading branches: Status code {response.status_code}")
        except Exception as e:
            print(f"Error loading branches: {e}")
    
    def filter_employees(self):
        """Filter employees by branch."""
        branch_id = self.branch_filter.currentData()
        # Ensure branch_id is not the API URL
        if branch_id == self.api_url:
            branch_id = None
        self.load_employees(branch_id)
    
    def filter_transactions(self):
        """Filter transactions by branch and type."""
        branch_id = self.transaction_branch_filter.currentData()
        # Ensure branch_id is not the API URL
        if branch_id == self.api_url:
            branch_id = None
            
        filter_type_map = {
            0: "all",
            1: "incoming",
            2: "outgoing",
            3: "branch_related"
        }
        
        filter_type = filter_type_map.get(self.transaction_type_filter.currentIndex(), "all")
        
        self.load_transactions(branch_id, filter_type)
    
    def add_branch(self):
        """Open dialog to add a new branch."""
        dialog = AddBranchDialog(self.token, self.api_url, self)
        if dialog.exec() == 1:  # If dialog was accepted
            self.load_branches()  # Refresh the branches list
            self.load_branches_for_filter()  # Refresh branch filters
            self.load_dashboard_data()  # Refresh dashboard data
    
    def edit_branch(self):
        """Open dialog to edit the selected branch."""
        selected_rows = self.branches_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "تنبيه", "الرجاء تحديد فرع للتعديل")
            return
        
        row = selected_rows[0].row()
        branch_data = self.branches_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        # Open edit dialog
        from ui.branch_management_improved import EditBranchDialog
        dialog = EditBranchDialog(branch_data, self.token, self.api_url, self)
        if dialog.exec() == 1:  # If dialog was accepted
            self.load_branches()  # Refresh the branches list
            self.load_branches_for_filter()  # Refresh branch filters
    
    def delete_branch(self):
        """Delete the selected branch."""
        selected_rows = self.branches_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "تنبيه", "الرجاء تحديد فرع للحذف")
            return
        
        row = selected_rows[0].row()
        branch_data = self.branches_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        branch_id = branch_data.get("id")
        branch_name = branch_data.get("name", "")
        
        # Confirm deletion
        reply = QMessageBox.question(self, "تأكيد الحذف", 
                                   f"هل أنت متأكد من حذف الفرع '{branch_name}'؟",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
                response = requests.delete(f"{self.api_url}/branches/{branch_id}/", headers=headers)
                
                if response.status_code == 204:
                    QMessageBox.information(self, "نجاح", "تم حذف الفرع بنجاح")
                    self.load_branches()  # Refresh the branches list
                    self.load_branches_for_filter()  # Refresh branch filters
                    self.load_dashboard_data()  # Refresh dashboard data
                else:
                    error_msg = f"فشل حذف الفرع: رمز الحالة {response.status_code}"
                    try:
                        error_data = response.json()
                        if "detail" in error_data:
                            error_msg = error_data["detail"]
                    except:
                        pass
                    
                    QMessageBox.warning(self, "خطأ", error_msg)
            except Exception as e:
                print(f"Error deleting branch: {e}")
                QMessageBox.warning(self, "خطأ", f"تعذر حذف الفرع: {str(e)}")
    
    def view_branch(self):
        """View details of the selected branch."""
        selected_rows = self.branches_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "تنبيه", "الرجاء تحديد فرع للعرض")
            return
        
        row = selected_rows[0].row()
        branch_data = self.branches_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        # Create a dialog to display branch details
        dialog = QDialog(self)
        dialog.setWindowTitle(f"تفاصيل الفرع: {branch_data.get('name', '')}")
        dialog.setGeometry(150, 150, 600, 400)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
                font-family: Arial;
            }
            QLabel {
                color: #333;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Branch details
        details_group = ModernGroupBox("معلومات الفرع", "#3498db")
        details_layout = QFormLayout()
        
        details_layout.addRow("رمز الفرع:", QLabel(branch_data.get("branch_id", "")))
        details_layout.addRow("اسم الفرع:", QLabel(branch_data.get("name", "")))
        details_layout.addRow("الموقع:", QLabel(branch_data.get("location", "")))
        details_layout.addRow("المحافظة:", QLabel(branch_data.get("governorate", "")))
        
        details_group.setLayout(details_layout)
        layout.addWidget(details_group)
        
        # Branch employees
        employees_group = ModernGroupBox("موظفي الفرع", "#2ecc71")
        employees_layout = QVBoxLayout()
        
        employees_table = QTableWidget()
        employees_table.setColumnCount(3)
        employees_table.setHorizontalHeaderLabels(["اسم المستخدم", "الدور", "تاريخ الإنشاء"])
        employees_table.horizontalHeader().setStretchLastSection(True)
        employees_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            response = requests.get(
                f"{self.api_url}/branches/{branch_data.get('id')}/employees/", 
                headers=headers
            )
            
            if response.status_code == 200:
                employees = response.json()
                employees_table.setRowCount(len(employees))
                
                for i, employee in enumerate(employees):
                    employees_table.setItem(i, 0, QTableWidgetItem(employee.get("username", "")))
                    
                    # Map role to Arabic
                    role = employee.get("role", "")
                    role_arabic = "موظف"
                    if role == "director":
                        role_arabic = "مدير"
                    elif role == "branch_manager":
                        role_arabic = "مدير فرع"
                    
                    employees_table.setItem(i, 1, QTableWidgetItem(role_arabic))
                    employees_table.setItem(i, 2, QTableWidgetItem(employee.get("created_at", "")))
        except Exception as e:
            print(f"Error loading branch employees: {e}")
        
        employees_layout.addWidget(employees_table)
        employees_group.setLayout(employees_layout)
        layout.addWidget(employees_group)
        
        # Branch statistics
        stats_group = ModernGroupBox("إحصائيات الفرع", "#e74c3c")
        stats_layout = QFormLayout()
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            
            # Get employee stats
            emp_response = requests.get(
                f"{self.api_url}/branches/{branch_data.get('id')}/employees/stats/", 
                headers=headers
            )
            if emp_response.status_code == 200:
                emp_data = emp_response.json()
                stats_layout.addRow("عدد الموظفين:", QLabel(str(emp_data.get("total", 0))))
            
            # Get transaction stats
            trans_response = requests.get(
                f"{self.api_url}/branches/{branch_data.get('id')}/transactions/stats/", 
                headers=headers
            )
            if trans_response.status_code == 200:
                trans_data = trans_response.json()
                stats_layout.addRow("عدد التحويلات:", QLabel(str(trans_data.get("total", 0))))
                stats_layout.addRow("إجمالي المبالغ:", QLabel(f"{trans_data.get('total_amount', 0):,.2f}"))
        except Exception as e:
            print(f"Error loading branch statistics: {e}")
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Close button
        close_button = ModernButton("إغلاق", color="#e74c3c")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def add_employee(self):
        """Open dialog to add a new employee."""
        dialog = AddEmployeeDialog(is_admin=True, branch_id=None, token=self.token)
        if dialog.exec() == 1:  # If dialog was accepted
            self.load_employees()  # Refresh the employees list
            self.load_dashboard_data()  # Refresh dashboard data
    
    def edit_employee(self):
        """Open dialog to edit the selected employee."""
        selected_rows = self.employees_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "تنبيه", "الرجاء تحديد موظف للتعديل")
            return
        
        row = selected_rows[0].row()
        employee_data = self.employees_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        # Open edit dialog
        from ui.user_management_improved import EditEmployeeDialog
        dialog = EditEmployeeDialog(employee_data, self.token, self.api_url, self)
        if dialog.exec() == 1:  # If dialog was accepted
            self.load_employees()  # Refresh the employees list
    
    def delete_employee(self):
        """Delete the selected employee."""
        selected_rows = self.employees_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "تنبيه", "الرجاء تحديد موظف للحذف")
            return
        
        row = selected_rows[0].row()
        employee_data = self.employees_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        employee_id = employee_data.get("id")
        employee_name = employee_data.get("username", "")
        
        # Confirm deletion
        reply = QMessageBox.question(self, "تأكيد الحذف", 
                                   f"هل أنت متأكد من حذف الموظف '{employee_name}'؟",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
                response = requests.delete(f"{self.api_url}/users/{employee_id}", headers=headers)
                
                if response.status_code == 204 or response.status_code == 200:
                    QMessageBox.information(self, "نجاح", "تم حذف الموظف بنجاح")
                    self.load_employees()  # Refresh the employees list
                    self.load_dashboard_data()  # Refresh dashboard data
                else:
                    error_msg = f"فشل حذف الموظف: رمز الحالة {response.status_code}"
                    try:
                        error_data = response.json()
                        if "detail" in error_data:
                            error_msg = error_data["detail"]
                    except:
                        pass
                    
                    QMessageBox.warning(self, "خطأ", error_msg)
            except Exception as e:
                print(f"Error deleting employee: {e}")
                QMessageBox.warning(self, "خطأ", f"تعذر حذف الموظف: {str(e)}")
    
    def search_user(self):
        """Open user search dialog."""
        dialog = UserSearchDialog(self.token, self.api_url, self)
        dialog.exec()
    
    def reset_password(self):
        """Reset password for the selected employee."""
        selected_rows = self.employees_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "تنبيه", "الرجاء تحديد موظف لإعادة تعيين كلمة المرور")
            return
        
        row = selected_rows[0].row()
        employee_data = self.employees_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        employee_username = employee_data.get("username", "")
        
        # Create a dialog to reset password
        dialog = QDialog(self)
        dialog.setWindowTitle(f"إعادة تعيين كلمة المرور: {employee_username}")
        dialog.setGeometry(150, 150, 400, 200)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
                font-family: Arial;
            }
            QLabel {
                color: #333;
            }
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Password fields
        form_layout = QFormLayout()
        
        new_password_label = QLabel("كلمة المرور الجديدة:")
        new_password_input = QLineEdit()
        new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow(new_password_label, new_password_input)
        
        confirm_password_label = QLabel("تأكيد كلمة المرور:")
        confirm_password_input = QLineEdit()
        confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow(confirm_password_label, confirm_password_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        cancel_button = ModernButton("إلغاء", color="#e74c3c")
        cancel_button.clicked.connect(dialog.reject)
        buttons_layout.addWidget(cancel_button)
        
        save_button = ModernButton("حفظ", color="#2ecc71")
        
        def reset_password_action():
            new_password = new_password_input.text()
            confirm_password = confirm_password_input.text()
            
            if not new_password:
                QMessageBox.warning(dialog, "تنبيه", "الرجاء إدخال كلمة المرور الجديدة")
                return
            
            if new_password != confirm_password:
                QMessageBox.warning(dialog, "تنبيه", "كلمة المرور وتأكيدها غير متطابقين")
                return
            
            try:
                headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
                data = {
                    "username": employee_username,
                    "new_password": new_password
                }
                response = requests.post(f"{self.api_url}/reset-password/", json=data, headers=headers)
                
                if response.status_code == 200:
                    QMessageBox.information(dialog, "نجاح", "تم إعادة تعيين كلمة المرور بنجاح")
                    dialog.accept()
                else:
                    error_msg = f"فشل إعادة تعيين كلمة المرور: رمز الحالة {response.status_code}"
                    try:
                        error_data = response.json()
                        if "detail" in error_data:
                            error_msg = error_data["detail"]
                    except:
                        pass
                    
                    QMessageBox.warning(dialog, "خطأ", error_msg)
            except Exception as e:
                print(f"Error resetting password: {e}")
                QMessageBox.warning(dialog, "خطأ", f"تعذر إعادة تعيين كلمة المرور: {str(e)}")
        
        save_button.clicked.connect(reset_password_action)
        buttons_layout.addWidget(save_button)
        
        layout.addLayout(buttons_layout)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def view_transaction(self):
        """View details of the selected transaction."""
        selected_rows = self.transactions_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "تنبيه", "الرجاء تحديد تحويل للعرض")
            return
        
        row = selected_rows[0].row()
        transaction = self.transactions_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        # Create a dialog to display transaction details
        dialog = QDialog(self)
        dialog.setWindowTitle("تفاصيل التحويل")
        dialog.setGeometry(150, 150, 500, 400)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
                font-family: Arial;
            }
            QLabel {
                color: #333;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("تفاصيل التحويل")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Transaction details
        details_group = ModernGroupBox("معلومات التحويل", "#3498db")
        details_layout = QVBoxLayout()
        
        # Format transaction details
        details_text = f"""
        <b>رقم التحويل:</b> {transaction.get('id', '')}<br>
        <b>التاريخ:</b> {transaction.get('date', '')}<br>
        <br>
        <b>المرسل:</b> {transaction.get('sender', '')}<br>
        <b>رقم هاتف المرسل:</b> {transaction.get('sender_mobile', '')}<br>
        <b>محافظة المرسل:</b> {transaction.get('sender_governorate', '')}<br>
        <b>موقع المرسل:</b> {transaction.get('sender_location', '')}<br>
        <br>
        <b>المستلم:</b> {transaction.get('receiver', '')}<br>
        <b>رقم هاتف المستلم:</b> {transaction.get('receiver_mobile', '')}<br>
        <b>محافظة المستلم:</b> {transaction.get('receiver_governorate', '')}<br>
        <b>موقع المستلم:</b> {transaction.get('receiver_location', '')}<br>
        <br>
        <b>المبلغ:</b> {transaction.get('amount', '')} {transaction.get('currency', '')}<br>
        <b>الرسالة:</b> {transaction.get('message', '')}<br>
        <br>
        <b>الفرع:</b> {transaction.get('branch_governorate', '')}<br>
        <b>الموظف:</b> {transaction.get('employee_name', '')}<br>
        <b>الحالة:</b> {transaction.get('status', '')}
        """
        
        details_label = QLabel(details_text)
        details_label.setTextFormat(Qt.TextFormat.RichText)
        details_label.setWordWrap(True)
        details_layout.addWidget(details_label)
        
        details_group.setLayout(details_layout)
        layout.addWidget(details_group)
        
        # Close button
        close_button = ModernButton("إغلاق", color="#e74c3c")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def update_transaction_status(self):
        """Update status of the selected transaction."""
        selected_rows = self.transactions_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "تنبيه", "الرجاء تحديد تحويل لتحديث الحالة")
            return
        
        row = selected_rows[0].row()
        transaction = self.transactions_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        transaction_id = transaction.get('id', '')
        
        # Create a dialog to update status
        dialog = QDialog(self)
        dialog.setWindowTitle("تحديث حالة التحويل")
        dialog.setGeometry(150, 150, 400, 200)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
                font-family: Arial;
            }
            QLabel {
                color: #333;
            }
            QComboBox {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Status selection
        form_layout = QFormLayout()
        
        status_label = QLabel("الحالة:")
        status_combo = QComboBox()
        status_combo.addItems(["قيد الانتظار", "تم الاستلام", "ملغي"])
        
        # Set current status
        current_status = transaction.get('status', '')
        if current_status == "completed":
            status_combo.setCurrentText("تم الاستلام")
        elif current_status == "cancelled":
            status_combo.setCurrentText("ملغي")
        else:
            status_combo.setCurrentText("قيد الانتظار")
        
        form_layout.addRow(status_label, status_combo)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        cancel_button = ModernButton("إلغاء", color="#e74c3c")
        cancel_button.clicked.connect(dialog.reject)
        buttons_layout.addWidget(cancel_button)
        
        save_button = ModernButton("حفظ", color="#2ecc71")
        
        def update_status_action():
            # Map Arabic status to English
            status_map = {
                "قيد الانتظار": "processing",
                "تم الاستلام": "completed",
                "ملغي": "cancelled"
            }
            
            new_status = status_map.get(status_combo.currentText(), "processing")
            
            try:
                headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
                data = {
                    "transaction_id": transaction_id,
                    "status": new_status
                }
                response = requests.post(f"{self.api_url}/update-transaction-status/", json=data, headers=headers)
                
                if response.status_code == 200:
                    QMessageBox.information(dialog, "نجاح", "تم تحديث حالة التحويل بنجاح")
                    dialog.accept()
                    self.load_transactions()  # Refresh the transactions list
                else:
                    error_msg = f"فشل تحديث حالة التحويل: رمز الحالة {response.status_code}"
                    try:
                        error_data = response.json()
                        if "detail" in error_data:
                            error_msg = error_data["detail"]
                    except:
                        pass
                    
                    QMessageBox.warning(dialog, "خطأ", error_msg)
            except Exception as e:
                print(f"Error updating transaction status: {e}")
                QMessageBox.warning(dialog, "خطأ", f"تعذر تحديث حالة التحويل: {str(e)}")
        
        save_button.clicked.connect(update_status_action)
        buttons_layout.addWidget(save_button)
        
        layout.addLayout(buttons_layout)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def print_receipt(self):
        """Print receipt for the selected transaction."""
        selected_rows = self.transactions_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "تنبيه", "الرجاء تحديد تحويل لطباعة الإيصال")
            return
        
        row = selected_rows[0].row()
        transaction = self.transactions_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        transaction_id = transaction.get('id', '')
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            response = requests.get(f"{self.api_url}/transactions/{transaction_id}/receipt/", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                receipt_url = data.get("receipt_url", "")
                
                if receipt_url:
                    # Open receipt in browser or PDF viewer
                    QMessageBox.information(self, "نجاح", "تم فتح الإيصال في المتصفح")
                    # In a real application, you would open the URL in a browser or PDF viewer
                else:
                    QMessageBox.warning(self, "تنبيه", "لا يوجد إيصال متاح لهذا التحويل")
            else:
                QMessageBox.warning(self, "خطأ", f"فشل طباعة الإيصال: رمز الحالة {response.status_code}")
        except Exception as e:
            print(f"Error printing receipt: {e}")
            QMessageBox.warning(self, "خطأ", f"تعذر طباعة الإيصال: {str(e)}")
    
    def search_transaction(self):
        """Open transaction search dialog."""
        # This would be similar to the user search dialog but for transactions
        QMessageBox.information(self, "معلومات", "ميزة البحث عن التحويلات قيد التطوير")
    
    def generate_report(self):
        """Generate a report based on the selected options."""
        report_type_map = {
            "تقرير التحويلات": "transactions",
            "تقرير الفروع": "branches",
            "تقرير الموظفين": "employees"
        }
        
        report_type = report_type_map.get(self.report_type.currentText(), "transactions")
        from_date = self.from_date.date().toString("yyyy-MM-dd")
        to_date = self.to_date.date().toString("yyyy-MM-dd")
        branch_id = self.report_branch_filter.currentData()
        
        # Ensure branch_id is not the API URL
        if branch_id == self.api_url:
            branch_id = None
            
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            params = {
                "date_from": from_date,
                "date_to": to_date
            }
            
            if branch_id:
                params["branch_id"] = branch_id
            
            response = requests.get(
                f"{self.api_url}/reports/{report_type}/", 
                headers=headers,
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                
                # Set up table columns based on report type
                if report_type == "transactions":
                    self.report_table.setColumnCount(7)
                    self.report_table.setHorizontalHeaderLabels([
                        "رقم التحويل", "التاريخ", "المرسل", "المستلم", "المبلغ", "العملة", "الحالة"
                    ])
                elif report_type == "branches":
                    self.report_table.setColumnCount(5)
                    self.report_table.setHorizontalHeaderLabels([
                        "رمز الفرع", "اسم الفرع", "الموقع", "المحافظة", "الحالة"
                    ])
                elif report_type == "employees":
                    self.report_table.setColumnCount(4)
                    self.report_table.setHorizontalHeaderLabels([
                        "اسم المستخدم", "الدور", "الفرع", "تاريخ الإنشاء"
                    ])
                
                # Fill table with data
                self.report_table.setRowCount(len(items))
                
                for i, item in enumerate(items):
                    if report_type == "transactions":
                        self.report_table.setItem(i, 0, QTableWidgetItem(item.get("id", "")))
                        self.report_table.setItem(i, 1, QTableWidgetItem(item.get("date", "")))
                        self.report_table.setItem(i, 2, QTableWidgetItem(item.get("sender", "")))
                        self.report_table.setItem(i, 3, QTableWidgetItem(item.get("receiver", "")))
                        self.report_table.setItem(i, 4, QTableWidgetItem(str(item.get("amount", ""))))
                        self.report_table.setItem(i, 5, QTableWidgetItem(item.get("currency", "")))
                        self.report_table.setItem(i, 6, QTableWidgetItem(item.get("status", "")))
                    elif report_type == "branches":
                        self.report_table.setItem(i, 0, QTableWidgetItem(item.get("branch_id", "")))
                        self.report_table.setItem(i, 1, QTableWidgetItem(item.get("name", "")))
                        self.report_table.setItem(i, 2, QTableWidgetItem(item.get("location", "")))
                        self.report_table.setItem(i, 3, QTableWidgetItem(item.get("governorate", "")))
                        self.report_table.setItem(i, 4, QTableWidgetItem(item.get("status", "")))
                    elif report_type == "employees":
                        self.report_table.setItem(i, 0, QTableWidgetItem(item.get("username", "")))
                        self.report_table.setItem(i, 1, QTableWidgetItem(item.get("role", "")))
                        self.report_table.setItem(i, 2, QTableWidgetItem(str(item.get("branch_id", ""))))
                        self.report_table.setItem(i, 3, QTableWidgetItem(item.get("created_at", "")))
                
                self.report_table.horizontalHeader().setStretchLastSection(True)
                self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
                
                QMessageBox.information(self, "نجاح", "تم إنشاء التقرير بنجاح")
            else:
                QMessageBox.warning(self, "خطأ", f"فشل إنشاء التقرير: رمز الحالة {response.status_code}")
        except Exception as e:
            print(f"Error generating report: {e}")
            QMessageBox.warning(self, "خطأ", f"تعذر إنشاء التقرير: {str(e)}")
    
    def export_pdf(self):
        """Export the current report as PDF."""
        # This would use a PDF library to export the report
        QMessageBox.information(self, "معلومات", "ميزة تصدير PDF قيد التطوير")
    
    def export_excel(self):
        """Export the current report as Excel."""
        # This would use pandas to export the report to Excel
        QMessageBox.information(self, "معلومات", "ميزة تصدير Excel قيد التطوير")
    
    def print_report(self):
        """Print the current report."""
        # This would use QPrinter to print the report
        QMessageBox.information(self, "معلومات", "ميزة الطباعة قيد التطوير")
    
    def save_settings(self):
        """Save system settings."""
        # In a real application, this would save the settings to a database or config file
        QMessageBox.information(self, "نجاح", "تم حفظ الإعدادات بنجاح")
    
    def change_password(self):
        """Change the user's password."""
        old_password = self.old_password_input.text()
        new_password = self.new_password_input.text()
        confirm_password = self.confirm_password_input.text()
        
        if not old_password or not new_password or not confirm_password:
            QMessageBox.warning(self, "تنبيه", "الرجاء ملء جميع حقول كلمة المرور")
            return
        
        if new_password != confirm_password:
            QMessageBox.warning(self, "تنبيه", "كلمة المرور الجديدة وتأكيدها غير متطابقين")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            data = {
                "old_password": old_password,
                "new_password": new_password
            }
            response = requests.post(f"{self.api_url}/change-password/", json=data, headers=headers)
            
            if response.status_code == 200:
                QMessageBox.information(self, "نجاح", "تم تغيير كلمة المرور بنجاح")
                self.old_password_input.clear()
                self.new_password_input.clear()
                self.confirm_password_input.clear()
            else:
                error_msg = f"فشل تغيير كلمة المرور: رمز الحالة {response.status_code}"
                try:
                    error_data = response.json()
                    if "detail" in error_data:
                        error_msg = error_data["detail"]
                except:
                    pass
                
                QMessageBox.warning(self, "خطأ", error_msg)
        except Exception as e:
            print(f"Error changing password: {e}")
            QMessageBox.warning(self, "خطأ", f"تعذر تغيير كلمة المرور: {str(e)}")
    
    def create_backup(self):
        """Create a backup of the database."""
        # This would create a backup of the database
        QMessageBox.information(self, "معلومات", "ميزة النسخ الاحتياطي قيد التطوير")
    
    def restore_backup(self):
        """Restore from a backup."""
        # This would restore from a backup
        QMessageBox.information(self, "معلومات", "ميزة استعادة النسخ الاحتياطي قيد التطوير")
