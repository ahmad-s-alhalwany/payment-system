import sqlite3
from contextlib import closing

def init_db():
    """Initialize database with proper error handling and optimized schema."""
    try:
        with closing(sqlite3.connect("transactions.db")) as conn:
            cursor = conn.cursor()

            # Create branches table with standardized ID type
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS branches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    branch_code TEXT UNIQUE NOT NULL,  -- Unique human-readable ID
                    name TEXT UNIQUE NOT NULL,
                    location TEXT NOT NULL,
                    governorate TEXT NOT NULL
                )
            """)

            # Create users table with password hashing note
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,  -- Store hashed passwords
                    role TEXT NOT NULL CHECK(role IN ('director', 'branch_manager', 'employee')),
                    branch_id INTEGER REFERENCES branches(id) ON DELETE SET NULL
                )
            """)
            
            cursor.execute("""
                CREATE VIEW legacy_transactions AS
                SELECT 
                    id,
                    json_extract(sender_details, '$.name') as sender,
                    json_extract(sender_details, '$.mobile') as sender_mobile,
                    json_extract(sender_details, '$.governorate') as sender_governorate,
                    json_extract(receiver_details, '$.name') as receiver,
                    json_extract(receiver_details, '$.mobile') as receiver_mobile,
                    amount,
                    currency,
                    message,
                    branch_id,
                    employee_id,
                    transaction_date as date
                FROM transactions
            """)

            # Optimized transactions table with proper normalization
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id TEXT PRIMARY KEY,
                    sender_details TEXT NOT NULL,  -- JSON-encoded sender info
                    receiver_details TEXT NOT NULL,  -- JSON-encoded receiver info
                    amount REAL NOT NULL CHECK(amount > 0),
                    currency TEXT NOT NULL DEFAULT 'IQD',
                    message TEXT,
                    branch_id INTEGER NOT NULL REFERENCES branches(id),
                    employee_id INTEGER NOT NULL REFERENCES users(id),
                    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create performance indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_transactions_date 
                ON transactions(transaction_date)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_transactions_branch 
                ON transactions(branch_id)
            """)

            conn.commit()
            
    except sqlite3.Error as e:
        print(f"Database initialization failed: {str(e)}")
        raise

# Initialize the database
if __name__ == "__main__":
    init_db()