import sqlite3
from datetime import datetime
import json
import os

class UserTransactionHistory:
    def __init__(self, db_path="transactions.db"):
        """Initialize the UserTransactionHistory class with database path."""
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize the database and create necessary tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create user_transaction_history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_transaction_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_mobile TEXT,
                transaction_id TEXT,
                transaction_type TEXT CHECK(transaction_type IN ('sender', 'receiver')),
                transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                amount REAL,
                currency TEXT,
                status TEXT,
                FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE
            )
        """)
        
        # Create user_transaction_stats table for aggregated statistics
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_transaction_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_mobile TEXT UNIQUE,
                total_sent_count INTEGER DEFAULT 0,
                total_sent_amount REAL DEFAULT 0,
                total_received_count INTEGER DEFAULT 0,
                total_received_amount REAL DEFAULT 0,
                last_transaction_date TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def record_transaction(self, transaction_id):
        """Record a transaction in the user history for both sender and receiver."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get transaction details
        cursor.execute("""
            SELECT sender, sender_mobile, receiver, receiver_mobile, amount, currency, status, date
            FROM transactions
            WHERE id = ?
        """, (transaction_id,))
        
        result = cursor.fetchone()
        if not result:
            conn.close()
            return False
        
        sender, sender_mobile, receiver, receiver_mobile, amount, currency, status, date = result
        
        # Record for sender
        cursor.execute("""
            INSERT INTO user_transaction_history 
            (user_mobile, transaction_id, transaction_type, transaction_date, amount, currency, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (sender_mobile, transaction_id, 'sender', date, amount, currency, status))
        
        # Record for receiver
        cursor.execute("""
            INSERT INTO user_transaction_history 
            (user_mobile, transaction_id, transaction_type, transaction_date, amount, currency, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (receiver_mobile, transaction_id, 'receiver', date, amount, currency, status))
        
        # Update statistics for sender
        cursor.execute("""
            INSERT INTO user_transaction_stats 
            (user_mobile, total_sent_count, total_sent_amount, last_transaction_date, last_updated)
            VALUES (?, 1, ?, ?, datetime('now'))
            ON CONFLICT(user_mobile) DO UPDATE SET
            total_sent_count = total_sent_count + 1,
            total_sent_amount = total_sent_amount + ?,
            last_transaction_date = ?,
            last_updated = datetime('now')
        """, (sender_mobile, amount, date, amount, date))
        
        # Update statistics for receiver
        cursor.execute("""
            INSERT INTO user_transaction_stats 
            (user_mobile, total_received_count, total_received_amount, last_transaction_date, last_updated)
            VALUES (?, 1, ?, ?, datetime('now'))
            ON CONFLICT(user_mobile) DO UPDATE SET
            total_received_count = total_received_count + 1,
            total_received_amount = total_received_amount + ?,
            last_transaction_date = ?,
            last_updated = datetime('now')
        """, (receiver_mobile, amount, date, amount, date))
        
        conn.commit()
        conn.close()
        return True
    
    def update_transaction_status(self, transaction_id, new_status):
        """Update the status of a transaction in the user history."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Update status in user_transaction_history
        cursor.execute("""
            UPDATE user_transaction_history
            SET status = ?
            WHERE transaction_id = ?
        """, (new_status, transaction_id))
        
        conn.commit()
        conn.close()
        return True
    
    def get_user_history(self, user_mobile, limit=50, offset=0):
        """Get transaction history for a specific user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT h.id, h.transaction_id, h.transaction_type, h.transaction_date, 
                   h.amount, h.currency, h.status,
                   t.sender, t.receiver, t.sender_governorate, t.receiver_governorate,
                   t.sender_location, t.receiver_location, t.message
            FROM user_transaction_history h
            JOIN transactions t ON h.transaction_id = t.id
            WHERE h.user_mobile = ?
            ORDER BY h.transaction_date DESC
            LIMIT ? OFFSET ?
        """, (user_mobile, limit, offset))
        
        columns = [column[0] for column in cursor.description]
        transactions = []
        for row in cursor.fetchall():
            transaction = dict(zip(columns, row))
            transactions.append(transaction)
        
        conn.close()
        return transactions
    
    def get_user_stats(self, user_mobile):
        """Get transaction statistics for a specific user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT total_sent_count, total_sent_amount, total_received_count, 
                   total_received_amount, last_transaction_date, last_updated
            FROM user_transaction_stats
            WHERE user_mobile = ?
        """, (user_mobile,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return {
                "total_sent_count": 0,
                "total_sent_amount": 0,
                "total_received_count": 0,
                "total_received_amount": 0,
                "last_transaction_date": None,
                "last_updated": None
            }
        
        return {
            "total_sent_count": result[0],
            "total_sent_amount": result[1],
            "total_received_count": result[2],
            "total_received_amount": result[3],
            "last_transaction_date": result[4],
            "last_updated": result[5]
        }
    
    def export_user_history(self, user_mobile, format="json"):
        """Export user transaction history to a file."""
        transactions = self.get_user_history(user_mobile, limit=1000)
        stats = self.get_user_stats(user_mobile)
        
        os.makedirs("exports", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"exports/user_history_{user_mobile}_{timestamp}.{format}"
        
        data = {
            "user_mobile": user_mobile,
            "export_date": datetime.now().isoformat(),
            "statistics": stats,
            "transactions": transactions
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            if format == "json":
                json.dump(data, f, ensure_ascii=False, indent=4)
            else:
                # Default to text format
                f.write(f"Transaction History for {user_mobile}\n")
                f.write(f"Export Date: {data['export_date']}\n\n")
                f.write("Statistics:\n")
                f.write(f"Total Sent: {stats['total_sent_count']} transactions, {stats['total_sent_amount']} amount\n")
                f.write(f"Total Received: {stats['total_received_count']} transactions, {stats['total_received_amount']} amount\n")
                f.write(f"Last Transaction: {stats['last_transaction_date']}\n\n")
                f.write("Transactions:\n")
                for t in transactions:
                    f.write(f"ID: {t['transaction_id']}, Type: {t['transaction_type']}, Date: {t['transaction_date']}\n")
                    f.write(f"Amount: {t['amount']} {t['currency']}, Status: {t['status']}\n")
                    if t['transaction_type'] == 'sender':
                        f.write(f"To: {t['receiver']} ({t['receiver_governorate']}, {t['receiver_location']})\n")
                    else:
                        f.write(f"From: {t['sender']} ({t['sender_governorate']}, {t['sender_location']})\n")
                    f.write(f"Message: {t['message']}\n\n")
        
        return filename
    
    def process_pending_transactions(self):
        """Process all transactions that haven't been recorded in user history yet."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all transaction IDs
        cursor.execute("SELECT id FROM transactions")
        all_transactions = [row[0] for row in cursor.fetchall()]
        
        # Get transaction IDs already in history
        cursor.execute("SELECT DISTINCT transaction_id FROM user_transaction_history")
        recorded_transactions = [row[0] for row in cursor.fetchall()]
        
        # Find transactions not yet recorded
        pending_transactions = set(all_transactions) - set(recorded_transactions)
        
        conn.close()
        
        # Record each pending transaction
        for transaction_id in pending_transactions:
            self.record_transaction(transaction_id)
        
        return len(pending_transactions)

# Hook function to be called after transaction status updates
def update_history_after_status_change(transaction_id, new_status):
    """Update user transaction history after a status change."""
    history = UserTransactionHistory()
    history.update_transaction_status(transaction_id, new_status)
    return True

# Hook function to be called after new transactions
def record_new_transaction(transaction_id):
    """Record a new transaction in user history."""
    history = UserTransactionHistory()
    history.record_transaction(transaction_id)
    return True
