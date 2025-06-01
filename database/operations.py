from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum, or_, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import sqlalchemy.orm
from datetime import datetime
import enum
import os
from .models import (
    Product, Category, Supplier, PriceHistory, StockMovement,
    Customer, SalesOrder, SalesOrderItem, PurchaseOrder, PurchaseOrderItem,
    EditHistory, MeasureUnit, get_session
)

def track_edit(session, product_id, field_name, old_value, new_value):
    if old_value != new_value:
        edit = EditHistory(
            product_id=product_id,
            field_name=field_name,
            old_value=str(old_value) if old_value is not None else None,
            new_value=str(new_value) if new_value is not None else None
        )
        session.add(edit)

# Basic Product Operations
def get_all_products():
    session = get_session()
    products = session.query(Product)\
        .options(sqlalchemy.orm.joinedload(Product.category))\
        .options(sqlalchemy.orm.joinedload(Product.supplier))\
        .all()
    session.close()
    return products

def get_product_by_id(product_id):
    session = get_session()
    product = session.query(Product).filter(Product.id == product_id).first()
    session.close()
    return product

def get_product_history(product_id):
    session = get_session()
    history = session.query(EditHistory)\
        .filter(EditHistory.product_id == product_id)\
        .order_by(EditHistory.changed_at.desc())\
        .all()
    session.close()
    return history

def delete_product(product_id):
    session = get_session()
    product = session.query(Product).filter(Product.id == product_id).first()
    if product:
        session.delete(product)
        session.commit()
    session.close()

# Category operations
def add_category(name, description=None):
    session = get_session()
    category = Category(name=name, description=description)
    session.add(category)
    session.commit()
    session.close()
    return category

def get_all_categories():
    session = get_session()
    categories = session.query(Category).all()
    session.close()
    return categories

# Supplier operations
def add_supplier(name, contact_person=None, email=None, phone=None, address=None):
    session = get_session()
    supplier = Supplier(
        name=name,
        contact_person=contact_person,
        email=email,
        phone=phone,
        address=address
    )
    session.add(supplier)
    session.commit()
    session.close()
    return supplier

def get_all_suppliers():
    session = get_session()
    suppliers = session.query(Supplier).all()
    session.close()
    return suppliers

# Enhanced Product operations
def add_product(name, quantity, unit_price, measure_unit, category_id=None, supplier_id=None,
                description=None, alert_threshold=10, width=None, height=None,
                material_type=None):
    session = get_session()
    product = Product(
        name=name,
        quantity=quantity,
        unit_price=unit_price,
        measure_unit=measure_unit,
        category_id=category_id,
        supplier_id=supplier_id,
        description=description,
        alert_threshold=alert_threshold,
        width=width,
        height=height,
        material_type=material_type
    )
    session.add(product)
    session.commit()
    
    # Track initial creation
    track_edit(session, product.id, "creation", None, "Product created")
    session.commit()
    session.close()
    return product

def update_product(product_id, **kwargs):
    session = get_session()
    product = session.query(Product).filter(Product.id == product_id).first()
    if product:
        # Track price change if unit_price is being updated
        if 'unit_price' in kwargs and kwargs['unit_price'] != product.unit_price:
            price_history = PriceHistory(
                product_id=product.id,
                old_price=product.unit_price,
                new_price=kwargs['unit_price']
            )
            session.add(price_history)
        
        # Track quantity change if quantity is being updated
        if 'quantity' in kwargs:
            quantity_change = kwargs['quantity'] - product.quantity
            if quantity_change != 0:
                stock_movement = StockMovement(
                    product_id=product.id,
                    quantity_changed=quantity_change,
                    reference_type='adjustment',
                    notes='Manual adjustment'
                )
                session.add(stock_movement)
        
        # Track all changes
        for key, new_value in kwargs.items():
            old_value = getattr(product, key)
            if old_value != new_value:
                track_edit(session, product.id, key, old_value, new_value)
                setattr(product, key, new_value)
        
        session.commit()
    session.close()
    return product

def search_products(search_term):
    session = get_session()
    products = session.query(Product)\
        .options(sqlalchemy.orm.joinedload(Product.category))\
        .options(sqlalchemy.orm.joinedload(Product.supplier))\
        .filter(
            or_(
                Product.name.ilike(f"%{search_term}%"),
                Product.description.ilike(f"%{search_term}%")
            )
        ).all()
    session.close()
    return products

