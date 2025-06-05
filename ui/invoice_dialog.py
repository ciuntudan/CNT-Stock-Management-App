from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
    QSpinBox, QDoubleSpinBox, QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt
from database.operations import (
    get_all_companies, get_all_customers, get_all_products,
    create_invoice
)
from utils.pdf_generator import generate_invoice_pdf
from .customer_dialog import CustomerDialog
from .styles import STYLES, COLORS
import os
from datetime import datetime

class InvoiceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Generare Factură")
        self.setMinimumWidth(800)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Company selection
        company_layout = QHBoxLayout()
        company_layout.addWidget(QLabel("Firma emitentă:"))
        self.company_combo = QComboBox()
        self.load_companies()
        company_layout.addWidget(self.company_combo)
        
        # Series input
        company_layout.addWidget(QLabel("Seria:"))
        self.series_input = QLineEdit()
        self.series_input.setMaxLength(10)
        self.series_input.setFixedWidth(100)
        company_layout.addWidget(self.series_input)
        
        layout.addLayout(company_layout)
        
        # Customer section with management button
        customer_layout = QHBoxLayout()
        customer_layout.addWidget(QLabel("Client:"))
        self.customer_combo = QComboBox()
        self.load_customers()
        customer_layout.addWidget(self.customer_combo)
        
        manage_customers_btn = QPushButton("Gestionare Clienti")
        manage_customers_btn.setStyleSheet(STYLES['button'] % (COLORS['primary'], '#1976D2', '#1565C0'))
        manage_customers_btn.clicked.connect(self.show_customer_dialog)
        customer_layout.addWidget(manage_customers_btn)
        
        layout.addLayout(customer_layout)
        
        # Products table
        layout.addWidget(QLabel("Produse:"))
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels([
            "Denumire", "U.M.", "Cantitate", "Preț unitar", "Total"
        ])
        layout.addWidget(self.items_table)
        
        # Add product button
        add_product_btn = QPushButton("Adaugă Produs")
        add_product_btn.clicked.connect(self.add_product_row)
        layout.addWidget(add_product_btn)
        
        # Totals
        totals_layout = QHBoxLayout()
        
        # Subtotal
        totals_layout.addWidget(QLabel("Subtotal:"))
        self.subtotal_label = QLabel("0.00 RON")
        totals_layout.addWidget(self.subtotal_label)
        
        # VAT
        totals_layout.addWidget(QLabel("TVA (19%):"))
        self.vat_label = QLabel("0.00 RON")
        totals_layout.addWidget(self.vat_label)
        
        # Total
        totals_layout.addWidget(QLabel("Total:"))
        self.total_label = QLabel("0.00 RON")
        totals_layout.addWidget(self.total_label)
        
        layout.addLayout(totals_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        generate_btn = QPushButton("Generează Factură")
        generate_btn.clicked.connect(self.generate_invoice)
        cancel_btn = QPushButton("Anulează")
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(generate_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
    
    def load_companies(self):
        self.company_combo.clear()
        companies = get_all_companies()
        for company in companies:
            self.company_combo.addItem(company.name, company.id)
    
    def load_customers(self):
        self.customer_combo.clear()
        customers = get_all_customers()
        for customer in customers:
            display_name = f"{customer.name}"
            if customer.company_name:
                display_name += f" ({customer.company_name})"
            self.customer_combo.addItem(display_name, customer.id)
    
    def show_customer_dialog(self):
        dialog = CustomerDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            # Refresh customer list
            self.load_customers()
    
    def add_product_row(self):
        row = self.items_table.rowCount()
        self.items_table.insertRow(row)
        
        # Product name
        name = QLineEdit()
        self.items_table.setCellWidget(row, 0, name)
        
        # Unit of measure
        um = QComboBox()
        um.addItems(["buc", "m", "m²", "kg", "l"])
        um.setCurrentText("buc")
        self.items_table.setCellWidget(row, 1, um)
        
        # Quantity
        quantity = QDoubleSpinBox()
        quantity.setMinimum(0.01)
        quantity.setMaximum(9999.99)
        quantity.setValue(1)
        quantity.valueChanged.connect(self.update_totals)
        self.items_table.setCellWidget(row, 2, quantity)
        
        # Unit price
        price = QDoubleSpinBox()
        price.setMinimum(0.01)
        price.setMaximum(999999.99)
        price.setValue(0)
        price.valueChanged.connect(self.update_totals)
        self.items_table.setCellWidget(row, 3, price)
        
        # Total
        total = QLabel("0.00 RON")
        total.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.items_table.setCellWidget(row, 4, total)
        
        self.update_totals()
    
    def update_totals(self):
        subtotal = 0
        
        for row in range(self.items_table.rowCount()):
            quantity = self.items_table.cellWidget(row, 2).value()
            price = self.items_table.cellWidget(row, 3).value()
            total = quantity * price
            
            total_label = self.items_table.cellWidget(row, 4)
            total_label.setText(f"{total:.2f} RON")
            
            subtotal += total
        
        vat = subtotal * 0.19
        total = subtotal + vat
        
        self.subtotal_label.setText(f"{subtotal:.2f} RON")
        self.vat_label.setText(f"{vat:.2f} RON")
        self.total_label.setText(f"{total:.2f} RON")
    
    def generate_invoice(self):
        if not self.validate_form():
            return
        
        # Get selected company and customer
        company_id = self.company_combo.currentData()
        customer_id = self.customer_combo.currentData()
        series = self.series_input.text().strip().upper()
        
        # Prepare items
        items = []
        for row in range(self.items_table.rowCount()):
            name = self.items_table.cellWidget(row, 0).text()
            unit = self.items_table.cellWidget(row, 1).currentText()
            quantity = self.items_table.cellWidget(row, 2).value()
            unit_price = self.items_table.cellWidget(row, 3).value()
            
            items.append({
                'description': name,
                'measure_unit': unit,
                'quantity': quantity,
                'unit_price': unit_price
            })
        
        try:
            # Create invoice in database
            invoice = create_invoice(company_id, customer_id, items, series)
            
            # Generate PDF
            filename = f"Factura_{invoice.series}_{invoice.number:04d}.pdf"
            save_path = QFileDialog.getSaveFileName(
                self,
                "Salvează factura",
                filename,
                "PDF Files (*.pdf)"
            )[0]
            
            if save_path:
                generate_invoice_pdf(invoice, save_path)
                QMessageBox.information(
                    self,
                    "Succes",
                    f"Factura a fost generată cu succes și salvată în:\n{save_path}"
                )
                self.accept()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Eroare",
                f"A apărut o eroare la generarea facturii:\n{str(e)}"
            )
    
    def validate_form(self):
        if not self.company_combo.currentData():
            QMessageBox.warning(self, "Validare", "Selectați firma emitentă!")
            return False
        
        if not self.series_input.text().strip():
            QMessageBox.warning(self, "Validare", "Introduceți seria facturii!")
            return False
        
        if not self.customer_combo.currentData():
            QMessageBox.warning(self, "Validare", "Selectați clientul!")
            return False
        
        if self.items_table.rowCount() == 0:
            QMessageBox.warning(self, "Validare", "Adăugați cel puțin un produs!")
            return False
        
        # Validate product names
        for row in range(self.items_table.rowCount()):
            name = self.items_table.cellWidget(row, 0).text().strip()
            if not name:
                QMessageBox.warning(self, "Validare", f"Introduceți numele produsului pentru rândul {row + 1}!")
                return False
        
        return True 