from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QTableWidget, QTableWidgetItem,
    QHeaderView
)
from PyQt5.QtCore import Qt
from database.operations import add_customer, get_all_customers, update_customer, delete_customer
from .styles import STYLES, COLORS

class CustomerDialog(QDialog):
    def __init__(self, parent=None, customer=None):
        super().__init__(parent)
        self.customer = customer
        self.setWindowTitle("Gestionare Clienti")
        self.setup_ui()
        self.load_customers()
        
        # Set dialog size and style
        self.setMinimumWidth(800)
        self.setStyleSheet('''
            QDialog {
                background-color: #FAFAFA;
            }
            QLabel {
                font-size: 13px;
                color: #424242;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #E0E0E0;
                border-radius: 4px;
                background-color: white;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #2196F3;
            }
        ''')
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Customer details section
        details_layout = QVBoxLayout()
        
        # Name
        name_layout = QHBoxLayout()
        name_label = QLabel("Nume:")
        self.name_input = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        details_layout.addLayout(name_layout)
        
        # Address
        address_layout = QHBoxLayout()
        address_label = QLabel("Adresa:")
        self.address_input = QLineEdit()
        address_layout.addWidget(address_label)
        address_layout.addWidget(self.address_input)
        details_layout.addLayout(address_layout)
        
        # CIF (Registration number)
        cif_layout = QHBoxLayout()
        cif_label = QLabel("CIF:")
        self.cif_input = QLineEdit()
        cif_layout.addWidget(cif_label)
        cif_layout.addWidget(self.cif_input)
        details_layout.addLayout(cif_layout)
        
        # Trade Register Number
        reg_layout = QHBoxLayout()
        reg_label = QLabel("Nr. Reg. Com:")
        self.reg_input = QLineEdit()
        reg_layout.addWidget(reg_label)
        reg_layout.addWidget(self.reg_input)
        details_layout.addLayout(reg_layout)
        
        # Bank Account (IBAN)
        iban_layout = QHBoxLayout()
        iban_label = QLabel("Cont (IBAN):")
        self.iban_input = QLineEdit()
        iban_layout.addWidget(iban_label)
        iban_layout.addWidget(self.iban_input)
        details_layout.addLayout(iban_layout)
        
        # Bank Name
        bank_layout = QHBoxLayout()
        bank_label = QLabel("Banca:")
        self.bank_input = QLineEdit()
        bank_layout.addWidget(bank_label)
        bank_layout.addWidget(self.bank_input)
        details_layout.addLayout(bank_layout)
        
        layout.addLayout(details_layout)
        
        # Buttons for customer operations
        button_layout = QHBoxLayout()
        
        add_btn = QPushButton("Adauga Client")
        add_btn.setStyleSheet(STYLES['button'] % (COLORS['success'], '#43A047', '#388E3C'))
        add_btn.clicked.connect(self.add_customer)
        
        update_btn = QPushButton("Actualizeaza")
        update_btn.setStyleSheet(STYLES['button'] % (COLORS['primary'], '#1976D2', '#1565C0'))
        update_btn.clicked.connect(self.update_selected_customer)
        
        delete_btn = QPushButton("Sterge")
        delete_btn.setStyleSheet(STYLES['button'] % (COLORS['danger'], '#E53935', '#D32F2F'))
        delete_btn.clicked.connect(self.delete_selected_customer)
        
        close_btn = QPushButton("Inchide")
        close_btn.setStyleSheet(STYLES['button'] % (COLORS['gray'], '#757575', '#616161'))
        close_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(add_btn)
        button_layout.addWidget(update_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        # Customers table
        self.customers_table = QTableWidget()
        self.customers_table.setColumnCount(6)
        self.customers_table.setHorizontalHeaderLabels([
            "Nume", "Adresa", "CIF", "Nr. Reg. Com", "Cont (IBAN)", "Banca"
        ])
        self.customers_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.customers_table.setStyleSheet('''
            QTableWidget {
                border: none;
                background-color: white;
                gridline-color: #E0E0E0;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #E3F2FD;
                color: #212121;
            }
            QHeaderView::section {
                background-color: #F5F5F5;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #E0E0E0;
                font-weight: bold;
            }
        ''')
        self.customers_table.itemClicked.connect(self.load_customer_data)
        layout.addWidget(self.customers_table)
    
    def load_customers(self):
        self.customers_table.setRowCount(0)
        customers = get_all_customers()
        
        for customer in customers:
            row = self.customers_table.rowCount()
            self.customers_table.insertRow(row)
            
            items = [
                QTableWidgetItem(customer.name),
                QTableWidgetItem(customer.address or ""),
                QTableWidgetItem(customer.registration_number or ""),
                QTableWidgetItem(customer.trade_register_number or ""),
                QTableWidgetItem(customer.bank_account or ""),
                QTableWidgetItem(customer.bank_name or "")
            ]
            
            for col, item in enumerate(items):
                item.setTextAlignment(Qt.AlignCenter)
                self.customers_table.setItem(row, col, item)
    
    def load_customer_data(self, item):
        row = item.row()
        
        self.name_input.setText(self.customers_table.item(row, 0).text())
        self.address_input.setText(self.customers_table.item(row, 1).text())
        self.cif_input.setText(self.customers_table.item(row, 2).text())
        self.reg_input.setText(self.customers_table.item(row, 3).text())
        self.iban_input.setText(self.customers_table.item(row, 4).text())
        self.bank_input.setText(self.customers_table.item(row, 5).text())
        
        # Store the selected customer's data
        self.current_customer = {
            'name': self.name_input.text(),
            'address': self.address_input.text(),
            'registration_number': self.cif_input.text(),
            'trade_register_number': self.reg_input.text(),
            'bank_account': self.iban_input.text(),
            'bank_name': self.bank_input.text()
        }
    
    def clear_inputs(self):
        self.name_input.clear()
        self.address_input.clear()
        self.cif_input.clear()
        self.reg_input.clear()
        self.iban_input.clear()
        self.bank_input.clear()
        self.current_customer = None
    
    def add_customer(self):
        if not self.validate_form():
            return
        
        try:
            add_customer(
                name=self.name_input.text().strip(),
                address=self.address_input.text().strip(),
                registration_number=self.cif_input.text().strip(),
                trade_register_number=self.reg_input.text().strip(),
                bank_account=self.iban_input.text().strip(),
                bank_name=self.bank_input.text().strip()
            )
            
            self.clear_inputs()
            self.load_customers()
            QMessageBox.information(self, "Succes", "Clientul a fost adaugat cu succes!")
            
        except Exception as e:
            QMessageBox.critical(self, "Eroare", f"A aparut o eroare la adaugarea clientului:\n{str(e)}")
    
    def update_selected_customer(self):
        if not hasattr(self, 'current_customer'):
            QMessageBox.warning(self, "Atentie", "Selectati un client pentru actualizare!")
            return
        
        if not self.validate_form():
            return
        
        try:
            update_customer(
                self.current_customer_id,
                name=self.name_input.text().strip(),
                address=self.address_input.text().strip(),
                registration_number=self.cif_input.text().strip(),
                trade_register_number=self.reg_input.text().strip(),
                bank_account=self.iban_input.text().strip(),
                bank_name=self.bank_input.text().strip()
            )
            
            self.clear_inputs()
            self.load_customers()
            QMessageBox.information(self, "Succes", "Clientul a fost actualizat cu succes!")
            
        except Exception as e:
            QMessageBox.critical(self, "Eroare", f"A aparut o eroare la actualizarea clientului:\n{str(e)}")
    
    def delete_selected_customer(self):
        if not hasattr(self, 'current_customer'):
            QMessageBox.warning(self, "Atentie", "Selectati un client pentru stergere!")
            return
        
        reply = QMessageBox.question(
            self,
            "Confirmare stergere",
            "Sunteti sigur ca doriti sa stergeti acest client?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                delete_customer(self.current_customer_id)
                self.clear_inputs()
                self.load_customers()
                QMessageBox.information(self, "Succes", "Clientul a fost sters cu succes!")
                
            except Exception as e:
                QMessageBox.critical(self, "Eroare", f"A aparut o eroare la stergerea clientului:\n{str(e)}")
    
    def validate_form(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Validare", "Numele clientului este obligatoriu!")
            return False
        if not self.cif_input.text().strip():
            QMessageBox.warning(self, "Validare", "CIF-ul este obligatoriu!")
            return False
        if not self.reg_input.text().strip():
            QMessageBox.warning(self, "Validare", "Numarul de inregistrare la Registrul Comertului este obligatoriu!")
            return False
        return True 