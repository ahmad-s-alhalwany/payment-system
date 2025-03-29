from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import User, Branch, Base
from pydantic import BaseModel
import uuid
from datetime import datetime, timedelta
from security import hash_password, verify_password, create_jwt_token, SECRET_KEY, ALGORITHM
import sqlite3
from generate_receipt import create_receipt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from typing import Optional, List
from fastapi.middleware.cors import CORSMiddleware
import sqlalchemy.exc

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

SQLALCHEMY_DATABASE_URL = "sqlite:///./transactions.db"  # Use the same database file for both SQLAlchemy and direct SQLite
# SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})  # SQLite specific option
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the database tables if they don't exist
Base.metadata.create_all(bind=engine)

# Database setup
def init_db():
    conn = sqlite3.connect("transactions.db")
    cursor = conn.cursor()
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
            branch_id INTEGER,
            employee_id INTEGER,
            employee_name TEXT,
            branch_governorate TEXT,
            status TEXT DEFAULT 'processing',
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE SET NULL,
            FOREIGN KEY (employee_id) REFERENCES users(id) ON DELETE SET NULL
        )
    """)
    
    # Create notifications table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT,
            recipient_phone TEXT,
            message TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE
        )
    """)
    
    conn.commit()
    conn.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

init_db()

# Data models
class Transaction(BaseModel):
    sender: str
    sender_mobile: str
    sender_governorate: str
    sender_location: str
    receiver: str
    receiver_mobile: str
    receiver_governorate: str
    receiver_location: str
    amount: float
    currency: str = "ليرة سورية"  # Default to Syrian Pound
    message: str
    employee_name: str
    branch_governorate: str

class TransactionStatus(BaseModel):
    transaction_id: str
    status: str

class LoginRequest(BaseModel):
    username: str
    password: str

class PasswordReset(BaseModel):
    username: str
    new_password: str

class ChangePassword(BaseModel):
    old_password: str
    new_password: str

def save_to_db(transaction, branch_id=None, employee_id=None):
    transaction_id = str(uuid.uuid4())
    transaction_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect("transactions.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transactions (id, sender, sender_mobile, sender_governorate, sender_location, 
                                 receiver, receiver_mobile, receiver_governorate, receiver_location, 
                                 amount, currency, message, branch_id, employee_id, employee_name, 
                                 branch_governorate, status, date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (transaction_id, transaction.sender, transaction.sender_mobile, transaction.sender_governorate, 
          transaction.sender_location, transaction.receiver, transaction.receiver_mobile, transaction.receiver_governorate,
          transaction.receiver_location, transaction.amount, transaction.currency, transaction.message, 
          branch_id, employee_id, transaction.employee_name, transaction.branch_governorate, 
          "processing", transaction_date))

    # Create notification for the receiver
    notification_message = f"Hello {transaction.receiver}, you have a new money transfer of {transaction.amount} {transaction.currency} waiting for you. Please visit your nearest branch to collect it."
    cursor.execute("""
        INSERT INTO notifications (transaction_id, recipient_phone, message, status)
        VALUES (?, ?, ?, ?)
    """, (transaction_id, transaction.receiver_mobile, notification_message, "pending"))

    conn.commit()
    conn.close()
    return transaction_id

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "employee"
    branch_id: Optional[int] = None
    
class BranchCreate(BaseModel):
    branch_id: str
    name: str
    location: str
    governorate: str    
    
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        role: str = payload.get("role")
        branch_id: int = payload.get("branch_id")
        user_id: int = payload.get("user_id")
        
        if username is None or role is None:
            raise credentials_exception
            
        return {"username": username, "role": role, "branch_id": branch_id, "user_id": user_id}
    except JWTError:
        raise credentials_exception

