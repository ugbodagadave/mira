from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    BigInteger,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_user_id = Column(BigInteger, unique=True, nullable=False)
    first_name = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    price_alerts = relationship("PriceAlert", back_populates="user")
    new_listing_alerts = relationship("NewListingAlert", back_populates="user")

class NewListingAlert(Base):
    __tablename__ = "new_listing_alerts"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    collection_name = Column(String, nullable=False)
    collection_address = Column(String, nullable=False)
    chain = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="new_listing_alerts")

class PriceAlert(Base):
    __tablename__ = "price_alerts"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    collection_name = Column(String, nullable=False)
    collection_address = Column(String, nullable=False)
    chain = Column(String, nullable=False)
    threshold_price = Column(Float, nullable=False)
    direction = Column(String, nullable=False)  # 'above' or 'below'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="price_alerts")
