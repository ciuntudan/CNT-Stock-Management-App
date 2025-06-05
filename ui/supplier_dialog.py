from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox
)
from database.operations import add_supplier
from .styles import STYLES, COLORS

class SupplierDialog(QDialog):
    def __init__(self, parent=None, supplier=None):
        super().__init__(parent)
        self.supplier = supplier
        self.setWindowTitle("Adaugă Furnizor" if not supplier else "Editează Furnizor")
        self.setup_ui()
        if supplier:
            self.load_supplier_data()
        
        # Set dialog size and style
        self.setMinimumWidth(500)
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
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Name
        name_layout = QHBoxLayout()
        name_label = QLabel("Denumire:")
        self.name_input = QLineEdit()
        if self.supplier:
            self.name_input.setText(self.supplier.name)
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # Contact person
        contact_layout = QHBoxLayout()
        contact_label = QLabel("Persoană de contact:")
        self.contact_input = QLineEdit()
        if self.supplier:
            self.contact_input.setText(self.supplier.contact_person)
        contact_layout.addWidget(contact_label)
        contact_layout.addWidget(self.contact_input)
        layout.addLayout(contact_layout)
        
        # Email
        email_layout = QHBoxLayout()
        email_label = QLabel("Email:")
        self.email_input = QLineEdit()
        if self.supplier:
            self.email_input.setText(self.supplier.email)
        email_layout.addWidget(email_label)
        email_layout.addWidget(self.email_input)
        layout.addLayout(email_layout)
        
        # Phone
        phone_layout = QHBoxLayout()
        phone_label = QLabel("Telefon:")
        self.phone_input = QLineEdit()
        if self.supplier:
            self.phone_input.setText(self.supplier.phone)
        phone_layout.addWidget(phone_label)
        phone_layout.addWidget(self.phone_input)
        layout.addLayout(phone_layout)
        
        # Address
        address_layout = QHBoxLayout()
        address_label = QLabel("Adresă:")
        self.address_input = QLineEdit()
        if self.supplier:
            self.address_input.setText(self.supplier.address)
        address_layout.addWidget(address_label)
        address_layout.addWidget(self.address_input)
        layout.addLayout(address_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Anulează")
        cancel_btn.setStyleSheet(STYLES['button'] % (COLORS['gray'], '#757575', '#616161'))
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("Salvează")
        save_btn.setStyleSheet(STYLES['button'] % (COLORS['success'], '#43A047', '#388E3C'))
        save_btn.clicked.connect(self.save_supplier)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def save_supplier(self):
        if not self.validate_form():
            return
        
        try:
            supplier = add_supplier(
                name=self.name_input.text().strip(),
                contact_person=self.contact_input.text().strip(),
                email=self.email_input.text().strip(),
                phone=self.phone_input.text().strip(),
                address=self.address_input.text().strip()
            )
            
            QMessageBox.information(
                self,
                "Succes",
                "Furnizorul a fost salvat cu succes!"
            )
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Eroare",
                f"A apărut o eroare la salvarea furnizorului:\n{str(e)}"
            )
    
    def validate_form(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Validare", "Introduceți denumirea furnizorului!")
            return False
        
        return True
    
    def load_supplier_data(self):
        if not self.supplier:
            return
            
        self.name_input.setText(self.supplier.name)
        self.contact_input.setText(self.supplier.contact_person or "")
        self.email_input.setText(self.supplier.email or "")
        self.phone_input.setText(self.supplier.phone or "")
        self.address_input.setText(self.supplier.address or "") 