@app.post("/send-money/")
async def send_money(transaction: Transaction, current_user: dict = Depends(get_current_user)):
    # Use the branch_id and user ID from the authenticated user
    branch_id = current_user.get("branch_id")
    employee_id = current_user.get("user_id")
    
    transaction_id = save_to_db(transaction, branch_id, employee_id)
    receipt_file = create_receipt(transaction_id, transaction.sender, transaction.sender_governorate, transaction.sender_location,
                                  transaction.receiver, transaction.receiver_governorate, transaction.receiver_location,
                                  transaction.amount, transaction.currency, transaction.employee_name, transaction.branch_governorate)
    return {"status": "success", "message": "Transaction saved!", "receipt": receipt_file, "transaction_id": transaction_id}

@app.post("/transactions/", status_code=201)
async def create_transaction(transaction: Transaction, current_user: dict = Depends(get_current_user)):
    # Use the branch_id and user ID from the authenticated user
    branch_id = current_user.get("branch_id")
    employee_id = current_user.get("user_id")
    
    transaction_id = save_to_db(transaction, branch_id, employee_id)
    receipt_file = create_receipt(transaction_id, transaction.sender, transaction.sender_governorate, transaction.sender_location,
                                  transaction.receiver, transaction.receiver_governorate, transaction.receiver_location,
                                  transaction.amount, transaction.currency, transaction.employee_name, transaction.branch_governorate)
    return {"status": "success", "message": "Transaction saved!", "receipt": receipt_file, "transaction_id": transaction_id}

