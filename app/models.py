from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.sql import func  # Для использования func.now() и других функций базы данных
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime  # Для работы с датами и временем

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)  # Пароль должен быть зашифрован
    first_name = Column(String)
    last_name = Column(String)
    phone_number = Column(String)
    birth_date = Column(DateTime)
    is_working = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связь с таблицей смен и задач
    work_shifts = relationship("WorkShift", back_populates="user")
    tasks = relationship("Task", back_populates="user")

class WorkShift(Base):
    __tablename__ = "work_shifts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    shift_date = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="work_shifts")

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    task_description = Column(Text)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="tasks")

class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    icon_url = Column(String)

    # Связь с таблицей Product
    products = relationship('Product', back_populates="category")

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'))
    sold_count = Column(Integer, default=0)
    image_url = Column(String)  
    # Обратная связь с таблицей Category
    category = relationship('Category', back_populates="products")
    sales = relationship("Sale", back_populates="product")

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    username = Column(String, nullable=False)  # Логин пользователя
    quantity = Column(Integer, nullable=False)
    sale_time = Column(DateTime(timezone=True), nullable=False)

    # Связь с продуктом
    product = relationship("Product", back_populates="sales")