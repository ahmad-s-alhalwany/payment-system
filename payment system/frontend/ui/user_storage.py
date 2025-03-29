import sqlite3
import os
import json
from datetime import datetime

class UserStorage:
    """Class for storing and retrieving user information for search functionality."""
    
    def __init__(self, db_path="user_data.db"):
        """Initialize the user storage with database path."""
        self.db_path = db_path
        self.initialize_db()
    
    def initialize_db(self):
        """Create database and tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            mobile TEXT,
            governorate TEXT,
            location TEXT,
            created_at TEXT,
            last_transaction TEXT,
            metadata TEXT
        )
        ''')
        
        # Create transactions table for user history
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            transaction_id INTEGER,
            transaction_type TEXT,
            amount REAL,
            currency TEXT,
            branch_name TEXT,
            transaction_date TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, name, mobile=None, governorate=None, location=None, metadata=None):
        """Add a new user to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute("SELECT id FROM users WHERE name = ? AND mobile = ?", (name, mobile))
        existing_user = cursor.fetchone()
        
        if existing_user:
            user_id = existing_user[0]
        else:
            # Insert new user
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            metadata_json = json.dumps(metadata) if metadata else None
            
            cursor.execute('''
            INSERT INTO users (name, mobile, governorate, location, created_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, mobile, governorate, location, created_at, metadata_json))
            
            user_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return user_id
    
    def update_user(self, user_id, name=None, mobile=None, governorate=None, location=None, metadata=None):
        """Update user information."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current user data
        cursor.execute("SELECT name, mobile, governorate, location, metadata FROM users WHERE id = ?", (user_id,))
        current_data = cursor.fetchone()
        
        if not current_data:
            conn.close()
            return False
        
        # Update only provided fields
        new_name = name if name is not None else current_data[0]
        new_mobile = mobile if mobile is not None else current_data[1]
        new_governorate = governorate if governorate is not None else current_data[2]
        new_location = location if location is not None else current_data[3]
        
        # Handle metadata update
        if metadata is not None:
            current_metadata = json.loads(current_data[4]) if current_data[4] else {}
            current_metadata.update(metadata)
            new_metadata = json.dumps(current_metadata)
        else:
            new_metadata = current_data[4]
        
        cursor.execute('''
        UPDATE users 
        SET name = ?, mobile = ?, governorate = ?, location = ?, metadata = ?
        WHERE id = ?
        ''', (new_name, new_mobile, new_governorate, new_location, new_metadata, user_id))
        
        conn.commit()
        conn.close()
        
        return True
    
    def add_transaction(self, user_id, transaction_id, transaction_type, amount, currency, branch_name):
        """Add a transaction record for a user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        transaction_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Insert transaction
        cursor.execute('''
        INSERT INTO user_transactions 
        (user_id, transaction_id, transaction_type, amount, currency, branch_name, transaction_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, transaction_id, transaction_type, amount, currency, branch_name, transaction_date))
        
        # Update last transaction date for user
        cursor.execute('''
        UPDATE users SET last_transaction = ? WHERE id = ?
        ''', (transaction_date, user_id))
        
        conn.commit()
        conn.close()
        
        return True
    
    def search_users(self, query, search_type="name"):
        """Search for users based on different criteria."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if search_type == "name":
            cursor.execute("SELECT * FROM users WHERE name LIKE ?", (f"%{query}%",))
        elif search_type == "mobile":
            cursor.execute("SELECT * FROM users WHERE mobile LIKE ?", (f"%{query}%",))
        elif search_type == "governorate":
            cursor.execute("SELECT * FROM users WHERE governorate LIKE ?", (f"%{query}%",))
        elif search_type == "location":
            cursor.execute("SELECT * FROM users WHERE location LIKE ?", (f"%{query}%",))
        else:
            # Search across all fields
            cursor.execute('''
            SELECT * FROM users 
            WHERE name LIKE ? OR mobile LIKE ? OR governorate LIKE ? OR location LIKE ?
            ''', (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"))
        
        users = cursor.fetchall()
        
        # Convert to list of dictionaries
        user_list = []
        for user in users:
            user_dict = {
                "id": user[0],
                "name": user[1],
                "mobile": user[2],
                "governorate": user[3],
                "location": user[4],
                "created_at": user[5],
                "last_transaction": user[6],
                "metadata": json.loads(user[7]) if user[7] else None
            }
            user_list.append(user_dict)
        
        conn.close()
        
        return user_list
    
    def get_user_transactions(self, user_id):
        """Get all transactions for a specific user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM user_transactions WHERE user_id = ? ORDER BY transaction_date DESC
        ''', (user_id,))
        
        transactions = cursor.fetchall()
        
        # Convert to list of dictionaries
        transaction_list = []
        for transaction in transactions:
            transaction_dict = {
                "id": transaction[0],
                "user_id": transaction[1],
                "transaction_id": transaction[2],
                "transaction_type": transaction[3],
                "amount": transaction[4],
                "currency": transaction[5],
                "branch_name": transaction[6],
                "transaction_date": transaction[7]
            }
            transaction_list.append(transaction_dict)
        
        conn.close()
        
        return transaction_list
    
    def get_user_by_id(self, user_id):
        """Get user information by ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return None
        
        user_dict = {
            "id": user[0],
            "name": user[1],
            "mobile": user[2],
            "governorate": user[3],
            "location": user[4],
            "created_at": user[5],
            "last_transaction": user[6],
            "metadata": json.loads(user[7]) if user[7] else None
        }
        
        conn.close()
        
        return user_dict
    
    def get_user_by_mobile(self, mobile):
        """Get user information by mobile number."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE mobile = ?", (mobile,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return None
        
        user_dict = {
            "id": user[0],
            "name": user[1],
            "mobile": user[2],
            "governorate": user[3],
            "location": user[4],
            "created_at": user[5],
            "last_transaction": user[6],
            "metadata": json.loads(user[7]) if user[7] else None
        }
        
        conn.close()
        
        return user_dict
    
    def get_all_users(self, limit=100, offset=0):
        """Get all users with pagination."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users ORDER BY name LIMIT ? OFFSET ?", (limit, offset))
        users = cursor.fetchall()
        
        # Convert to list of dictionaries
        user_list = []
        for user in users:
            user_dict = {
                "id": user[0],
                "name": user[1],
                "mobile": user[2],
                "governorate": user[3],
                "location": user[4],
                "created_at": user[5],
                "last_transaction": user[6],
                "metadata": json.loads(user[7]) if user[7] else None
            }
            user_list.append(user_dict)
        
        conn.close()
        
        return user_list
    
    def count_users(self):
        """Get total count of users in database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        
        conn.close()
        
        return count
    
    def delete_user(self, user_id):
        """Delete a user and all their transactions."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Delete user transactions first (foreign key constraint)
        cursor.execute("DELETE FROM user_transactions WHERE user_id = ?", (user_id,))
        
        # Delete user
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        
        conn.commit()
        conn.close()
        
        return True
    
    def add_sample_data(self):
        """Add sample data for testing purposes."""
        # Sample users
        users = [
            {"name": "أحمد محمد", "mobile": "0912345678", "governorate": "دمشق", "location": "المزة"},
            {"name": "سامر علي", "mobile": "0923456789", "governorate": "حلب", "location": "الجميلية"},
            {"name": "خالد وليد", "mobile": "0934567890", "governorate": "حمص", "location": "الوعر"},
            {"name": "عمر فادي", "mobile": "0945678901", "governorate": "اللاذقية", "location": "الرمل الشمالي"},
            {"name": "سمير فراس", "mobile": "0956789012", "governorate": "طرطوس", "location": "الكورنيش"},
            {"name": "رامي سامر", "mobile": "0967890123", "governorate": "حماة", "location": "السوق"},
            {"name": "محمد علي", "mobile": "0978901234", "governorate": "دير الزور", "location": "الميادين"},
            {"name": "نور الدين", "mobile": "0989012345", "governorate": "الرقة", "location": "المنصور"},
            {"name": "فادي سامي", "mobile": "0990123456", "governorate": "الحسكة", "location": "القامشلي"},
            {"name": "عماد خالد", "mobile": "0901234567", "governorate": "درعا", "location": "المحطة"}
        ]
        
        # Add users
        user_ids = []
        for user in users:
            user_id = self.add_user(
                name=user["name"],
                mobile=user["mobile"],
                governorate=user["governorate"],
                location=user["location"]
            )
            user_ids.append(user_id)
        
        # Sample transactions
        transactions = [
            {"user_id": user_ids[0], "transaction_id": 1001, "transaction_type": "send", "amount": 50000, "currency": "ل.س", "branch_name": "فرع دمشق"},
            {"user_id": user_ids[1], "transaction_id": 1001, "transaction_type": "receive", "amount": 50000, "currency": "ل.س", "branch_name": "فرع حلب"},
            {"user_id": user_ids[2], "transaction_id": 1002, "transaction_type": "send", "amount": 100, "currency": "دولار", "branch_name": "فرع حمص"},
            {"user_id": user_ids[3], "transaction_id": 1002, "transaction_type": "receive", "amount": 100, "currency": "دولار", "branch_name": "فرع دمشق"},
            {"user_id": user_ids[4], "transaction_id": 1003, "transaction_type": "send", "amount": 200, "currency": "يورو", "branch_name": "فرع اللاذقية"},
            {"user_id": user_ids[5], "transaction_id": 1003, "transaction_type": "receive", "amount": 200, "currency": "يورو", "branch_name": "فرع حمص"},
            {"user_id": user_ids[6], "transaction_id": 1004, "transaction_type": "send", "amount": 75000, "currency": "ل.س", "branch_name": "فرع حلب"},
            {"user_id": user_ids[7], "transaction_id": 1004, "transaction_type": "receive", "amount": 75000, "currency": "ل.س", "branch_name": "فرع طرطوس"},
            {"user_id": user_ids[8], "transaction_id": 1005, "transaction_type": "send", "amount": 150, "currency": "دولار", "branch_name": "فرع دمشق"},
            {"user_id": user_ids[9], "transaction_id": 1005, "transaction_type": "receive", "amount": 150, "currency": "دولار", "branch_name": "فرع حماة"}
        ]
        
        # Add transactions
        for transaction in transactions:
            self.add_transaction(
                user_id=transaction["user_id"],
                transaction_id=transaction["transaction_id"],
                transaction_type=transaction["transaction_type"],
                amount=transaction["amount"],
                currency=transaction["currency"],
                branch_name=transaction["branch_name"]
            )
        
        return True

# Example usage
if __name__ == "__main__":
    # Create storage instance
    storage = UserStorage()
    
    # Add sample data
    storage.add_sample_data()
    
    # Test search
    results = storage.search_users("أحمد")
    print(f"Found {len(results)} users matching 'أحمد':")
    for user in results:
        print(f"  - {user['name']} ({user['mobile']})")
    
    # Test get transactions
    if results:
        user_id = results[0]["id"]
        transactions = storage.get_user_transactions(user_id)
        print(f"\nTransactions for {results[0]['name']}:")
        for transaction in transactions:
            print(f"  - {transaction['transaction_type']}: {transaction['amount']} {transaction['currency']} at {transaction['branch_name']}")