@app.post("/login/")
async def login(user: LoginRequest, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first() 
    if db_user and verify_password(user.password, db_user.password):
        # Create token with expiration time (24 hours)
        access_token_expires = timedelta(hours=24)
        expires = datetime.utcnow() + access_token_expires
        
        # Include user role and branch_id in the token
        token_data = {
            "username": db_user.username,
            "role": db_user.role,
            "branch_id": db_user.branch_id,
            "user_id": db_user.id,
            "exp": expires
        }
        
        access_token = create_jwt_token(token_data)
        return {
            "access_token": access_token, 
            "token_type": "bearer", 
            "role": db_user.role, 
            "username": db_user.username,
            "branch_id": db_user.branch_id,
            "user_id": db_user.id,
            "token": access_token  # Adding token directly for frontend compatibility
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.post("/register/")
def register_user(user: UserCreate, token: str = Depends(oauth2_scheme)):
    try:
        # Try to decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("username")
        role = payload.get("role")
        branch_id = payload.get("branch_id")
        user_id = payload.get("user_id")
        
        # Check if user has permission to create users
        if role not in ["director", "branch_manager"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
        
        # Branch managers can only create employees for their own branch
        if role == "branch_manager" and (user.role != "employee" or user.branch_id != branch_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Branch managers can only create employees for their own branch")
        
        db = SessionLocal()
        try:
            # Check if username already exists
            existing_user = db.query(User).filter(User.username == user.username).first()
            if existing_user:
                raise HTTPException(status_code=400, detail="Username already registered")
            
            # Check if branch exists if branch_id is provided
            if user.branch_id:
                branch = db.query(Branch).filter(Branch.id == user.branch_id).first()
                if not branch:
                    raise HTTPException(status_code=404, detail="Branch not found")
            
            # Create new user
            hashed_password = hash_password(user.password)
            db_user = User(
                username=user.username,
                password=hashed_password,
                role=user.role,
                branch_id=user.branch_id,
                created_at=datetime.now()
            )
            
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            
            return {"id": db_user.id, "username": db_user.username, "role": db_user.role, "branch_id": db_user.branch_id}
        finally:
            db.close()
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.post("/users/")
def create_user(user: UserCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # Check if user has permission to create users
    if current_user["role"] not in ["director", "branch_manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    # Branch managers can only create employees for their own branch
    if current_user["role"] == "branch_manager" and (user.role != "employee" or user.branch_id != current_user["branch_id"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Branch managers can only create employees")
    
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Check if branch exists if branch_id is provided
    if user.branch_id:
        branch = db.query(Branch).filter(Branch.id == user.branch_id).first()
        if not branch:
            raise HTTPException(status_code=404, detail="Branch not found")
    
    # Create new user
    hashed_password = hash_password(user.password)
    db_user = User(
        username=user.username,
        password=hashed_password,
        role=user.role,
        branch_id=user.branch_id,
        created_at=datetime.now()
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {"id": db_user.id, "username": db_user.username, "role": db_user.role, "branch_id": db_user.branch_id}

@app.post("/branches/")
def create_branch(branch: BranchCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # Only directors can create branches
    if current_user["role"] != "director":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    try:
        # Check if branch_id already exists
        existing_branch = db.query(Branch).filter(Branch.branch_id == branch.branch_id).first()
        if existing_branch:
            raise HTTPException(status_code=400, detail="Branch ID already registered")
        
        # Create new branch
        db_branch = Branch(
            branch_id=branch.branch_id,
            name=branch.name,
            location=branch.location,
            governorate=branch.governorate,
            created_at=datetime.now()
        )
        
        db.add(db_branch)
        db.commit()
        db.refresh(db_branch)
        
        return {"id": db_branch.id, "branch_id": db_branch.branch_id, "name": db_branch.name, "location": db_branch.location, "governorate": db_branch.governorate}
    
    except sqlalchemy.exc.IntegrityError as e:
        db.rollback()
        # Handle specific integrity errors with user-friendly messages
        if "UNIQUE constraint failed: branches.name" in str(e):
            raise HTTPException(status_code=400, detail="A branch with this name already exists. Please use a different name.")
        elif "UNIQUE constraint failed: branches.branch_id" in str(e):
            raise HTTPException(status_code=400, detail="A branch with this ID already exists. Please use a different branch ID.")
        else:
            # For other integrity errors
            raise HTTPException(status_code=400, detail=f"Database integrity error: {str(e)}")

@app.get("/branches/")
def get_branches(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    # Modified to accept token directly without requiring current_user
    # This allows the endpoint to be called without full authentication
    try:
        # Try to decode the token, but don't fail if it's invalid
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except:
        # If token is invalid, just proceed without authentication
        pass
    
    branches = db.query(Branch).all()
    
    branch_list = []
    for branch in branches:
        branch_list.append({
            "id": branch.id,
            "branch_id": branch.branch_id,
            "name": branch.name,
            "location": branch.location,
            "governorate": branch.governorate,
            "created_at": branch.created_at.strftime("%Y-%m-%d %H:%M:%S") if branch.created_at else None
        })
    
    return {"branches": branch_list}

@app.get("/branches/{branch_id}")
def get_branch(branch_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    branch = db.query(Branch).filter(Branch.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    
    return {
        "id": branch.id,
        "branch_id": branch.branch_id,
        "name": branch.name,
        "location": branch.location,
        "governorate": branch.governorate,
        "created_at": branch.created_at.strftime("%Y-%m-%d %H:%M:%S") if branch.created_at else None
    }

@app.get("/users/")
def get_users(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # Only directors and branch managers can view users
    if current_user["role"] not in ["director", "branch_manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    query = db.query(User)
    
    # Branch managers can only see users in their branch
    if current_user["role"] == "branch_manager":
        query = query.filter(User.branch_id == current_user["branch_id"])
    
    users = query.all()
    
    # Get branch names for each user
    user_list = []
    for user in users:
        branch_name = None
        if user.branch_id:
            branch = db.query(Branch).filter(Branch.id == user.branch_id).first()
            if branch:
                branch_name = branch.name
        
        user_list.append({
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "branch_id": user.branch_id,
            "branch_name": branch_name,
            "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else None
        })
    
    return {"users": user_list}

@app.get("/employees/")
def get_employees(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user), branch_id: Optional[int] = None):
    # Only directors and branch managers can view employees
    if current_user["role"] not in ["director", "branch_manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    query = db.query(User)
    
    # Filter by role to only include employees
    query = query.filter(User.role == "employee")
    
    # Filter by branch_id if provided
    if branch_id:
        # Branch managers can only view employees in their own branch
        if current_user["role"] == "branch_manager" and current_user["branch_id"] != branch_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only view employees in your branch")
        query = query.filter(User.branch_id == branch_id)
    # If no branch_id provided but user is branch manager, only show their branch
    elif current_user["role"] == "branch_manager":
        query = query.filter(User.branch_id == current_user["branch_id"])
    
    employees = query.all()
    
    # Get branch names for each employee
    employee_list = []
    for employee in employees:
        branch_name = None
        if employee.branch_id:
            branch = db.query(Branch).filter(Branch.id == employee.branch_id).first()
            if branch:
                branch_name = branch.name
        
        employee_list.append({
            "id": employee.id,
            "username": employee.username,
            "role": employee.role,
            "branch_id": employee.branch_id,
            "branch_name": branch_name,
            "created_at": employee.created_at.strftime("%Y-%m-%d %H:%M:%S") if employee.created_at else None
        })
    
    return employee_list

@app.get("/branches/{branch_id}/employees/")
def get_branch_employees(branch_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # Check if user has permission to view branch employees
    if current_user["role"] not in ["director", "branch_manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    # Branch managers can only view employees in their own branch
    if current_user["role"] == "branch_manager" and current_user["branch_id"] != branch_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only view employees in your branch")
    
    # Check if branch exists
    branch = db.query(Branch).filter(Branch.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    
    # Get employees for the branch
    employees = db.query(User).filter(User.branch_id == branch_id).all()
    
    employee_list = []
    for employee in employees:
        employee_list.append({
            "id": employee.id,
            "username": employee.username,
            "role": employee.role,
            "branch_id": employee.branch_id,
            "created_at": employee.created_at.strftime("%Y-%m-%d %H:%M:%S") if employee.created_at else None
        })
    
    return employee_list

@app.get("/transactions/")
def get_transactions(
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user),
    branch_id: Optional[int] = None,
    filter_type: Optional[str] = None,
    limit: Optional[int] = None
):
    conn = sqlite3.connect("transactions.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Base query
    query = "SELECT * FROM transactions"
    params = []
    
    # Apply filters
    where_clauses = []
    
    # Filter by branch_id
    if branch_id:
        where_clauses.append("branch_id = ?")
        params.append(branch_id)
    
    # Branch managers can only see transactions from their branch
    if current_user["role"] == "branch_manager":
        where_clauses.append("branch_id = ?")
        params.append(current_user["branch_id"])
    
    # Apply filter_type
    if filter_type:
        if filter_type == "incoming":
            # Transactions where this branch is the receiver's branch
            where_clauses.append("receiver_governorate = (SELECT governorate FROM branches WHERE id = ?)")
            params.append(branch_id if branch_id else current_user["branch_id"])
        elif filter_type == "outgoing":
            # Transactions where this branch is the sender's branch
            where_clauses.append("sender_governorate = (SELECT governorate FROM branches WHERE id = ?)")
            params.append(branch_id if branch_id else current_user["branch_id"])
        elif filter_type == "branch_related":
            # Transactions related to this branch (either sender or receiver)
            where_clauses.append("(sender_governorate = (SELECT governorate FROM branches WHERE id = ?) OR receiver_governorate = (SELECT governorate FROM branches WHERE id = ?))")
            params.append(branch_id if branch_id else current_user["branch_id"])
            params.append(branch_id if branch_id else current_user["branch_id"])
    
    # Combine where clauses
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
    
    # Order by date (newest first)
    query += " ORDER BY date DESC"
    
    # Apply limit
    if limit:
        query += " LIMIT ?"
        params.append(limit)
    
    cursor.execute(query, params)
    transactions = cursor.fetchall()
    
    transaction_list = []
    for transaction in transactions:
        transaction_dict = dict(transaction)
        transaction_list.append(transaction_dict)
    
    conn.close()
    
    return {"transactions": transaction_list}

@app.post("/update-transaction-status/")
def update_transaction_status(status_update: TransactionStatus, current_user: dict = Depends(get_current_user)):
    # Only directors and branch managers can update transaction status
    if current_user["role"] not in ["director", "branch_manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    conn = sqlite3.connect("transactions.db")
    cursor = conn.cursor()
    
    # Check if transaction exists
    cursor.execute("SELECT * FROM transactions WHERE id = ?", (status_update.transaction_id,))
    transaction = cursor.fetchone()
    
    if not transaction:
        conn.close()
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Branch managers can only update transactions in their branch
    if current_user["role"] == "branch_manager":
        branch_id = transaction[12]  # branch_id is at index 12
        if branch_id != current_user["branch_id"]:
            conn.close()
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only update transactions in your branch")
    
    # Update transaction status
    cursor.execute(
        "UPDATE transactions SET status = ? WHERE id = ?",
        (status_update.status, status_update.transaction_id)
    )
    
    conn.commit()
    conn.close()
    
    return {"status": "success", "message": "Transaction status updated"}

@app.post("/reset-password/")
def reset_password(reset_data: PasswordReset, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # Only directors and branch managers can reset passwords
    if current_user["role"] not in ["director", "branch_manager"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Find the user
    user = db.query(User).filter(User.username == reset_data.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Branch managers can only reset passwords for employees in their branch
    if current_user["role"] == "branch_manager" and (user.role != "employee" or user.branch_id != current_user["branch_id"]):
        raise HTTPException(status_code=403, detail="You can only reset passwords for employees in your branch")
    
    # Update password
    user.password = hash_password(reset_data.new_password)
    db.commit()
    
    return {"status": "success", "message": "Password reset successfully"}

@app.post("/change-password/")
def change_password(password_data: ChangePassword, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # Find the user
    user = db.query(User).filter(User.username == current_user["username"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify old password
    if not verify_password(password_data.old_password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect old password")
    
    # Update password
    user.password = hash_password(password_data.new_password)
    db.commit()
    
    return {"status": "success", "message": "Password changed successfully"}

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # Only directors and branch managers can delete users
    if current_user["role"] not in ["director", "branch_manager"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Find the user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Directors can't be deleted
    if user.role == "director":
        raise HTTPException(status_code=403, detail="Directors cannot be deleted")
    
    # Branch managers can only delete employees in their branch
    if current_user["role"] == "branch_manager" and (user.role != "employee" or user.branch_id != current_user["branch_id"]):
        raise HTTPException(status_code=403, detail="You can only delete employees in your branch")
    
    # Delete the user
    db.delete(user)
    db.commit()
    
    return {"status": "success", "message": "User deleted successfully"}

@app.delete("/branches/{branch_id}/")
def delete_branch(branch_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # Only directors can delete branches
    if current_user["role"] != "director":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Find the branch
    branch = db.query(Branch).filter(Branch.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    
    # Check if there are users assigned to this branch
    users = db.query(User).filter(User.branch_id == branch_id).all()
    if users:
        raise HTTPException(status_code=400, detail="Cannot delete branch with assigned users")
    
    # Delete the branch
    db.delete(branch)
    db.commit()
    
    return {"status": "success", "message": "Branch deleted successfully"}

@app.get("/branches/stats/")
def get_branch_stats(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # Get total number of branches
    total_branches = db.query(Branch).count()
    
    # Get active branches (all branches are considered active for now)
    active_branches = total_branches
    
    return {
        "total": total_branches,
        "active": active_branches
    }

@app.get("/users/stats/")
def get_user_stats(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # Get total number of users
    total_users = db.query(User).count()
    
    # Get number of employees
    employees = db.query(User).filter(User.role == "employee").count()
    
    return {
        "total": total_users,
        "directors": db.query(User).filter(User.role == "director").count(),
        "branch_managers": db.query(User).filter(User.role == "branch_manager").count(),
        "employees": employees
    }

@app.get("/branches/{branch_id}/employees/stats/")
def get_branch_employees_stats(branch_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # Check if user has permission to view branch employee stats
    if current_user["role"] not in ["director", "branch_manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    # Branch managers can only view stats for their own branch
    if current_user["role"] == "branch_manager" and current_user["branch_id"] != branch_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only view stats for your branch")
    
    # Check if branch exists
    branch = db.query(Branch).filter(Branch.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    
    # Get total number of employees in the branch
    total_employees = db.query(User).filter(User.branch_id == branch_id).count()
    
    return {
        "total": total_employees,
        "active": total_employees  # For now, all employees are considered active
    }

@app.get("/branches/{branch_id}/transactions/stats/")
def get_branch_transactions_stats(branch_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # Check if user has permission to view branch transaction stats
    if current_user["role"] not in ["director", "branch_manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    # Branch managers can only view stats for their own branch
    if current_user["role"] == "branch_manager" and current_user["branch_id"] != branch_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only view stats for your branch")
    
    # Check if branch exists
    branch = db.query(Branch).filter(Branch.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    
    conn = sqlite3.connect("transactions.db")
    cursor = conn.cursor()
    
    # Get total number of transactions for the branch
    cursor.execute("SELECT COUNT(*) FROM transactions WHERE branch_id = ?", (branch_id,))
    total_transactions = cursor.fetchone()[0]
    
    # Get total amount of transactions for the branch
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE branch_id = ?", (branch_id,))
    total_amount = cursor.fetchone()[0] or 0
    
    # Get number of completed transactions
    cursor.execute("SELECT COUNT(*) FROM transactions WHERE branch_id = ? AND status = 'completed'", (branch_id,))
    completed_transactions = cursor.fetchone()[0]
    
    # Get number of pending transactions
    cursor.execute("SELECT COUNT(*) FROM transactions WHERE branch_id = ? AND status = 'processing'", (branch_id,))
    pending_transactions = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "total": total_transactions,
        "total_amount": total_amount,
        "completed": completed_transactions,
        "pending": pending_transactions
    }

@app.get("/transactions/stats/")
def get_transactions_stats(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    conn = sqlite3.connect("transactions.db")
    cursor = conn.cursor()
    
    # Base query
    query = "SELECT COUNT(*), SUM(amount) FROM transactions"
    params = []
    
    # Branch managers can only see transactions from their branch
    if current_user["role"] == "branch_manager":
        query += " WHERE branch_id = ?"
        params.append(current_user["branch_id"])
    
    cursor.execute(query, params)
    result = cursor.fetchone()
    total_transactions = result[0] or 0
    total_amount = result[1] or 0
    
    # Get number of completed transactions
    completed_query = "SELECT COUNT(*) FROM transactions"
    completed_params = []
    
    if current_user["role"] == "branch_manager":
        completed_query += " WHERE branch_id = ? AND status = 'completed'"
        completed_params.append(current_user["branch_id"])
    else:
        completed_query += " WHERE status = 'completed'"
    
    cursor.execute(completed_query, completed_params)
    result = cursor.fetchone()
    completed_transactions = result[0] or 0
    
    # Get number of pending transactions
    pending_query = "SELECT COUNT(*) FROM transactions"
    pending_params = []
    
    if current_user["role"] == "branch_manager":
        pending_query += " WHERE branch_id = ? AND status = 'processing'"
        pending_params.append(current_user["branch_id"])
    else:
        pending_query += " WHERE status = 'processing'"
    
    cursor.execute(pending_query, pending_params)
    result = cursor.fetchone()
    pending_transactions = result[0] or 0
    
    conn.close()
    
    return {
        "total": total_transactions,
        "total_amount": total_amount,
        "completed": completed_transactions,
        "pending": pending_transactions
    }

@app.get("/transactions/{transaction_id}/")
def get_transaction(transaction_id: str, current_user: dict = Depends(get_current_user)):
    conn = sqlite3.connect("transactions.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get transaction
    cursor.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,))
    transaction = cursor.fetchone()
    
    if not transaction:
        conn.close()
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Branch managers can only view transactions from their branch
    if current_user["role"] == "branch_manager" and transaction["branch_id"] != current_user["branch_id"]:
        conn.close()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only view transactions from your branch")
    
    transaction_dict = dict(transaction)
    
    conn.close()
    
    return transaction_dict

@app.get("/transactions/{transaction_id}/receipt/")
def get_transaction_receipt(transaction_id: str, current_user: dict = Depends(get_current_user)):
    conn = sqlite3.connect("transactions.db")
    cursor = conn.cursor()
    
    # Check if transaction exists
    cursor.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,))
    transaction = cursor.fetchone()
    
    if not transaction:
        conn.close()
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Branch managers can only view receipts for transactions from their branch
    if current_user["role"] == "branch_manager" and transaction[12] != current_user["branch_id"]:  # branch_id is at index 12
        conn.close()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only view receipts for transactions from your branch")
    
    conn.close()
    
    # Generate receipt
    receipt_file = create_receipt(transaction_id, transaction[1], transaction[3], transaction[4],
                                 transaction[5], transaction[7], transaction[8],
                                 transaction[9], transaction[10], transaction[14], transaction[15])
    
    return {"receipt_url": receipt_file}

@app.get("/reports/{report_type}/")
def get_report(
    report_type: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    branch_id: Optional[int] = None
):
    # Only directors and branch managers can view reports
    if current_user["role"] not in ["director", "branch_manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    # Branch managers can only view reports for their branch
    if current_user["role"] == "branch_manager":
        if branch_id and branch_id != current_user["branch_id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only view reports for your branch")
        branch_id = current_user["branch_id"]
    
    # Generate report based on type
    if report_type == "transactions":
        return generate_transactions_report(db, branch_id, date_from, date_to)
    elif report_type == "branches":
        return generate_branches_report(db)
    elif report_type == "employees":
        return generate_employees_report(db, branch_id)
    else:
        raise HTTPException(status_code=400, detail="Invalid report type")

def generate_transactions_report(db: Session, branch_id=None, date_from=None, date_to=None):
    conn = sqlite3.connect("transactions.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Base query
    query = "SELECT * FROM transactions"
    params = []
    
    # Apply filters
    where_clauses = []
    
    # Filter by branch_id
    if branch_id:
        where_clauses.append("branch_id = ?")
        params.append(branch_id)
    
    # Filter by date range
    if date_from:
        where_clauses.append("date >= ?")
        params.append(date_from)
    
    if date_to:
        where_clauses.append("date <= ?")
        params.append(date_to)
    
    # Combine where clauses
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
    
    # Order by date (newest first)
    query += " ORDER BY date DESC"
    
    cursor.execute(query, params)
    transactions = cursor.fetchall()
    
    transaction_list = []
    for transaction in transactions:
        transaction_dict = dict(transaction)
        transaction_list.append(transaction_dict)
    
    conn.close()
    
    return {"items": transaction_list}

def generate_branches_report(db: Session):
    branches = db.query(Branch).all()
    
    branch_list = []
    for branch in branches:
        branch_list.append({
            "id": branch.id,
            "branch_id": branch.branch_id,
            "name": branch.name,
            "location": branch.location,
            "governorate": branch.governorate,
            "created_at": branch.created_at.strftime("%Y-%m-%d %H:%M:%S") if branch.created_at else None,
            "status": "active"  # All branches are considered active for now
        })
    
    return {"items": branch_list}

def generate_employees_report(db: Session, branch_id):
    query = db.query(User).filter(User.role == "employee")
    
    if branch_id:
        query = query.filter(User.branch_id == branch_id)
    
    employees = query.all()
    
    employee_list = []
    for employee in employees:
        branch_name = None
        if employee.branch_id:
            branch = db.query(Branch).filter(Branch.id == employee.branch_id).first()
            if branch:
                branch_name = branch.name
        
        employee_list.append({
            "id": employee.id,
            "username": employee.username,
            "role": employee.role,
            "branch_id": employee.branch_id,
            "branch_name": branch_name,
            "created_at": employee.created_at.strftime("%Y-%m-%d %H:%M:%S") if employee.created_at else None
        })
    
    return {"items": employee_list}
