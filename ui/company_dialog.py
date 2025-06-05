from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox
)
from database.operations import add_company

class CompanyDialog(QDialog):
    def __init__(self, parent=None, company=None):
        super().__init__(parent)
        self.company = company
        self.setWindowTitle("Adaugă Firmă" if not company else "Editează Firma")
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Company details
        form_layout = QVBoxLayout()
        
        # Name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Denumire:"))
        self.name_input = QLineEdit()
        if self.company:
            self.name_input.setText(self.company.name)
        name_layout.addWidget(self.name_input)
        form_layout.addLayout(name_layout)
        
        # Registration number (CUI)
        reg_layout = QHBoxLayout()
        reg_layout.addWidget(QLabel("CUI:"))
        self.reg_input = QLineEdit()
        if self.company:
            self.reg_input.setText(self.company.registration_number)
        reg_layout.addWidget(self.reg_input)
        form_layout.addLayout(reg_layout)
        
        # VAT number
        vat_layout = QHBoxLayout()
        vat_layout.addWidget(QLabel("Nr. Reg. Com.:"))
        self.vat_input = QLineEdit()
        if self.company:
            self.vat_input.setText(self.company.vat_number)
        vat_layout.addWidget(self.vat_input)
        form_layout.addLayout(vat_layout)
        
        # Address
        addr_layout = QHBoxLayout()
        addr_layout.addWidget(QLabel("Adresa:"))
        self.addr_input = QLineEdit()
        if self.company:
            self.addr_input.setText(self.company.address)
        addr_layout.addWidget(self.addr_input)
        form_layout.addLayout(addr_layout)
        
        # Bank name
        bank_layout = QHBoxLayout()
        bank_layout.addWidget(QLabel("Banca:"))
        self.bank_input = QLineEdit()
        if self.company:
            self.bank_input.setText(self.company.bank_name)
        bank_layout.addWidget(self.bank_input)
        form_layout.addLayout(bank_layout)
        
        # Bank account
        account_layout = QHBoxLayout()
        account_layout.addWidget(QLabel("IBAN:"))
        self.account_input = QLineEdit()
        if self.company:
            self.account_input.setText(self.company.bank_account)
        account_layout.addWidget(self.account_input)
        form_layout.addLayout(account_layout)
        
        # Phone
        phone_layout = QHBoxLayout()
        phone_layout.addWidget(QLabel("Telefon:"))
        self.phone_input = QLineEdit()
        if self.company:
            self.phone_input.setText(self.company.phone)
        phone_layout.addWidget(self.phone_input)
        form_layout.addLayout(phone_layout)
        
        # Email
        email_layout = QHBoxLayout()
        email_layout.addWidget(QLabel("Email:"))
        self.email_input = QLineEdit()
        if self.company:
            self.email_input.setText(self.company.email)
        email_layout.addWidget(self.email_input)
        form_layout.addLayout(email_layout)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("Salvează")
        save_btn.clicked.connect(self.save_company)
        cancel_btn = QPushButton("Anulează")
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
    
    def save_company(self):
        if not self.validate_form():
            return
        
        try:
            company = add_company(
                name=self.name_input.text().strip(),
                registration_number=self.reg_input.text().strip(),
                vat_number=self.vat_input.text().strip(),
                address=self.addr_input.text().strip(),
                bank_name=self.bank_input.text().strip(),
                bank_account=self.account_input.text().strip(),
                phone=self.phone_input.text().strip(),
                email=self.email_input.text().strip()
            )
            
            QMessageBox.information(
                self,
                "Succes",
                "Firma a fost salvată cu succes!"
            )
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Eroare",
                f"A apărut o eroare la salvarea firmei:\n{str(e)}"
            )
    
    def validate_form(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Validare", "Introduceți denumirea firmei!")
            return False
        
        if not self.reg_input.text().strip():
            QMessageBox.warning(self, "Validare", "Introduceți CUI-ul!")
            return False
        
        if not self.addr_input.text().strip():
            QMessageBox.warning(self, "Validare", "Introduceți adresa!")
            return False
        
        return True 