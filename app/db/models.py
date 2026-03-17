from sqlalchemy import Column, Integer, String, Enum, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from app.db.database import Base

class Type_Operation(enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, index=True)

    is_active = Column(Boolean, default=True)
    create_at = Column(DateTime, default=datetime.utcnow)

    bank_accounts = relationship("BankAccount", back_populates="user", cascade="all, delete-orphan")

class BankAccount(Base):
    __tablename__ = "bank_accounts"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    name = Column(String)
    balance = Column(Float, default=0.0)

    create_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="bank_accounts")
    operations = relationship("BankOperation", back_populates="account", cascade="all, delete-orphan")

class BankOperation(Base):
    __tablename__ = "bank_operations"
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("bank_accounts.id"))

    type = Column(Enum(Type_Operation))
    amount = Column(Float)
    description = Column(String)
    category = Column(String)

    create_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    account = relationship("BankAccount", back_populates="operations")