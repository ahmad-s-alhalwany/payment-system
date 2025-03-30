from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, Session, joinedload
from models import User, Branch, Base
from pydantic import BaseModel
import uuid
from datetime import datetime, timedelta
from security import hash_password, verify_password, create_jwt_token, decode_jwt_token, SECRET_KEY, ALGORITHM
from generate_receipt import create_receipt
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from typing import Optional, List
from fastapi.middleware.cors import CORSMiddleware
import sqlalchemy.exc
import sqlite3

# Initialize FastAPI
app = FastAPI(title="Payment System API", version="2.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./transactions.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# Security Setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# Pydantic Models
class TransactionCreate(BaseModel):
    sender: str
    sender_mobile: str
    sender_governorate: str
    sender_location: str
    receiver: str
    receiver_mobile: str
    receiver_governorate: str
    receiver_location: str
    amount: float
    currency: str = "ليرة سورية"
    message: str
    employee_name: str
    branch_governorate: str

class TransactionStatusUpdate(BaseModel):
    transaction_id: str
    status: str

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "employee"
    branch_id: Optional[int] = None

class BranchCreate(BaseModel):
    branch_code: str  # Changed from branch_id to match model
    name: str
    location: str
    governorate: str

# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Authentication Middleware
async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = decode_jwt_token(token)
        return {
            "username": payload.username,
            "role": payload.role,
            "branch_id": payload.branch_id,
            "user_id": payload.user_id
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

# Core Endpoints
@app.post("/transactions/", status_code=201)
async def create_transaction(
    transaction: TransactionCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new money transfer transaction"""
    try:
        transaction_id = str(uuid.uuid4())
        transaction_date = datetime.now()

        # Save transaction using SQLAlchemy ORM
        db.execute("""
            INSERT INTO transactions 
            (id, sender, sender_mobile, sender_governorate, sender_location, 
             receiver, receiver_mobile, receiver_governorate, receiver_location, 
             amount, currency, message, branch_id, employee_id, employee_name, 
             branch_governorate, status, date)
            VALUES 
            (:id, :sender, :sender_mobile, :sender_governorate, :sender_location,
             :receiver, :receiver_mobile, :receiver_governorate, :receiver_location,
             :amount, :currency, :message, :branch_id, :employee_id, :employee_name,
             :branch_governorate, :status, :date)
        """, {
            "id": transaction_id,
            **transaction.dict(),
            "branch_id": current_user["branch_id"],
            "employee_id": current_user["user_id"],
            "status": "processing",
            "date": transaction_date
        })

        # Create notification
        notification_msg = f"Hello {transaction.receiver}, transfer of {transaction.amount} {transaction.currency} is pending"
        db.execute(
            "INSERT INTO notifications (transaction_id, recipient_phone, message, status) "
            "VALUES (:tid, :phone, :msg, :status)",
            {"tid": transaction_id, "phone": transaction.receiver_mobile, 
             "msg": notification_msg, "status": "pending"}
        )

        db.commit()

        # Generate receipt
        receipt_path = create_receipt(
            transaction_id=transaction_id,
            **transaction.dict(exclude={"message", "employee_name", "branch_governorate"}),
            employee_name=current_user["username"],
            branch_governorate=transaction.branch_governorate
        )

        return {
            "status": "success",
            "transaction_id": transaction_id,
            "receipt_url": receipt_path
        }

    except sqlalchemy.exc.SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/login/")
async def login(
    form_data: OAuth2PasswordBearer = Depends(),
    db: Session = Depends(get_db)
):
    """Authenticate user and return JWT token"""
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = create_jwt_token({
        "sub": user.username,
        "role": user.role,
        "branch_id": user.branch_id,
        "uid": user.id
    })
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_info": {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "branch_id": user.branch_id
        }
    }

# User Management Endpoints
@app.post("/users/", status_code=201)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create new system user"""
    # Authorization check
    if current_user["role"] not in ["director", "branch_manager"]:
        raise HTTPException(status_code=403, detail="Insufficient privileges")
    
    # Branch manager restrictions
    if current_user["role"] == "branch_manager":
        if user.role != "employee" or user.branch_id != current_user["branch_id"]:
            raise HTTPException(
                status_code=403,
                detail="Branch managers can only create employees in their branch"
            )
    
    # Validate username uniqueness
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Create user
    try:
        new_user = User(
            username=user.username,
            password=hash_password(user.password),
            role=user.role,
            branch_id=user.branch_id
        )
        db.add(new_user)
        db.commit()
        return {
            "id": new_user.id,
            "username": new_user.username,
            "role": new_user.role,
            "branch_id": new_user.branch_id
        }
    except sqlalchemy.exc.IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Invalid branch reference")

# Transaction Endpoints
@app.get("/transactions/")
async def get_transactions(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    branch_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    limit: int = 100
):
    """Retrieve transactions with filters"""
    query = db.query(Transaction).options(joinedload(Transaction.branch))
    
    # Apply filters
    if current_user["role"] == "branch_manager":
        query = query.filter(Transaction.branch_id == current_user["branch_id"])
    elif branch_id:
        query = query.filter(Transaction.branch_id == branch_id)
    
    if status_filter:
        query = query.filter(Transaction.status == status_filter)
    
    transactions = query.order_by(Transaction.date.desc()).limit(limit).all()
    
    return [{
        "id": t.id,
        "amount": t.amount,
        "currency": t.currency,
        "status": t.status,
        "date": t.date.isoformat(),
        "branch": t.branch.name if t.branch else None
    } for t in transactions]

# Security Endpoints
@app.post("/change-password/")
async def change_password(
    data: hash_password,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update user password"""
    user = db.query(User).get(current_user["user_id"])
    
    if not verify_password(data.old_password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect current password")
    
    user.password = hash_password(data.new_password)
    db.commit()
    return {"status": "success"}

# Administrative Endpoints
@app.post("/branches/", status_code=201)
async def create_branch(
    branch: BranchCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create new branch (Director only)"""
    if current_user["role"] != "director":
        raise HTTPException(status_code=403, detail="Director privileges required")
    
    try:
        new_branch = Branch(
            branch_code=branch.branch_code,
            name=branch.name,
            location=branch.location,
            governorate=branch.governorate
        )
        db.add(new_branch)
        db.commit()
        return {
            "id": new_branch.id,
            "branch_code": new_branch.branch_code,
            "name": new_branch.name
        }
    except sqlalchemy.exc.IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Branch code or name already exists"
        )

# Error Handling
@app.exception_handler(sqlalchemy.exc.SQLAlchemyError)
async def handle_db_errors(_, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Database error: {str(exc)}"}
    )

@app.exception_handler(JWTError)
async def handle_jwt_errors(_, exc):
    return JSONResponse(
        status_code=401,
        content={"detail": "Invalid authentication credentials"}
    )