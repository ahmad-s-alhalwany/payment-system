import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QFont
from ui.money_transfer_improved import MoneyTransferApp
from ui.dashboard_improved import DirectorDashboard
from ui.branch_manager_dashboard import BranchManagerDashboard
from ui.user_search import UserSearchDialog
from login_fixed import LoginWindow

def get_application_styles():
    """Return centralized stylesheet for the entire application."""
    return """
        /* Base styles */
        QWidget {
            font-family: Arial;
            background-color: #f5f5f5;
        }
        
        /* Message Box Styling */
        QMessageBox {
            background-color: #f5f5f5;
        }
        QMessageBox QPushButton {
            background-color: #2c3e50;
            color: white;
            border-radius: 5px;
            padding: 6px 12px;
            font-weight: bold;
        }
        QMessageBox QPushButton:hover {
            background-color: #34495e;
        }

        /* Modern UI Components */
        QPushButton {
            background-color: #2980b9;
            color: white;
            border-radius: 8px;
            padding: 10px 15px;
            font-size: 13px;
            border: none;
        }
        QPushButton:hover { background-color: #3498db; }
        QPushButton:pressed { background-color: #1c6ea4; }

        /* Tab Widget Styling */
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
        }
        QTabBar::tab:selected {
            background-color: #2c3e50;
            color: white;
        }

        /* Table Widget Styling */
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
        }
        QTableWidget::item { padding: 5px; }
        QTableWidget::item:selected {
            background-color: #3498db;
            color: white;
        }
    """

def launch_dashboard(login_data: dict):
    """Initialize the appropriate dashboard based on user role."""
    try:
        if login_data["role"] == "director":
            window = DirectorDashboard(token=login_data["token"])
            window.setWindowTitle("لوحة تحكم المدير - نظام التحويلات المالية")
        elif login_data["role"] == "branch_manager":
            print(f"Initializing Branch Manager Dashboard (Branch ID: {login_data['branch_id']})")
            window = BranchManagerDashboard(
                branch_id=login_data["branch_id"],
                token=login_data["token"]
            )
            window.setWindowTitle(f"لوحة تحكم مدير الفرع - الفرع {login_data['branch_id']}")
        elif login_data["role"] == "employee":
            window = MoneyTransferApp(
                user_token=login_data["token"],
                branch_id=login_data["branch_id"],
                user_id=login_data["user_id"],
                user_role=login_data["role"],
                username=login_data["username"]
            )
            window.setWindowTitle(f"واجهة الموظف - {login_data['username']}")
        else:
            raise ValueError("Unknown user role")
        
        window.show()
        return window
    except Exception as e:
        QMessageBox.critical(None, "خطأ فادح", f"فشل تحميل الواجهة: {str(e)}")
        return None

def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Arial", 10))
    app.setStyleSheet(get_application_styles())

    login_window = LoginWindow()
    
    if login_window.exec() != 1:  # Login failed/canceled
        sys.exit()

    # Collect login data with validation
    login_data = {
        "role": getattr(login_window, "user_role", None),
        "branch_id": getattr(login_window, "branch_id", None),
        "user_id": getattr(login_window, "user_id", None),
        "token": getattr(login_window, "token", None),
        "username": login_window.username_input.text().strip()  # Direct access to username field
    }

    # Validate critical fields
    if not all([login_data["role"], login_data["token"]]):
        QMessageBox.warning(None, "خطأ", "بيانات المستخدم غير مكتملة!")
        sys.exit()

    window = launch_dashboard(login_data)
    if not window:
        sys.exit()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()