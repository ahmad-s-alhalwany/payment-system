import sqlite3
from datetime import datetime
import json
import os
import hashlib

class UserProfile:
    def __init__(self, db_path="transactions.db"):
        """Initialize the UserProfile class with database path."""
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize the database and create necessary tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create user_profiles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mobile TEXT UNIQUE,
                name TEXT,
                governorate TEXT,
                location TEXT,
                id_number TEXT,
                id_type TEXT,
                email TEXT,
                preferred_currency TEXT DEFAULT 'IQD',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create user_verification table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_verification (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_profile_id INTEGER,
                verification_type TEXT,
                verification_status TEXT DEFAULT 'pending',
                verification_date TIMESTAMP,
                verified_by INTEGER,
                notes TEXT,
                FOREIGN KEY (user_profile_id) REFERENCES user_profiles(id) ON DELETE CASCADE,
                FOREIGN KEY (verified_by) REFERENCES users(id) ON DELETE SET NULL
            )
        """)
        
        # Create user_documents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_profile_id INTEGER,
                document_type TEXT,
                document_path TEXT,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                uploaded_by INTEGER,
                FOREIGN KEY (user_profile_id) REFERENCES user_profiles(id) ON DELETE CASCADE,
                FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE SET NULL
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_or_update_profile(self, mobile, name=None, governorate=None, location=None, 
                                id_number=None, id_type=None, email=None, preferred_currency=None):
        """Create a new user profile or update an existing one."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if profile exists
        cursor.execute("SELECT id FROM user_profiles WHERE mobile = ?", (mobile,))
        result = cursor.fetchone()
        
        if result:
            # Update existing profile
            profile_id = result[0]
            update_fields = []
            params = []
            
            if name is not None:
                update_fields.append("name = ?")
                params.append(name)
            if governorate is not None:
                update_fields.append("governorate = ?")
                params.append(governorate)
            if location is not None:
                update_fields.append("location = ?")
                params.append(location)
            if id_number is not None:
                update_fields.append("id_number = ?")
                params.append(id_number)
            if id_type is not None:
                update_fields.append("id_type = ?")
                params.append(id_type)
            if email is not None:
                update_fields.append("email = ?")
                params.append(email)
            if preferred_currency is not None:
                update_fields.append("preferred_currency = ?")
                params.append(preferred_currency)
            
            if update_fields:
                update_fields.append("updated_at = datetime('now')")
                query = f"UPDATE user_profiles SET {', '.join(update_fields)} WHERE id = ?"
                params.append(profile_id)
                cursor.execute(query, params)
        else:
            # Create new profile
            cursor.execute("""
                INSERT INTO user_profiles 
                (mobile, name, governorate, location, id_number, id_type, email, preferred_currency)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (mobile, name, governorate, location, id_number, id_type, email, 
                  preferred_currency or 'IQD'))
            profile_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        return profile_id
    
    def get_profile(self, mobile):
        """Get user profile by mobile number."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, mobile, name, governorate, location, id_number, id_type, 
                   email, preferred_currency, created_at, updated_at
            FROM user_profiles
            WHERE mobile = ?
        """, (mobile,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
        
        return {
            "id": result[0],
            "mobile": result[1],
            "name": result[2],
            "governorate": result[3],
            "location": result[4],
            "id_number": result[5],
            "id_type": result[6],
            "email": result[7],
            "preferred_currency": result[8],
            "created_at": result[9],
            "updated_at": result[10]
        }
    
    def add_verification(self, mobile, verification_type, verification_status, verified_by, notes=None):
        """Add a verification record for a user profile."""
        profile = self.get_profile(mobile)
        if not profile:
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO user_verification
            (user_profile_id, verification_type, verification_status, verification_date, verified_by, notes)
            VALUES (?, ?, ?, datetime('now'), ?, ?)
        """, (profile["id"], verification_type, verification_status, verified_by, notes))
        
        conn.commit()
        conn.close()
        return True
    
    def add_document(self, mobile, document_type, document_path, uploaded_by):
        """Add a document for a user profile."""
        profile = self.get_profile(mobile)
        if not profile:
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO user_documents
            (user_profile_id, document_type, document_path, uploaded_by)
            VALUES (?, ?, ?, ?)
        """, (profile["id"], document_type, document_path, uploaded_by))
        
        conn.commit()
        conn.close()
        return True
    
    def get_verification_status(self, mobile):
        """Get verification status for a user profile."""
        profile = self.get_profile(mobile)
        if not profile:
            return None
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT verification_type, verification_status, verification_date, notes
            FROM user_verification
            WHERE user_profile_id = ?
            ORDER BY verification_date DESC
        """, (profile["id"],))
        
        verifications = []
        for row in cursor.fetchall():
            verifications.append({
                "verification_type": row[0],
                "verification_status": row[1],
                "verification_date": row[2],
                "notes": row[3]
            })
        
        conn.close()
        return verifications
    
    def get_documents(self, mobile):
        """Get documents for a user profile."""
        profile = self.get_profile(mobile)
        if not profile:
            return None
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT document_type, document_path, upload_date, uploaded_by
            FROM user_documents
            WHERE user_profile_id = ?
            ORDER BY upload_date DESC
        """, (profile["id"],))
        
        documents = []
        for row in cursor.fetchall():
            documents.append({
                "document_type": row[0],
                "document_path": row[1],
                "upload_date": row[2],
                "uploaded_by": row[3]
            })
        
        conn.close()
        return documents
    
    def update_from_transaction(self, transaction_id):
        """Update user profiles from transaction data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get transaction details
        cursor.execute("""
            SELECT sender, sender_mobile, sender_governorate, sender_location,
                   receiver, receiver_mobile, receiver_governorate, receiver_location
            FROM transactions
            WHERE id = ?
        """, (transaction_id,))
        
        result = cursor.fetchone()
        if not result:
            conn.close()
            return False
        
        sender, sender_mobile, sender_governorate, sender_location, receiver, receiver_mobile, receiver_governorate, receiver_location = result
        
        conn.close()
        
        # Update sender profile
        self.create_or_update_profile(
            mobile=sender_mobile,
            name=sender,
            governorate=sender_governorate,
            location=sender_location
        )
        
        # Update receiver profile
        self.create_or_update_profile(
            mobile=receiver_mobile,
            name=receiver,
            governorate=receiver_governorate,
            location=receiver_location
        )
        
        return True
    
    def search_profiles(self, search_term, search_type="all"):
        """Search for user profiles."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        search_term = f"%{search_term}%"
        
        if search_type == "mobile":
            query = "SELECT * FROM user_profiles WHERE mobile LIKE ?"
            params = (search_term,)
        elif search_type == "name":
            query = "SELECT * FROM user_profiles WHERE name LIKE ?"
            params = (search_term,)
        elif search_type == "governorate":
            query = "SELECT * FROM user_profiles WHERE governorate LIKE ?"
            params = (search_term,)
        elif search_type == "location":
            query = "SELECT * FROM user_profiles WHERE location LIKE ?"
            params = (search_term,)
        else:  # all
            query = """
                SELECT * FROM user_profiles 
                WHERE mobile LIKE ? OR name LIKE ? OR governorate LIKE ? OR location LIKE ?
            """
            params = (search_term, search_term, search_term, search_term)
        
        cursor.execute(query, params)
        
        columns = [column[0] for column in cursor.description]
        profiles = []
        for row in cursor.fetchall():
            profile = dict(zip(columns, row))
            profiles.append(profile)
        
        conn.close()
        return profiles
    
    def export_profile(self, mobile, format="json"):
        """Export user profile to a file."""
        profile = self.get_profile(mobile)
        if not profile:
            return None
        
        verifications = self.get_verification_status(mobile)
        documents = self.get_documents(mobile)
        
        os.makedirs("exports", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"exports/user_profile_{mobile}_{timestamp}.{format}"
        
        data = {
            "profile": profile,
            "verifications": verifications,
            "documents": documents,
            "export_date": datetime.now().isoformat()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            if format == "json":
                json.dump(data, f, ensure_ascii=False, indent=4)
            else:
                # Default to text format
                f.write(f"User Profile for {profile['name']} ({profile['mobile']})\n")
                f.write(f"Export Date: {data['export_date']}\n\n")
                f.write("Profile Information:\n")
                f.write(f"Name: {profile['name']}\n")
                f.write(f"Mobile: {profile['mobile']}\n")
                f.write(f"Governorate: {profile['governorate']}\n")
                f.write(f"Location: {profile['location']}\n")
                f.write(f"ID Number: {profile['id_number']}\n")
                f.write(f"ID Type: {profile['id_type']}\n")
                f.write(f"Email: {profile['email']}\n")
                f.write(f"Preferred Currency: {profile['preferred_currency']}\n")
                f.write(f"Created: {profile['created_at']}\n")
                f.write(f"Updated: {profile['updated_at']}\n\n")
                
                f.write("Verifications:\n")
                for v in verifications:
                    f.write(f"Type: {v['verification_type']}, Status: {v['verification_status']}, Date: {v['verification_date']}\n")
                    if v['notes']:
                        f.write(f"Notes: {v['notes']}\n")
                
                f.write("\nDocuments:\n")
                for d in documents:
                    f.write(f"Type: {d['document_type']}, Path: {d['document_path']}, Uploaded: {d['upload_date']}\n")
        
        return filename
    
    def process_pending_profiles(self):
        """Process all transactions to update user profiles."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all transactions
        cursor.execute("SELECT id FROM transactions")
        transactions = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        # Update profiles for each transaction
        count = 0
        for transaction_id in transactions:
            if self.update_from_transaction(transaction_id):
                count += 1
        
        return count

# Hook function to be called after new transactions
def update_profiles_after_transaction(transaction_id):
    """Update user profiles after a new transaction."""
    profile_manager = UserProfile()
    profile_manager.update_from_transaction(transaction_id)
    return True

# Function to generate a unique ID for a user based on their information
def generate_user_id(name, mobile, id_number=None):
    """Generate a unique ID for a user based on their information."""
    # Create a string with user information
    user_info = f"{name}|{mobile}"
    if id_number:
        user_info += f"|{id_number}"
    
    # Add a timestamp for uniqueness
    user_info += f"|{datetime.now().isoformat()}"
    
    # Generate a hash
    hash_object = hashlib.sha256(user_info.encode())
    user_id = hash_object.hexdigest()[:12].upper()
    
    return user_id
