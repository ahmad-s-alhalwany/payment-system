import sqlite3

def init_db():
    """Initialize the database and create necessary tables if they do not exist."""
    conn = sqlite3.connect("transactions.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS branches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            branch_id TEXT UNIQUE,  # Unique identification number for each branch
            name TEXT UNIQUE,
            location TEXT,
            governorate TEXT  # Governorate responsible for the branch
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT CHECK(role IN ('director', 'branch_manager', 'employee')),
            branch_id INTEGER,
            FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE SET NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id TEXT PRIMARY KEY,
            sender TEXT,
            sender_mobile TEXT,
            sender_governorate TEXT, 
            sender_location TEXT,
            receiver TEXT,
            receiver_mobile TEXT,
            receiver_governorate TEXT,
            receiver_location TEXT,
            amount REAL,
            currency TEXT,
            message TEXT,
            branch_id INTEGER,  # Add branch_id column
            employee_id INTEGER,
            employee_name TEXT,  # Add employee name
            branch_governorate TEXT,  # Add branch governorate
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE SET NULL,
            FOREIGN KEY (employee_id) REFERENCES users(id) ON DELETE SET NULL
        )
    """)

    conn.commit()
    conn.close()

# Initialize the database when script runs
init_db()