# Report operations
def get_low_stock_products():
    session = get_session()
    products = session.query(Product).filter(
        Product.quantity <= Product.alert_threshold
    ).all()
    session.close()
    return products

def get_stock_movements(product_id=None, start_date=None, end_date=None):
    session = get_session()
    query = session.query(StockMovement)
    
    if product_id:
        query = query.filter(StockMovement.product_id == product_id)
    if start_date:
        query = query.filter(StockMovement.timestamp >= start_date)
    if end_date:
        query = query.filter(StockMovement.timestamp <= end_date)
    
    movements = query.order_by(StockMovement.timestamp.desc()).all()
    session.close()
    return movements

def get_price_history(product_id):
    session = get_session()
    history = session.query(PriceHistory)\
        .filter(PriceHistory.product_id == product_id)\
        .order_by(PriceHistory.changed_at.desc())\
        .all()
    session.close()
    return history

# Customer operations
def add_customer(name, email=None, phone=None, address=None, company_name=None):
    session = get_session()
    customer = Customer(
        name=name,
        email=email,
        phone=phone,
        address=address,
        company_name=company_name
    )
    session.add(customer)
    session.commit()
    session.close()
    return customer

def get_all_customers():
    session = get_session()
    customers = session.query(Customer).all()
    session.close()
    return customers

# Sales Order operations
def create_sales_order(customer_id, items, notes=None, created_by_id=None):
    session = get_session()
    
    # Create the order
    order = SalesOrder(
        customer_id=customer_id,
        notes=notes,
        created_by_id=created_by_id
    )
    session.add(order)
    session.flush()  # Get the order ID
    
    total_amount = 0
    
    # Add items and update stock
    for item_data in items:
        item = SalesOrderItem(
            order_id=order.id,
            product_id=item_data['product_id'],
            quantity=item_data['quantity'],
            unit_price=item_data['unit_price'],
            width=item_data.get('width'),
            height=item_data.get('height'),
            notes=item_data.get('notes')
        )
        session.add(item)
        
        # Update product stock
        product = session.query(Product).filter(Product.id == item_data['product_id']).first()
        if product:
            product.quantity -= item_data['quantity']
            
            # Record stock movement
            movement = StockMovement(
                product_id=product.id,
                quantity_changed=-item_data['quantity'],
                reference_type='sale',
                reference_id=order.id,
                performed_by_id=created_by_id
            )
            session.add(movement)
            
            total_amount += item_data['quantity'] * item_data['unit_price']
    
    order.total_amount = total_amount
    session.commit()
    session.close()
    return order

def get_sales_order(order_id):
    session = get_session()
    order = session.query(SalesOrder)\
        .filter(SalesOrder.id == order_id)\
        .first()
    session.close()
    return order

# Purchase Order operations
def create_purchase_order(supplier_id, items, notes=None, created_by_id=None):
    session = get_session()
    
    order = PurchaseOrder(
        supplier_id=supplier_id,
        notes=notes,
        created_by_id=created_by_id
    )
    session.add(order)
    session.flush()
    
    total_amount = 0
    
    for item_data in items:
        item = PurchaseOrderItem(
            order_id=order.id,
            product_id=item_data['product_id'],
            quantity=item_data['quantity'],
            unit_price=item_data['unit_price'],
            notes=item_data.get('notes')
        )
        session.add(item)
        total_amount += item_data['quantity'] * item_data['unit_price']
    
    order.total_amount = total_amount
    session.commit()
    session.close()
    return order

def receive_purchase_order(order_id, received_by_id):
    session = get_session()
    order = session.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).first()
    
    if order and order.status == 'pending':
        order.status = 'received'
        
        # Update stock for each item
        for item in order.items:
            product = session.query(Product).filter(Product.id == item.product_id).first()
            if product:
                product.quantity += item.quantity
                
                # Record stock movement
                movement = StockMovement(
                    product_id=product.id,
                    quantity_changed=item.quantity,
                    reference_type='purchase',
                    reference_id=order.id,
                    performed_by_id=received_by_id
                )
                session.add(movement)
        
        session.commit()
    session.close()
    return order 