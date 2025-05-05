'''Data schemas for working with SQLite based on schemas in .schemas'''

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, Boolean
from sqlalchemy.orm import relationship

from .db import Base

class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String, index=True)
    is_admin = Column(Boolean)
    password = Column(String)

class Account(Base):
    __tablename__ = 'accounts'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    account_name = Column(String)
    amount = Column(Float)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User')

class Transaction(Base):
    __tablename__ = 'transactions'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String)
    amount = Column(Float)
    date = Column(Date)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User')
    account_id = Column(Integer, ForeignKey('accounts.id'))
    account = relationship('Account')
