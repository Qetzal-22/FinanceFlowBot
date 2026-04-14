from sqlalchemy import Column, Integer, String, Enum, Boolean, DateTime, ForeignKey, Float, BigInteger, UniqueConstraint
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
    telegram_id = Column(BigInteger, unique=True, index=True)

    is_active = Column(Boolean, default=True)
    create_at = Column(DateTime, default=datetime.utcnow)

    bank_accounts = relationship("BankAccount", back_populates="user", cascade="all, delete-orphan")
    categories = relationship("UserCategory", back_populates="user", cascade="all, delete-orphan")

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

    type = Column(Enum(Type_Operation, name="type_operation"))
    amount = Column(Float)
    balance_after = Column(Float)
    description = Column(String)
    category = Column(Integer)

    create_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    account = relationship("BankAccount", back_populates="operations")

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String)

    user_categories = relationship("UserCategory", back_populates="category")

class UserCategory(Base):
    __tablename__ = "user_category"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))

    user = relationship("User", back_populates="categories")
    category = relationship("Category", back_populates="user_categories")
    budgets = relationship("Budget", back_populates="user_category")


class Budget(Base):
    __tablename__ = "budgets"
    id = Column(Integer, primary_key=True)
    user_category_id = Column(Integer, ForeignKey("user_category.id"), nullable=False)

    amount = Column(Float, nullable=False)
    spend = Column(Float, nullable=False)

    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)

    create_at = Column(DateTime, default=datetime.utcnow)
    user_category = relationship("UserCategory", back_populates="budgets")

    __table_args__ = (
        UniqueConstraint(
            "user_category_id",
            "year",
            "month",
            name="uniq_budget_period"
        ),
    )