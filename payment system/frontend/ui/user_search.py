from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QComboBox,
    QTableWidget, QTableWidgetItem, QGroupBox, QRadioButton, QButtonGroup, QMessageBox,
    QHeaderView
)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt
import requests

SEARCH_TRANSACTIONS_API_URL = "http://127.0.0.1:8000/search-transactions/"

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

class UserSearchDialog(QDialog):
    """Dialog for searching and viewing user information."""
    
    def __init__(self, token=None, api_url="http://127.0.0.1:8000", parent=None):
        super().__init__(parent)
        self.token = token
        self.api_url = api_url
        
        self.setWindowTitle("بحث المستخدمين")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
                font-family: Arial;
            }
            QLabel {
                color: #333;
            }
            QLineEdit, QComboBox {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
            }
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
        
        # Main layout
        main_layout = QVBoxLayout()
        
        # Title
        title = QLabel("بحث المستخدمين")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        main_layout.addWidget(title)
        
        # Search group
        search_group = ModernGroupBox("بحث", "#3498db")
        search_layout = QVBoxLayout()
        
        # Search criteria
        criteria_layout = QHBoxLayout()
        
        # Radio buttons for search type
        self.search_type_group = QButtonGroup(self)
        
        # Name search
        self.name_radio = QRadioButton("بحث بالاسم")
        self.name_radio.setChecked(True)  # Default selection
        self.search_type_group.addButton(self.name_radio)
        criteria_layout.addWidget(self.name_radio)
        
        # Mobile search
        self.mobile_radio = QRadioButton("بحث برقم الهاتف")
        self.search_type_group.addButton(self.mobile_radio)
        criteria_layout.addWidget(self.mobile_radio)
        
        # Governorate search
        self.governorate_radio = QRadioButton("بحث بالمحافظة")
        self.search_type_group.addButton(self.governorate_radio)
        criteria_layout.addWidget(self.governorate_radio)
        
        # Location search
        self.location_radio = QRadioButton("بحث بالموقع")
        self.search_type_group.addButton(self.location_radio)
        criteria_layout.addWidget(self.location_radio)
        
        # All search
        self.all_radio = QRadioButton("بحث شامل")
        self.search_type_group.addButton(self.all_radio)
        criteria_layout.addWidget(self.all_radio)
        
        search_layout.addLayout(criteria_layout)
        
        # Search input
        search_input_layout = QHBoxLayout()
        
        search_label = QLabel("كلمة البحث:")
        search_input_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("أدخل كلمة البحث...")
        search_input_layout.addWidget(self.search_input)
        
        self.search_button = ModernButton("بحث", color="#3498db")
        self.search_button.clicked.connect(self.search_users)
        search_input_layout.addWidget(self.search_button)
        
        search_layout.addLayout(search_input_layout)
        search_group.setLayout(search_layout)
        main_layout.addWidget(search_group)
        
        # Results group
        results_group = ModernGroupBox("نتائج البحث", "#e74c3c")
        results_layout = QVBoxLayout()
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(8)
        self.results_table.setHorizontalHeaderLabels([
            "رقم التحويل", "المرسل", "المستلم", "المبلغ", "العملة", "الفرع المستلم", "الحالة", "التاريخ"
        ])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        results_layout.addWidget(self.results_table)
        results_group.setLayout(results_layout)
        main_layout.addWidget(results_group)
        
        # User info group
        user_info_group = ModernGroupBox("معلومات المستخدم", "#3498db")
        user_info_layout = QVBoxLayout()
        
        # User info will be displayed here when a user is selected
        self.user_info_label = QLabel("اختر مستخدمًا من نتائج البحث لعرض معلوماته")
        self.user_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        user_info_layout.addWidget(self.user_info_label)
        
        user_info_group.setLayout(user_info_layout)
        main_layout.addWidget(user_info_group)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.close_button = ModernButton("إغلاق", color="#e74c3c")
        self.close_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.close_button)
        
        self.view_details_button = ModernButton("عرض التفاصيل", color="#2ecc71")
        self.view_details_button.clicked.connect(self.view_user_details)
        self.view_details_button.setEnabled(False)  # Disabled until a user is selected
        buttons_layout.addWidget(self.view_details_button)
        
        main_layout.addLayout(buttons_layout)
        
        self.setLayout(main_layout)
        
        # Connect selection change
        self.results_table.itemSelectionChanged.connect(self.on_selection_changed)
    
    def search_users(self):
        """Search for users based on the selected criteria."""
        search_term = self.search_input.text().strip()
        if not search_term:
            QMessageBox.warning(self, "تنبيه", "الرجاء إدخال كلمة البحث")
            return
        
        # Determine search type
        search_type = "name"  # Default
        if self.mobile_radio.isChecked():
            search_type = "mobile"
        elif self.governorate_radio.isChecked():
            search_type = "governorate"
        elif self.location_radio.isChecked():
            search_type = "location"
        elif self.all_radio.isChecked():
            search_type = "all"
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            data = {
                "search_type": search_type,
                "search_term": search_term
            }
            response = requests.post(f"{self.api_url}/search-transactions/", json=data, headers=headers)
            
            if response.status_code == 200:
                transactions_data = response.json()
                transactions = transactions_data.get("transactions", [])
                self.results_table.setRowCount(len(transactions))
                
                for i, transaction in enumerate(transactions):
                    self.results_table.setItem(i, 0, QTableWidgetItem(str(transaction.get("id", ""))))
                    self.results_table.setItem(i, 1, QTableWidgetItem(transaction.get("sender", "")))
                    self.results_table.setItem(i, 2, QTableWidgetItem(transaction.get("receiver", "")))
                    self.results_table.setItem(i, 3, QTableWidgetItem(str(transaction.get("amount", ""))))
                    self.results_table.setItem(i, 4, QTableWidgetItem(transaction.get("currency", "")))
                    self.results_table.setItem(i, 5, QTableWidgetItem(transaction.get("receiver_governorate", "")))
                    
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
                    
                    self.results_table.setItem(i, 6, status_item)
                    self.results_table.setItem(i, 7, QTableWidgetItem(transaction.get("date", "")))
                    
                    # Store the transaction data in the first cell for later use
                    self.results_table.item(i, 0).setData(Qt.ItemDataRole.UserRole, transaction)
            else:
                QMessageBox.warning(self, "خطأ", f"فشل البحث: رمز الحالة {response.status_code}")
        except Exception as e:
            print(f"Error searching: {e}")
            QMessageBox.critical(self, "خطأ في الاتصال", 
                               "تعذر الاتصال بالخادم. الرجاء التحقق من اتصالك بالإنترنت وحالة الخادم.")
    
    def on_selection_changed(self):
        """Handle selection change in the results table."""
        selected_rows = self.results_table.selectionModel().selectedRows()
        has_selection = len(selected_rows) > 0
        
        self.view_details_button.setEnabled(has_selection)
        
        if has_selection:
            row = selected_rows[0].row()
            transaction = self.results_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            
            # Update user info label with basic information
            self.user_info_label.setText(
                f"المرسل: {transaction.get('sender', '')}\n"
                f"رقم هاتف المرسل: {transaction.get('sender_mobile', '')}\n"
                f"المستلم: {transaction.get('receiver', '')}\n"
                f"رقم هاتف المستلم: {transaction.get('receiver_mobile', '')}"
            )
    
    def view_user_details(self):
        """View detailed information about the selected user."""
        selected_rows = self.results_table.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        transaction = self.results_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        # Create a dialog to display detailed information
        details_dialog = QDialog(self)
        details_dialog.setWindowTitle("تفاصيل التحويل")
        details_dialog.setGeometry(150, 150, 500, 400)
        details_dialog.setStyleSheet("""
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
        close_button.clicked.connect(details_dialog.accept)
        layout.addWidget(close_button)
        
        details_dialog.setLayout(layout)
        details_dialog.exec()
