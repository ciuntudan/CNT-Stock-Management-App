from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import enum
import os

Base = declarative_base()

def get_session():
    db_path = os.path.join('database', 'stock.db')
    engine = create_engine(f'sqlite:///{db_path}')
    Session = sessionmaker(bind=engine)
    return Session()

def init_db():
    db_path = os.path.join('database', 'stock.db')
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)

class MeasureUnit(enum.Enum):
    PIECE = "Bucata"
    METER = "Metru"
    CENTIMETER = "Centimetru"
    SQUARE_METER = "Metru patrat"
    SQUARE_CENTIMETER = "Centimetru patrat"
    ROLL = "Rola"
    SHEET = "Coala"
    TOP = "Top"
    LITER = "Litru"

class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    products = relationship('Product', back_populates='category')

class Supplier(Base):
    __tablename__ = 'suppliers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    contact_person = Column(String(100))
    email = Column(String(100))
    phone = Column(String(20))
    address = Column(Text)
    products = relationship('Product', back_populates='supplier')

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    quantity = Column(Integer, default=0)
    unit_price = Column(Float, nullable=False)
    alert_threshold = Column(Integer, default=10)
    width = Column(Float)
    height = Column(Float)
    material_type = Column(String(50))
    measure_unit = Column(Enum(MeasureUnit), default=MeasureUnit.PIECE)
    
    category_id = Column(Integer, ForeignKey('categories.id'))
    category = relationship('Category', back_populates='products')
    
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))
    supplier = relationship('Supplier', back_populates='products')
    
    price_history = relationship('PriceHistory', back_populates='product')
    stock_movements = relationship('StockMovement', back_populates='product')
    edit_history = relationship('EditHistory', back_populates='product')

class PriceHistory(Base):
    __tablename__ = 'price_history'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    old_price = Column(Float, nullable=False)
    new_price = Column(Float, nullable=False)
    changed_at = Column(DateTime, default=datetime.utcnow)
    
    product = relationship('Product', back_populates='price_history')

class StockMovement(Base):
    __tablename__ = 'stock_movements'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity_changed = Column(Integer, nullable=False)
    reference_type = Column(String(20))  # 'sale', 'purchase', 'adjustment'
    reference_id = Column(Integer)  # ID of the sale/purchase order
    notes = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    product = relationship('Product', back_populates='stock_movements')

class EditHistory(Base):
    __tablename__ = 'edit_history'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    field_name = Column(String(50), nullable=False)
    old_value = Column(String(500))
    new_value = Column(String(500))
    changed_at = Column(DateTime, default=datetime.utcnow)
    
    product = relationship('Product', back_populates='edit_history')

class Customer(Base):
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100))
    phone = Column(String(20))
    address = Column(Text)
    company_name = Column(String(100))
    
    sales_orders = relationship('SalesOrder', back_populates='customer')

class SalesOrder(Base):
    __tablename__ = 'sales_orders'
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    order_date = Column(DateTime, default=datetime.utcnow)
    total_amount = Column(Float, default=0)
    notes = Column(Text)
    
    customer = relationship('Customer', back_populates='sales_orders')
    items = relationship('SalesOrderItem', back_populates='order')

class SalesOrderItem(Base):
    __tablename__ = 'sales_order_items'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('sales_orders.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    width = Column(Float)
    height = Column(Float)
    notes = Column(Text)
    
    order = relationship('SalesOrder', back_populates='items')
    product = relationship('Product')

class PurchaseOrder(Base):
    __tablename__ = 'purchase_orders'
    
    id = Column(Integer, primary_key=True)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))
    order_date = Column(DateTime, default=datetime.utcnow)
    total_amount = Column(Float, default=0)
    status = Column(String(20), default='pending')  # pending, received, cancelled
    notes = Column(Text)
    
    supplier = relationship('Supplier')
    items = relationship('PurchaseOrderItem', back_populates='order')

class PurchaseOrderItem(Base):
    __tablename__ = 'purchase_order_items'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('purchase_orders.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    notes = Column(Text)
    
    order = relationship('PurchaseOrder', back_populates='items')
    product = relationship('Product') 