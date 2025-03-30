import sys
import requests
from datetime import datetime
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, 
    QTableWidgetItem, QComboBox, QMessageBox, QGroupBox, QFormLayout, 
    QDateEdit, QDoubleSpinBox, QCheckBox, QMenu, QStatusBar
)
from PyQt6.QtGui import QColor, QAction, QFont
from PyQt6.QtCore import Qt, QDate, QTimer

TRANSACTIONS_API_URL = "http://127.0.0.1:8000/transactions/"

class TransactionHistory(QDialog):
    """Enhanced transaction history dialog combining best features of both versions."""
    
    def __init__(self, branch_id=None, token=None, user_role="employee"):
        super().__init__()
        self.branch_id = branch_id
        self.token = token
        self.user_role = user_role
        
        self.setWindowTitle("سجل التحويلات")
        self.setGeometry(150, 150, 1000, 600)
        
        self.setup_ui()
        self.load_transactions()
        
        # Set up auto-refresh timer (every 2 minutes)
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.load_transactions)
        self.refresh_timer.start(120000)
    
    def setup_ui(self):
        """Set up the UI components with improved design."""
        layout = QVBoxLayout()
        
        # Header with filter controls
        header_layout = QHBoxLayout()
        
        # Filter dropdown (from old version)
        self.filter_dropdown = QComboBox()
        self.filter_dropdown.addItems([
            "جميع التحويلات", 
            "التحويلات الواردة", 
            "التحويلات الصادرة",
            "التحويلات المتعلقة بالفرع"
        ])
        self.filter_dropdown.setCurrentIndex(3)  # Default to branch-related
        self.filter_dropdown.currentIndexChanged.connect(self.load_transactions)
        header_layout.addWidget(QLabel("تصفية:"))
        header_layout.addWidget(self.filter_dropdown)
        
        # Spacer
        header_layout.addStretch()
        
        # Buttons (from new version)
        self.filter_button = QPushButton("تصفية متقدمة")
        self.filter_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                padding: 5px 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.filter_button.clicked.connect(self.show_advanced_filter)
        header_layout.addWidget(self.filter_button)
        
        self.refresh_button = QPushButton("تحديث")
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 5px;
                padding: 5px 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        self.refresh_button.clicked.connect(self.load_transactions)
        header_layout.addWidget(self.refresh_button)
        
        self.export_button = QPushButton("تصدير")
        self.export_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 5px;
                padding: 5px 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.export_button.clicked.connect(self.export_transactions)
        header_layout.addWidget(self.export_button)
        
        layout.addLayout(header_layout)
        
        # Transactions table (combining both versions)
        self.table = QTableWidget()
        self.table.setColumnCount(15)
        self.table.setHorizontalHeaderLabels([
            "رقم العملية", "المرسل", "رقم المرسل", "المحافظة (المرسل)", "الموقع (المرسل)",
            "المستلم", "رقم المستلم", "المحافظة (المستلم)", "الموقع (المستلم)", "المبلغ", 
            "العملة", "نوع التحويل", "الرسالة", "اسم الموظف", "التاريخ"
        ])
        
        # Styling from new version
        self.table.setStyleSheet("""
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
        
        # Enable sorting
        self.table.setSortingEnabled(True)
        
        # Resize columns to content
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)
        
        # Connect double-click and context menu
        self.table.itemDoubleClicked.connect(self.show_transaction_details)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        layout.addWidget(self.table)
        
        # Status bar (from new version)
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel("جاهز")
        self.status_label.setFont(QFont("Arial", 10))
        status_layout.addWidget(self.status_label)
        
        self.count_label = QLabel("عدد التحويلات: 0")
        self.count_label.setFont(QFont("Arial", 10))
        status_layout.addWidget(self.count_label, alignment=Qt.AlignmentFlag.AlignRight)
        
        layout.addLayout(status_layout)
        
        self.setLayout(layout)
    
    def get_filter_type(self, index):
        """Convert dropdown index to API filter type (from old version)."""
        filter_types = ["all", "incoming", "outgoing", "branch_related"]
        return filter_types[index] if 0 <= index < len(filter_types) else "branch_related"
    
    def determine_transaction_type(self, transaction):
        """Determine transaction type (from old version)."""
        if str(transaction.get("branch_id")) == str(self.branch_id):
            return "صادر"  # Outgoing
        elif transaction.get("receiver_governorate") == transaction.get("branch_governorate"):
            return "وارد"  # Incoming
        return "غير مرتبط"  # Not related
    
    def load_transactions(self):
        """Load transactions with error handling (combined from both versions)."""
        self.status_label.setText("جاري تحميل البيانات...")
        
        try:
            # Get filter type from dropdown
            filter_index = self.filter_dropdown.currentIndex()
            filter_type = self.get_filter_type(filter_index)
            
            # Build request URL
            url = TRANSACTIONS_API_URL
            if self.branch_id:
                url = f"{TRANSACTIONS_API_URL}?branch_id={self.branch_id}&filter_type={filter_type}"
            
            # Add advanced filters if any
            if hasattr(self, 'advanced_filters'):
                for key, value in self.advanced_filters.items():
                    url += f"&{key}={value}"
            
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json().get("transactions", [])
                
                self.table.setRowCount(len(data))
                
                for row_idx, transaction in enumerate(data):
                    self.set_table_data(row_idx, transaction)
                
                self.status_label.setText("تم تحميل البيانات بنجاح")
                self.count_label.setText(f"عدد التحويلات: {len(data)}")
                
            else:
                error_msg = response.json().get('detail', response.text)
                self.status_label.setText("فشل في تحميل البيانات")
                QMessageBox.warning(self, "خطأ", f"حدث خطأ أثناء تحميل البيانات:\n{error_msg}")
                
        except Exception as e:
            self.status_label.setText("خطأ في الاتصال")
            QMessageBox.critical(self, "خطأ", f"تعذر الاتصال بالخادم:\n{str(e)}")
    
    def set_table_data(self, row_idx, transaction):
        """Populate table row with transaction data (from old version with enhancements)."""
        # Transaction ID
        self.table.setItem(row_idx, 0, QTableWidgetItem(str(transaction.get("id", ""))))
        
        # Sender info
        self.table.setItem(row_idx, 1, QTableWidgetItem(transaction.get("sender", "")))
        self.table.setItem(row_idx, 2, QTableWidgetItem(transaction.get("sender_mobile", "")))
        self.table.setItem(row_idx, 3, QTableWidgetItem(transaction.get("sender_governorate", "")))
        self.table.setItem(row_idx, 4, QTableWidgetItem(transaction.get("sender_location", "N/A")))
        
        # Receiver info
        self.table.setItem(row_idx, 5, QTableWidgetItem(transaction.get("receiver", "")))
        self.table.setItem(row_idx, 6, QTableWidgetItem(transaction.get("receiver_mobile", "")))
        self.table.setItem(row_idx, 7, QTableWidgetItem(transaction.get("receiver_governorate", "")))
        self.table.setItem(row_idx, 8, QTableWidgetItem(transaction.get("receiver_location", "N/A")))
        
        # Amount and currency
        amount = transaction.get("amount", 0)
        self.table.setItem(row_idx, 9, QTableWidgetItem(f"{float(amount):,.2f}" if amount else "0.00"))
        self.table.setItem(row_idx, 10, QTableWidgetItem(transaction.get("currency", "")))
        
        # Transaction type with coloring
        transaction_type = self.determine_transaction_type(transaction)
        type_item = QTableWidgetItem(transaction_type)
        
        if transaction_type == "وارد":
            type_item.setBackground(QColor("#d5f5e3"))  # Light green
        elif transaction_type == "صادر":
            type_item.setBackground(QColor("#fadbd8"))  # Light red
        
        self.table.setItem(row_idx, 11, type_item)
        
        # Message, employee, and date
        self.table.setItem(row_idx, 12, QTableWidgetItem(transaction.get("message", "")))
        self.table.setItem(row_idx, 13, QTableWidgetItem(transaction.get("employee_name", "N/A")))
        
        # Format date properly
        date_str = transaction.get("date", "")
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%Y-%m-%d")
        except:
            formatted_date = date_str
        self.table.setItem(row_idx, 14, QTableWidgetItem(formatted_date))
    
    def show_advanced_filter(self):
        """Show advanced filter dialog (from new version)."""
        filter_dialog = TransactionFilterDialog(self)
        if filter_dialog.exec() == QDialog.DialogCode.Accepted:
            self.advanced_filters = filter_dialog.get_filters()
            self.load_transactions()
    
    def show_transaction_details(self, item):
        """Show transaction details dialog (from new version with old data)."""
        row = item.row()
        transaction_id = self.table.item(row, 0).text()
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            response = requests.get(f"{TRANSACTIONS_API_URL}{transaction_id}", headers=headers)
            
            if response.status_code == 200:
                transaction = response.json()
                details_dialog = TransactionDetailsDialog(transaction, self)
                details_dialog.exec()
            else:
                QMessageBox.warning(self, "خطأ", "فشل تحميل تفاصيل التحويل")
                
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"تعذر الاتصال بالخادم:\n{str(e)}")
    
    def show_context_menu(self, position):
        """Show context menu for transactions (from new version)."""
        if not self.table.selectedItems():
            return
        
        row = self.table.selectedItems()[0].row()
        transaction_id = self.table.item(row, 0).text()
        
        menu = QMenu(self)
        
        # View details action
        view_action = QAction("عرض التفاصيل", self)
        view_action.triggered.connect(lambda: self.show_transaction_details(self.table.item(row, 0)))
        menu.addAction(view_action)
        
        # Status change actions for managers/directors
        if self.user_role in ["branch_manager", "director"]:
            status_menu = QMenu("تغيير الحالة", self)
            
            statuses = [
                ("إلى قيد الانتظار", "pending"),
                ("إلى قيد المعالجة", "processing"),
                ("إلى مكتمل", "completed"),
                ("إلى ملغي", "cancelled")
            ]
            
            for text, status in statuses:
                action = QAction(text, self)
                action.triggered.connect(
                    lambda checked, tid=transaction_id, s=status: self.update_transaction_status(tid, s))
                status_menu.addAction(action)
            
            menu.addMenu(status_menu)
        
        menu.exec(self.table.mapToGlobal(position))
    
    def update_transaction_status(self, transaction_id, new_status):
        """Update transaction status (from new version)."""
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            data = {"status": new_status}
            
            response = requests.patch(
                f"{TRANSACTIONS_API_URL}{transaction_id}/status/",
                json=data,
                headers=headers
            )
            
            if response.status_code == 200:
                QMessageBox.information(self, "نجاح", "تم تحديث حالة التحويل بنجاح")
                self.load_transactions()
            else:
                QMessageBox.warning(self, "خطأ", "فشل تحديث حالة التحويل")
                
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"تعذر الاتصال بالخادم:\n{str(e)}")
    
    def export_transactions(self):
        """Export transactions to file (placeholder)."""
        QMessageBox.information(self, "تصدير", "سيتم تصدير البيانات إلى ملف Excel")

class TransactionDetailsDialog(QDialog):
    """Transaction details dialog (from new version with old data fields)."""
    
    def __init__(self, transaction, parent=None):
        super().__init__(parent)
        self.transaction = transaction
        
        self.setWindowTitle("تفاصيل التحويل")
        self.setGeometry(300, 300, 500, 500)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the details UI."""
        layout = QVBoxLayout()
        
        # Transaction info group
        trans_group = QGroupBox("معلومات التحويل")
        trans_layout = QFormLayout()
        
        trans_layout.addRow("رقم التحويل:", QLabel(str(self.transaction.get("id", ""))))
        trans_layout.addRow("التاريخ:", QLabel(self.transaction.get("date", "")))
        trans_layout.addRow("المبلغ:", QLabel(f"{float(self.transaction.get('amount', 0)):,.2f}"))
        trans_layout.addRow("العملة:", QLabel(self.transaction.get("currency", "")))
        trans_layout.addRow("الحالة:", QLabel(self.transaction.get("status", "")))
        
        trans_group.setLayout(trans_layout)
        layout.addWidget(trans_group)
        
        # Sender info group
        sender_group = QGroupBox("معلومات المرسل")
        sender_layout = QFormLayout()
        
        sender_layout.addRow("الاسم:", QLabel(self.transaction.get("sender", "")))
        sender_layout.addRow("رقم الهاتف:", QLabel(self.transaction.get("sender_mobile", "")))
        sender_layout.addRow("المحافظة:", QLabel(self.transaction.get("sender_governorate", "")))
        sender_layout.addRow("الموقع:", QLabel(self.transaction.get("sender_location", "")))
        
        sender_group.setLayout(sender_layout)
        layout.addWidget(sender_group)
        
        # Receiver info group
        receiver_group = QGroupBox("معلومات المستلم")
        receiver_layout = QFormLayout()
        
        receiver_layout.addRow("الاسم:", QLabel(self.transaction.get("receiver", "")))
        receiver_layout.addRow("رقم الهاتف:", QLabel(self.transaction.get("receiver_mobile", "")))
        receiver_layout.addRow("المحافظة:", QLabel(self.transaction.get("receiver_governorate", "")))
        receiver_layout.addRow("الموقع:", QLabel(self.transaction.get("receiver_location", "")))
        
        receiver_group.setLayout(receiver_layout)
        layout.addWidget(receiver_group)
        
        # Additional info group
        extra_group = QGroupBox("معلومات إضافية")
        extra_layout = QFormLayout()
        
        extra_layout.addRow("الرسالة:", QLabel(self.transaction.get("message", "")))
        extra_layout.addRow("الموظف:", QLabel(self.transaction.get("employee_name", "")))
        
        extra_group.setLayout(extra_layout)
        layout.addWidget(extra_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        print_btn = QPushButton("طباعة")
        print_btn.setStyleSheet("background-color: #3498db; color: white;")
        print_btn.clicked.connect(self.print_transaction)
        btn_layout.addWidget(print_btn)
        
        close_btn = QPushButton("إغلاق")
        close_btn.setStyleSheet("background-color: #e74c3c; color: white;")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def print_transaction(self):
        """Print transaction (placeholder)."""
        QMessageBox.information(self, "طباعة", "سيتم طباعة تفاصيل التحويل")

class TransactionFilterDialog(QDialog):
    """Advanced filter dialog (from new version)."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("تصفية متقدمة")
        self.setup_ui()
    
    def setup_ui(self):
        """Set up filter UI."""
        layout = QVBoxLayout()
        
        # Date range
        date_group = QGroupBox("نطاق التاريخ")
        date_layout = QFormLayout()
        
        self.start_date = QDateEdit(QDate.currentDate().addMonths(-1))
        self.end_date = QDateEdit(QDate.currentDate())
        
        date_layout.addRow("من:", self.start_date)
        date_layout.addRow("إلى:", self.end_date)
        date_group.setLayout(date_layout)
        layout.addWidget(date_group)
        
        # Amount range
        amount_group = QGroupBox("نطاق المبلغ")
        amount_layout = QFormLayout()
        
        self.min_amount = QDoubleSpinBox()
        self.min_amount.setRange(0, 9999999)
        self.max_amount = QDoubleSpinBox()
        self.max_amount.setRange(0, 9999999)
        self.max_amount.setValue(9999999)
        
        amount_layout.addRow("الحد الأدنى:", self.min_amount)
        amount_layout.addRow("الحد الأقصى:", self.max_amount)
        amount_group.setLayout(amount_layout)
        layout.addWidget(amount_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        reset_btn = QPushButton("إعادة تعيين")
        reset_btn.setStyleSheet("background-color: #95a5a6; color: white;")
        reset_btn.clicked.connect(self.reset_filters)
        btn_layout.addWidget(reset_btn)
        
        apply_btn = QPushButton("تطبيق")
        apply_btn.setStyleSheet("background-color: #2ecc71; color: white;")
        apply_btn.clicked.connect(self.accept)
        btn_layout.addWidget(apply_btn)
        
        cancel_btn = QPushButton("إلغاء")
        cancel_btn.setStyleSheet("background-color: #e74c3c; color: white;")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def reset_filters(self):
        """Reset all filters to default values."""
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        self.end_date.setDate(QDate.currentDate())
        self.min_amount.setValue(0)
        self.max_amount.setValue(9999999)
    
    def get_filters(self):
        """Return filters as dict."""
        return {
            "start_date": self.start_date.date().toString("yyyy-MM-dd"),
            "end_date": self.end_date.date().toString("yyyy-MM-dd"),
            "min_amount": self.min_amount.value(),
            "max_amount": self.max_amount.value()
        }

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TransactionHistory()
    window.show()
    sys.exit(app.exec())