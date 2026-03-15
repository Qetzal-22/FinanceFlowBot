from collections import defaultdict

from sqlalchemy import Column, Integer, String, Enum, Boolean, DateTime, ForeignKey
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

    back_accounts = relationship("BackAccount", back_populates="user", cascade="all, delete-orphan")

class BackAccount(Base):
    __tablename__ = "back_accounts"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    name = Column(String)
    balance = Column(Integer, default=0)

    create_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_popuates="back_accounts")
    operations = relationship("BankOperations", back_popuates="back_account", cascade="all, delete-orphan")

class BackOperation(Base):
    id = Column(Integer, primary=True)
    account_id = Column(Integer, ForeignKey("back_accounts.id"))

    type = Column(Enum(Type_Operation))
    amount = Column(Integer)
    description = Column(String)
    category = Column(String)

    create_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    account = relationship("BackAccount", back_populates="operations")