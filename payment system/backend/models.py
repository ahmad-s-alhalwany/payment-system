from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, CheckConstraint, func, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    """Represents system users with authentication and authorization details"""
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "role IN ('director', 'branch_manager', 'employee')", 
            name="valid_roles_check"
        ),
        Index('ix_users_created_at', 'created_at'),
    )

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(128), nullable=False)  # Suitable for hashed passwords
    role = Column(
        String(15), 
        default='employee', 
        nullable=False, 
        server_default='employee'
    )
    branch_id = Column(Integer, ForeignKey("branches.id", ondelete="SET NULL"))
    created_at = Column(DateTime, server_default=func.now())  # Database-generated timestamp

    # Relationship for ORM joins
    branch = relationship("Branch", back_populates="users")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"

class Branch(Base):
    """Represents bank branches with geographical information"""
    __tablename__ = "branches"
    __table_args__ = (
        Index('ix_branches_governorate', 'governorate'),
        Index('ix_branches_created_at', 'created_at'),
    )

    id = Column(Integer, primary_key=True, index=True)
    branch_code = Column(String(10), unique=True, index=True, nullable=False)  # Human-readable ID
    name = Column(String(100), index=True, nullable=False)
    location = Column(String(150), nullable=False)
    governorate = Column(String(50), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationship for ORM joins
    users = relationship("User", back_populates="branch")

    def __repr__(self):
        return f"<Branch(id={self.id}, code='{self.branch_code}', name='{self.name}')>"