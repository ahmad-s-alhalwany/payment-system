import sys
import requests
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QDialog, QLineEdit, QFormLayout, QComboBox, QGroupBox,
    QGridLayout, QDateEdit, QSpinBox, QDoubleSpinBox, QCheckBox, QMenu,
    QStatusBar, QSplitter, QFrame, QTextEdit, QRadioButton, QButtonGroup
)
from PyQt6.QtGui import QFont, QColor, QAction, QIcon
from PyQt6.QtCore import Qt, QDate, pyqtSignal, QTimer

from ui.user_search import UserSearchDialog

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

class MoneyTransferApp(QWidget):
    """Money Transfer Application for the Internal Payment System."""
    
    def __init__(self, user_token=None, branch_id=None, user_id=None, user_role="employee", username="User", api_url="http://127.0.0.1:8000"):
        super().__init__()
        self.user_token = user_token
        self.branch_id = branch_id
        self.user_id = user_id
        self.user_role = user_role
        self.username = username
        self.api_url = api_url
        
        self.setup_ui()
        
        # Load initial data
        self.load_branches()
        self.load_transactions()
    
    def setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout()
        
        # Create tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ccc;
                border-radius: 5px;
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
        
        # Create tab widgets
        self.new_transfer_tab = QWidget()
        self.transactions_tab = QWidget()
        
        # Set up tabs
        self.setup_new_transfer_tab()
        self.setup_transactions_tab()
        
        # Add tabs to widget
        self.tabs.addTab(self.new_transfer_tab, "تحويل جديد")
        self.tabs.addTab(self.transactions_tab, "التحويلات")
        
        layout.addWidget(self.tabs)
        
        self.setLayout(layout)
    
    def setup_new_transfer_tab(self):
        """Set up the new transfer tab."""
        layout = QVBoxLayout()
        
        # Sender information
        sender_group = ModernGroupBox("معلومات المرسل", "#e74c3c")
        sender_layout = QGridLayout()
        
        # Sender name
        sender_name_label = QLabel("اسم المرسل:")
        sender_layout.addWidget(sender_name_label, 0, 0)
        
        self.sender_name_input = QLineEdit()
        self.sender_name_input.setPlaceholderText("أدخل اسم المرسل")
        sender_layout.addWidget(self.sender_name_input, 0, 1)
        
        # Sender mobile
        sender_mobile_label = QLabel("رقم الهاتف:")
        sender_layout.addWidget(sender_mobile_label, 0, 2)
        
        self.sender_mobile_input = QLineEdit()
        self.sender_mobile_input.setPlaceholderText("أدخل رقم الهاتف")
        sender_layout.addWidget(self.sender_mobile_input, 0, 3)
        
        # Sender ID
        sender_id_label = QLabel("رقم الهوية:")
        sender_layout.addWidget(sender_id_label, 1, 0)
        
        self.sender_id_input = QLineEdit()
        self.sender_id_input.setPlaceholderText("أدخل رقم الهوية")
        sender_layout.addWidget(self.sender_id_input, 1, 1)
        
        # Sender address
        sender_address_label = QLabel("العنوان:")
        sender_layout.addWidget(sender_address_label, 1, 2)
        
        self.sender_address_input = QLineEdit()
        self.sender_address_input.setPlaceholderText("أدخل العنوان")
        sender_layout.addWidget(self.sender_address_input, 1, 3)
        
        # Sender governorate
        sender_governorate_label = QLabel("المحافظة:")
        sender_layout.addWidget(sender_governorate_label, 2, 0)
        
        self.sender_governorate_input = QComboBox()
        self.sender_governorate_input.addItems([
            "دمشق", "حلب", "حمص", "حماة", "اللاذقية", "طرطوس", "درعا", "السويداء", "القنيطرة", "الرقة", "دير الزور", "الحسكة", "إدلب"
        ])
        sender_layout.addWidget(self.sender_governorate_input, 2, 1)
        
        # Sender location
        sender_location_label = QLabel("المنطقة:")
        sender_layout.addWidget(sender_location_label, 2, 2)
        
        self.sender_location_input = QLineEdit()
        self.sender_location_input.setPlaceholderText("أدخل المنطقة")
        sender_layout.addWidget(self.sender_location_input, 2, 3)
        
        sender_group.setLayout(sender_layout)
        layout.addWidget(sender_group)
        
        # Receiver information
        receiver_group = ModernGroupBox("معلومات المستلم", "#3498db")
        receiver_layout = QGridLayout()
        
        # Receiver name
        receiver_name_label = QLabel("اسم المستلم:")
        receiver_layout.addWidget(receiver_name_label, 0, 0)
        
        self.receiver_name_input = QLineEdit()
        self.receiver_name_input.setPlaceholderText("أدخل اسم المستلم")
        receiver_layout.addWidget(self.receiver_name_input, 0, 1)
        
        # Receiver mobile
        receiver_mobile_label = QLabel("رقم الهاتف:")
        receiver_layout.addWidget(receiver_mobile_label, 0, 2)
        
        self.receiver_mobile_input = QLineEdit()
        self.receiver_mobile_input.setPlaceholderText("أدخل رقم الهاتف")
        receiver_layout.addWidget(self.receiver_mobile_input, 0, 3)
        
        # Receiver ID
        receiver_id_label = QLabel("رقم الهوية:")
        receiver_layout.addWidget(receiver_id_label, 1, 0)
        
        self.receiver_id_input = QLineEdit()
        self.receiver_id_input.setPlaceholderText("أدخل رقم الهوية")
        receiver_layout.addWidget(self.receiver_id_input, 1, 1)
        
        # Receiver address
        receiver_address_label = QLabel("العنوان:")
        receiver_layout.addWidget(receiver_address_label, 1, 2)
        
        self.receiver_address_input = QLineEdit()
        self.receiver_address_input.setPlaceholderText("أدخل العنوان")
        receiver_layout.addWidget(self.receiver_address_input, 1, 3)
        
        # Receiver governorate
        receiver_governorate_label = QLabel("المحافظة:")
        receiver_layout.addWidget(receiver_governorate_label, 2, 0)
        
        self.receiver_governorate_input = QComboBox()
        self.receiver_governorate_input.addItems([
            "دمشق", "حلب", "حمص", "حماة", "اللاذقية", "طرطوس", "درعا", "السويداء", "القنيطرة", "الرقة", "دير الزور", "الحسكة", "إدلب"
        ])
        receiver_layout.addWidget(self.receiver_governorate_input, 2, 1)
        
        # Receiver location
        receiver_location_label = QLabel("المنطقة:")
        receiver_layout.addWidget(receiver_location_label, 2, 2)
        
        self.receiver_location_input = QLineEdit()
        self.receiver_location_input.setPlaceholderText("أدخل المنطقة")
        receiver_layout.addWidget(self.receiver_location_input, 2, 3)
        
        receiver_group.setLayout(receiver_layout)
        layout.addWidget(receiver_group)
        
        # Transfer information
        transfer_group = ModernGroupBox("معلومات التحويل", "#2ecc71")
        transfer_layout = QGridLayout()
        
        # Amount
        amount_label = QLabel("المبلغ:")
        transfer_layout.addWidget(amount_label, 0, 0)
        
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0, 1000000000)
        self.amount_input.setDecimals(2)
        self.amount_input.setSingleStep(100)
        self.amount_input.setValue(0)
        transfer_layout.addWidget(self.amount_input, 0, 1)
        
        # Currency
        currency_label = QLabel("العملة:")
        transfer_layout.addWidget(currency_label, 0, 2)
        
        self.currency_input = QComboBox()
        self.currency_input.addItems(["ليرة سورية", "دولار أمريكي", "يورو"])
        transfer_layout.addWidget(self.currency_input, 0, 3)
        
        # Branch
        branch_label = QLabel("الفرع:")
        transfer_layout.addWidget(branch_label, 1, 0)
        
        self.branch_input = QComboBox()
        # Enable branch selection for all users to allow sending to any branch
        self.branch_input.setEnabled(True)
        transfer_layout.addWidget(self.branch_input, 1, 1)
        
        # Date
        date_label = QLabel("التاريخ:")
        transfer_layout.addWidget(date_label, 1, 2)
        
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        transfer_layout.addWidget(self.date_input, 1, 3)
        
        # Notes
        notes_label = QLabel("ملاحظات:")
        transfer_layout.addWidget(notes_label, 2, 0)
        
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("أدخل أي ملاحظات إضافية")
        self.notes_input.setMaximumHeight(80)
        transfer_layout.addWidget(self.notes_input, 2, 1, 1, 3)
        
        transfer_group.setLayout(transfer_layout)
        layout.addWidget(transfer_group)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        clear_button = ModernButton("مسح", color="#e74c3c")
        clear_button.clicked.connect(self.clear_form)
        buttons_layout.addWidget(clear_button)
        
        save_button = ModernButton("حفظ", color="#3498db")
        save_button.clicked.connect(self.save_transfer)
        buttons_layout.addWidget(save_button)
        
        submit_button = ModernButton("إرسال", color="#2ecc71")
        submit_button.clicked.connect(self.submit_transfer)
        buttons_layout.addWidget(submit_button)
        
        layout.addLayout(buttons_layout)
        
        self.new_transfer_tab.setLayout(layout)
    
    def setup_transactions_tab(self):
        """Set up the transactions tab."""
        layout = QVBoxLayout()
        
        # Search and filter controls
        controls_layout = QHBoxLayout()
        
        # Search button
        search_button = ModernButton("بحث", color="#3498db")
        search_button.clicked.connect(self.open_search_dialog)
        controls_layout.addWidget(search_button)
        
        # Refresh button
        refresh_button = ModernButton("تحديث", color="#2ecc71")
        refresh_button.clicked.connect(self.load_transactions)
        controls_layout.addWidget(refresh_button)
        
        # Filter by status
        status_label = QLabel("تصفية حسب الحالة:")
        controls_layout.addWidget(status_label)
        
        self.status_filter = QComboBox()
        self.status_filter.addItem("الكل", "all")
        self.status_filter.addItem("قيد الانتظار", "pending")
        self.status_filter.addItem("قيد المعالجة", "processing")
        self.status_filter.addItem("مكتمل", "completed")
        self.status_filter.addItem("ملغي", "cancelled")
        self.status_filter.addItem("مرفوض", "rejected")
        self.status_filter.addItem("معلق", "on_hold")
        self.status_filter.currentIndexChanged.connect(self.filter_transactions)
        controls_layout.addWidget(self.status_filter)
        
        layout.addLayout(controls_layout)
        
        # Transactions table
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(8)
        self.transactions_table.setHorizontalHeaderLabels([
            "رقم التحويل", "التاريخ", "المرسل", "المستلم", "المبلغ", "الحالة", "الموظف", "الملاحظات"
        ])
        self.transactions_table.horizontalHeader().setStretchLastSection(True)
        self.transactions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.transactions_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
                gridline-color: #f0f0f0;
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
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        
        # Connect double-click event
        self.transactions_table.itemDoubleClicked.connect(self.show_transaction_details)
        
        # Connect context menu event
        self.transactions_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.transactions_table.customContextMenuRequested.connect(self.show_context_menu)
        
        layout.addWidget(self.transactions_table)
        
        # Status bar
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel("جاهز")
        status_layout.addWidget(self.status_label)
        
        self.count_label = QLabel("عدد التحويلات: 0")
        status_layout.addWidget(self.count_label, alignment=Qt.AlignmentFlag.AlignRight)
        
        layout.addLayout(status_layout)
        
        self.transactions_tab.setLayout(layout)
    
    def load_branches(self):
        """Load branches from the API."""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"} if self.user_token else {}
            response = requests.get(f"{self.api_url}/branches/", headers=headers)
            
            if response.status_code == 200:
                branches_data = response.json()
                branches = branches_data.get("branches", [])
                
                # Clear and populate branch combo
                self.branch_input.clear()
                
                for branch in branches:
                    # Display branch name and governorate together
                    branch_display = f"{branch.get('name', '')} - {branch.get('governorate', '')}"
                    self.branch_input.addItem(branch_display, branch.get("id", ""))
                
                # Set current branch if branch_id is provided
                if self.branch_id:
                    for i in range(self.branch_input.count()):
                        if self.branch_input.itemData(i) == self.branch_id:
                            self.branch_input.setCurrentIndex(i)
                            break
            else:
                QMessageBox.warning(self, "خطأ", f"فشل تحميل بيانات الفروع: رمز الحالة {response.status_code}")
        except Exception as e:
            print(f"Error loading branches: {e}")
            QMessageBox.critical(self, "خطأ في الاتصال", 
                               "تعذر الاتصال بالخادم. الرجاء التحقق من اتصالك بالإنترنت وحالة الخادم.")
    
    def load_transactions(self):
        """Load transactions from the API."""
        self.status_label.setText("جاري تحميل البيانات...")
        
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"} if self.user_token else {}
            
            # Build URL based on role and branch
            url = f"{self.api_url}/transactions/"
            if self.branch_id and self.user_role != "director":
                url += f"?branch_id={self.branch_id}"
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                transactions_data = response.json()
                transactions = transactions_data.get("transactions", [])
                
                # Store transactions for filtering
                self.all_transactions = transactions
                
                # Apply current filter
                self.filter_transactions()
                
                # Update status
                self.status_label.setText("تم تحميل البيانات بنجاح")
                self.count_label.setText(f"عدد التحويلات: {len(transactions)}")
            else:
                self.status_label.setText(f"خطأ في تحميل البيانات: {response.status_code}")
                QMessageBox.warning(self, "خطأ", f"فشل تحميل بيانات التحويلات: رمز الحالة {response.status_code}")
        except Exception as e:
            self.status_label.setText("خطأ في الاتصال")
            print(f"Error loading transactions: {e}")
            QMessageBox.critical(self, "خطأ في الاتصال", 
                               "تعذر الاتصال بالخادم. الرجاء التحقق من اتصالك بالإنترنت وحالة الخادم.")
    
    def filter_transactions(self):
        """Filter transactions based on selected status."""
        if not hasattr(self, 'all_transactions'):
            return
        
        selected_status = self.status_filter.currentData()
        
        if selected_status == "all":
            filtered_transactions = self.all_transactions
        else:
            filtered_transactions = [t for t in self.all_transactions if t.get("status", "") == selected_status]
        
        # Update table
        self.transactions_table.setRowCount(len(filtered_transactions))
        
        for i, transaction in enumerate(filtered_transactions):
            # Transaction ID
            self.transactions_table.setItem(i, 0, QTableWidgetItem(str(transaction.get("id", ""))))
            
            # Date
            date_str = transaction.get("date", "")
            formatted_date = date_str
            try:
                # Try to parse and format the date
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                formatted_date = date_obj.strftime("%Y-%m-%d")
            except:
                pass
            self.transactions_table.setItem(i, 1, QTableWidgetItem(formatted_date))
            
            # Sender
            self.transactions_table.setItem(i, 2, QTableWidgetItem(transaction.get("sender_name", "")))
            
            # Receiver
            self.transactions_table.setItem(i, 3, QTableWidgetItem(transaction.get("receiver_name", "")))
            
            # Amount
            amount = transaction.get("amount", 0)
            formatted_amount = f"{float(amount):,.2f}" if amount else "0.00"
            self.transactions_table.setItem(i, 4, QTableWidgetItem(formatted_amount))
            
            # Status
            status = transaction.get("status", "pending")
            status_arabic = self.get_status_arabic(status)
            status_item = QTableWidgetItem(status_arabic)
            
            # Color-code status
            status_item.setBackground(self.get_status_color(status))
            self.transactions_table.setItem(i, 5, status_item)
            
            # Employee
            self.transactions_table.setItem(i, 6, QTableWidgetItem(transaction.get("employee_name", "")))
            
            # Notes
            self.transactions_table.setItem(i, 7, QTableWidgetItem(transaction.get("notes", "")))
        
        # Update count
        self.count_label.setText(f"عدد التحويلات: {len(filtered_transactions)}")
    
    def get_status_arabic(self, status):
        """Convert status to Arabic."""
        status_map = {
            "pending": "قيد الانتظار",
            "processing": "قيد المعالجة",
            "completed": "مكتمل",
            "cancelled": "ملغي",
            "rejected": "مرفوض",
            "on_hold": "معلق"
        }
        return status_map.get(status, status)
    
    def get_status_color(self, status):
        """Get color for status."""
        status_colors = {
            "pending": QColor(255, 255, 200),  # Light yellow
            "processing": QColor(200, 200, 255),  # Light blue
            "completed": QColor(200, 255, 200),  # Light green
            "cancelled": QColor(255, 200, 200),  # Light red
            "rejected": QColor(255, 150, 150),  # Darker red
            "on_hold": QColor(255, 200, 150)  # Light orange
        }
        return status_colors.get(status, QColor(255, 255, 255))  # White default
    
    def clear_form(self):
        """Clear the new transfer form."""
        # Clear sender information
        self.sender_name_input.clear()
        self.sender_mobile_input.clear()
        self.sender_id_input.clear()
        self.sender_address_input.clear()
        self.sender_governorate_input.setCurrentIndex(0)
        self.sender_location_input.clear()
        
        # Clear receiver information
        self.receiver_name_input.clear()
        self.receiver_mobile_input.clear()
        self.receiver_id_input.clear()
        self.receiver_address_input.clear()
        self.receiver_governorate_input.setCurrentIndex(0)
        self.receiver_location_input.clear()
        
        # Clear transfer information
        self.amount_input.setValue(0)
        self.currency_input.setCurrentIndex(0)
        self.date_input.setDate(QDate.currentDate())
        self.notes_input.clear()
    
    def save_transfer(self):
        """Save the transfer as a draft."""
        # Validate required fields
        if not self.validate_transfer_form():
            return
        
        # Prepare data
        data = self.prepare_transfer_data()
        data["status"] = "pending"  # Draft status
        
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"} if self.user_token else {}
            response = requests.post(f"{self.api_url}/transactions/", json=data, headers=headers)
            
            if response.status_code == 201:
                QMessageBox.information(self, "نجاح", "تم حفظ التحويل بنجاح")
                self.clear_form()
                self.load_transactions()
            else:
                error_msg = f"فشل حفظ التحويل: رمز الحالة {response.status_code}"
                try:
                    error_data = response.json()
                    if "detail" in error_data:
                        error_msg = error_data["detail"]
                except:
                    pass
                
                QMessageBox.warning(self, "خطأ", error_msg)
        except Exception as e:
            print(f"Error saving transfer: {e}")
            QMessageBox.critical(self, "خطأ في الاتصال", 
                               "تعذر الاتصال بالخادم. الرجاء التحقق من اتصالك بالإنترنت وحالة الخادم.")
    
    def submit_transfer(self):
        """Submit the transfer for processing."""
        # Validate required fields
        if not self.validate_transfer_form():
            return
        
        # Prepare data
        data = self.prepare_transfer_data()
        data["status"] = "processing"  # Processing status
        
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"} if self.user_token else {}
            response = requests.post(f"{self.api_url}/transactions/", json=data, headers=headers)
            
            if response.status_code == 201:
                QMessageBox.information(self, "نجاح", "تم إرسال التحويل بنجاح")
                self.clear_form()
                self.load_transactions()
            else:
                error_msg = f"فشل إرسال التحويل: رمز الحالة {response.status_code}"
                try:
                    error_data = response.json()
                    if "detail" in error_data:
                        if isinstance(error_data["detail"], list):
                            # Handle multiple validation errors
                            errors = [f"{err['loc'][-1]}: {err['msg']}" for err in error_data["detail"]]
                            error_msg += "\n" + "\n".join(errors)
                        else:
                            error_msg += f"\nالتفاصيل: {error_data['detail']}"
                except:
                    pass
                QMessageBox.warning(self, "خطأ", error_msg)
                
                QMessageBox.warning(self, "خطأ", error_msg)
        except Exception as e:
            print(f"Error submitting transfer: {e}")
            QMessageBox.critical(self, "خطأ في الاتصال", 
                            "تعذر الاتصال بالخادم. الرجاء التحقق من اتصالك بالإنترنت وحالة الخادم.")
    
    def validate_transfer_form(self):
        """Validate the transfer form."""
        # Validate sender information
        if not self.sender_name_input.text():
            QMessageBox.warning(self, "تنبيه", "الرجاء إدخال اسم المرسل")
            return False
        
        if not self.sender_mobile_input.text():
            QMessageBox.warning(self, "تنبيه", "الرجاء إدخال رقم هاتف المرسل")
            return False
        
        # Validate receiver information
        if not self.receiver_name_input.text():
            QMessageBox.warning(self, "تنبيه", "الرجاء إدخال اسم المستلم")
            return False
        
        if not self.receiver_mobile_input.text():
            QMessageBox.warning(self, "تنبيه", "الرجاء إدخال رقم هاتف المستلم")
            return False
        
        # Validate amount
        if self.amount_input.value() <= 0:
            QMessageBox.warning(self, "تنبيه", "الرجاء إدخال مبلغ صحيح")
            return False
        
        return True
    
    def prepare_transfer_data(self):
        """Prepare transfer data for submission."""
        # Get selected branch ID
        branch_id = self.branch_id
        if self.user_role == "director":
            branch_id = self.branch_input.currentData()
        
        # Get branch governorate
        branch_governorate = self.sender_governorate_input.currentText()
        if self.user_role != "director":
            # For non-directors, use the branch's governorate
            branch_index = self.branch_input.currentIndex()
            branch_text = self.branch_input.currentText()
            if " - " in branch_text:
                branch_governorate = branch_text.split(" - ")[1]

        # Prepare data according to Transaction model
        data = {
            "sender": self.sender_name_input.text(),
            "sender_mobile": self.sender_mobile_input.text(),
            "sender_governorate": self.sender_governorate_input.currentText(),
            "sender_location": self.sender_location_input.text(),
            
            "receiver": self.receiver_name_input.text(),
            "receiver_mobile": self.receiver_mobile_input.text(),
            "receiver_governorate": self.receiver_governorate_input.currentText(),
            "receiver_location": self.receiver_location_input.text(),
            
            "amount": float(self.amount_input.value()),
            "currency": self.currency_input.currentText(),
            "message": self.notes_input.toPlainText(),
            
            "employee_name": self.username,
            "branch_governorate": branch_governorate
        }
        
        return data
    
    def show_transaction_details(self, item):
        """Show transaction details when an item is double-clicked."""
        row = item.row()
        transaction_id = self.transactions_table.item(row, 0).text()
        
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"} if self.user_token else {}
            response = requests.get(f"{self.api_url}/transactions/{transaction_id}", headers=headers)
            
            if response.status_code == 200:
                transaction = response.json()
                
                # Create and show details dialog
                details_dialog = TransactionDetailsDialog(transaction, self)
                details_dialog.exec()
            else:
                QMessageBox.warning(self, "خطأ", f"فشل تحميل تفاصيل التحويل: رمز الحالة {response.status_code}")
        except Exception as e:
            print(f"Error loading transaction details: {e}")
            QMessageBox.critical(self, "خطأ في الاتصال", 
                               "تعذر الاتصال بالخادم. الرجاء التحقق من اتصالك بالإنترنت وحالة الخادم.")
    
    def show_context_menu(self, position):
        """Show context menu for transactions table."""
        # Only show context menu if a row is selected
        if not self.transactions_table.selectedItems():
            return
        
        row = self.transactions_table.selectedItems()[0].row()
        transaction_id = self.transactions_table.item(row, 0).text()
        current_status = self.transactions_table.item(row, 5).text()
        
        # Create context menu
        context_menu = QMenu(self)
        
        # View details action
        view_action = QAction("عرض التفاصيل", self)
        view_action.triggered.connect(lambda: self.show_transaction_details(self.transactions_table.item(row, 0)))
        context_menu.addAction(view_action)
        
        # Change status action (only for managers and directors)
        if self.user_role in ["branch_manager", "director"]:
            change_status_menu = QMenu("تغيير الحالة", self)
            
            # Add status options
            statuses = [
                ("قيد الانتظار", "pending"),
                ("قيد المعالجة", "processing"),
                ("مكتمل", "completed"),
                ("ملغي", "cancelled"),
                ("مرفوض", "rejected"),
                ("معلق", "on_hold")
            ]
            
            for status_arabic, status_code in statuses:
                if status_arabic != current_status:  # Don't show current status
                    status_action = QAction(status_arabic, self)
                    status_action.triggered.connect(
                        lambda checked, tid=transaction_id, status=status_code: 
                        self.update_transaction_status(tid, status)
                    )
                    change_status_menu.addAction(status_action)
            
            context_menu.addMenu(change_status_menu)
        
        # Print action
        print_action = QAction("طباعة", self)
        print_action.triggered.connect(lambda: self.print_transaction(transaction_id))
        context_menu.addAction(print_action)
        
        # Show the context menu
        context_menu.exec(self.transactions_table.mapToGlobal(position))
    
    def update_transaction_status(self, transaction_id, new_status):
        """Update the status of a transaction."""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"} if self.user_token else {}
            data = {
                "transaction_id": transaction_id,
                "status": new_status
            }
            response = requests.post(f"{self.api_url}/update-transaction-status/", json=data, headers=headers)
            
            if response.status_code == 200:
                QMessageBox.information(self, "نجاح", "تم تحديث حالة التحويل بنجاح")
                self.load_transactions()  # Refresh the list
            else:
                QMessageBox.warning(self, "خطأ", f"فشل تحديث حالة التحويل: رمز الحالة {response.status_code}")
        except Exception as e:
            print(f"Error updating transaction status: {e}")
            QMessageBox.critical(self, "خطأ في الاتصال", 
                               "تعذر الاتصال بالخادم. الرجاء التحقق من اتصالك بالإنترنت وحالة الخادم.")
    
    def print_transaction(self, transaction_id):
        """Print a transaction."""
        # This is a placeholder - in a real app, you would implement actual printing
        QMessageBox.information(self, "طباعة", f"سيتم طباعة التحويل رقم {transaction_id}")
    
    def open_search_dialog(self):
        """Open the search dialog."""
        search_dialog = UserSearchDialog(self.user_token, self)
        search_dialog.exec()

class TransactionDetailsDialog(QDialog):
    """Dialog for displaying transaction details."""
    
    def __init__(self, transaction, parent=None):
        super().__init__(parent)
        self.transaction = transaction
        
        self.setWindowTitle("تفاصيل التحويل")
        self.setGeometry(300, 300, 500, 400)
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
                font-family: Arial;
            }
            QLabel {
                color: #333;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #3498db;
                border-radius: 5px;
                margin-top: 1em;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #3498db;
            }
        """)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout()
        
        # Transaction info group
        transaction_group = QGroupBox("معلومات التحويل")
        transaction_layout = QFormLayout()
        
        # Transaction ID
        transaction_id_label = QLabel("رقم التحويل:")
        transaction_id_value = QLabel(str(self.transaction.get("id", "")))
        transaction_id_value.setStyleSheet("font-weight: bold;")
        transaction_layout.addRow(transaction_id_label, transaction_id_value)
        
        # Date
        date_label = QLabel("التاريخ:")
        date_value = QLabel(self.transaction.get("date", ""))
        date_value.setStyleSheet("font-weight: bold;")
        transaction_layout.addRow(date_label, date_value)
        
        # Amount
        amount_label = QLabel("المبلغ:")
        amount = self.transaction.get("amount", 0)
        formatted_amount = f"{float(amount):,.2f}" if amount else "0.00"
        amount_value = QLabel(formatted_amount)
        amount_value.setStyleSheet("font-weight: bold;")
        transaction_layout.addRow(amount_label, amount_value)
        
        # Status
        status_label = QLabel("الحالة:")
        status = self.transaction.get("status", "pending")
        status_arabic = self.get_status_arabic(status)
        status_value = QLabel(status_arabic)
        status_value.setStyleSheet(f"font-weight: bold; color: {self.get_status_text_color(status)};")
        transaction_layout.addRow(status_label, status_value)
        
        transaction_group.setLayout(transaction_layout)
        layout.addWidget(transaction_group)
        
        # Sender info group
        sender_group = QGroupBox("معلومات المرسل")
        sender_layout = QFormLayout()
        
        # Sender name
        sender_name_label = QLabel("الاسم:")
        sender_name_value = QLabel(self.transaction.get("sender_name", ""))
        sender_name_value.setStyleSheet("font-weight: bold;")
        sender_layout.addRow(sender_name_label, sender_name_value)
        
        # Sender mobile
        sender_mobile_label = QLabel("رقم الهاتف:")
        sender_mobile_value = QLabel(self.transaction.get("sender_mobile", ""))
        sender_layout.addRow(sender_mobile_label, sender_mobile_value)
        
        # Sender ID
        sender_id_label = QLabel("رقم الهوية:")
        sender_id_value = QLabel(self.transaction.get("sender_id", ""))
        sender_layout.addRow(sender_id_label, sender_id_value)
        
        # Sender address
        sender_address_label = QLabel("العنوان:")
        sender_address_value = QLabel(self.transaction.get("sender_address", ""))
        sender_layout.addRow(sender_address_label, sender_address_value)
        
        sender_group.setLayout(sender_layout)
        layout.addWidget(sender_group)
        
        # Receiver info group
        receiver_group = QGroupBox("معلومات المستلم")
        receiver_layout = QFormLayout()
        
        # Receiver name
        receiver_name_label = QLabel("الاسم:")
        receiver_name_value = QLabel(self.transaction.get("receiver_name", ""))
        receiver_name_value.setStyleSheet("font-weight: bold;")
        receiver_layout.addRow(receiver_name_label, receiver_name_value)
        
        # Receiver mobile
        receiver_mobile_label = QLabel("رقم الهاتف:")
        receiver_mobile_value = QLabel(self.transaction.get("receiver_mobile", ""))
        receiver_layout.addRow(receiver_mobile_label, receiver_mobile_value)
        
        # Receiver ID
        receiver_id_label = QLabel("رقم الهوية:")
        receiver_id_value = QLabel(self.transaction.get("receiver_id", ""))
        receiver_layout.addRow(receiver_id_label, receiver_id_value)
        
        # Receiver address
        receiver_address_label = QLabel("العنوان:")
        receiver_address_value = QLabel(self.transaction.get("receiver_address", ""))
        receiver_layout.addRow(receiver_address_label, receiver_address_value)
        
        receiver_group.setLayout(receiver_layout)
        layout.addWidget(receiver_group)
        
        # Additional info group
        additional_group = QGroupBox("معلومات إضافية")
        additional_layout = QFormLayout()
        
        # Employee
        employee_label = QLabel("الموظف:")
        employee_value = QLabel(self.transaction.get("employee_name", ""))
        additional_layout.addRow(employee_label, employee_value)
        
        # Branch
        branch_label = QLabel("الفرع:")
        branch_value = QLabel(self.transaction.get("branch_name", ""))
        additional_layout.addRow(branch_label, branch_value)
        
        # Notes
        notes_label = QLabel("ملاحظات:")
        notes_value = QLabel(self.transaction.get("notes", ""))
        notes_value.setWordWrap(True)
        additional_layout.addRow(notes_label, notes_value)
        
        additional_group.setLayout(additional_layout)
        layout.addWidget(additional_group)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        print_button = QPushButton("طباعة")
        print_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        print_button.clicked.connect(self.print_transaction)
        buttons_layout.addWidget(print_button)
        
        close_button = QPushButton("إغلاق")
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        close_button.clicked.connect(self.accept)
        buttons_layout.addWidget(close_button)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def get_status_arabic(self, status):
        """Convert status to Arabic."""
        status_map = {
            "pending": "قيد الانتظار",
            "processing": "قيد المعالجة",
            "completed": "مكتمل",
            "cancelled": "ملغي",
            "rejected": "مرفوض",
            "on_hold": "معلق"
        }
        return status_map.get(status, status)
    
    def get_status_text_color(self, status):
        """Get text color for status."""
        status_colors = {
            "pending": "#f39c12",  # Orange
            "processing": "#3498db",  # Blue
            "completed": "#2ecc71",  # Green
            "cancelled": "#e74c3c",  # Red
            "rejected": "#c0392b",  # Darker red
            "on_hold": "#f1c40f"  # Yellow
        }
        return status_colors.get(status, "#333333")  # Dark gray default
    
    def print_transaction(self):
        """Print the transaction."""
        # This is a placeholder - in a real app, you would implement actual printing
        QMessageBox.information(self, "طباعة", f"سيتم طباعة التحويل رقم {self.transaction.get('id', '')}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MoneyTransferApp()
    window.show()
    sys.exit(app.exec())
