from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QSpinBox, QDoubleSpinBox,
    QTextEdit, QCheckBox, QMessageBox, QWidget
)
from PyQt5.QtCore import Qt
from database.operations import get_all_categories, get_all_suppliers
from database.models import MeasureUnit
from .styles import STYLES, COLORS

class ProductDialog(QDialog):
    def __init__(self, parent=None, product=None):
        super().__init__(parent)
        self.product = product
        self.setWindowTitle("Adaugă produs" if not product else "Editează produs")
        self.setup_ui()
        if product:
            self.load_product_data()
        
        # Set dialog size and style
        self.setMinimumWidth(600)
        self.setStyleSheet('''
            QDialog {
                background-color: #FAFAFA;
            }
            QLabel {
                font-size: 13px;
                color: #424242;
            }
            QLineEdit, QSpinBox, QDoubleSpinBox, QTextEdit, QComboBox, QCheckBox {
                padding: 8px;
                border: 2px solid #E0E0E0;
                border-radius: 4px;
                background-color: white;
                font-size: 13px;
            }
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QTextEdit:focus, QComboBox:focus {
                border-color: #2196F3;
            }
            QSpinBox::up-button, QDoubleSpinBox::up-button {
                width: 20px;
            }
            QSpinBox::down-button, QDoubleSpinBox::down-button {
                width: 20px;
            }
            QCheckBox {
                border: none;
                padding: 5px;
            }
            QCheckBox:hover {
                background-color: #F5F5F5;
            }
        ''')
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Name and Unit
        form_layout1 = QHBoxLayout()
        
        name_layout = QVBoxLayout()
        name_label = QLabel("Nume:")
        self.name_input = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        form_layout1.addLayout(name_layout)
        
        unit_layout = QVBoxLayout()
        unit_label = QLabel("Unitate de masura:")
        self.unit_combo = QComboBox()
        self.unit_combo.setStyleSheet(STYLES['combo_box'])
        for unit in MeasureUnit:
            self.unit_combo.addItem(unit.value, unit)
        unit_layout.addWidget(unit_label)
        unit_layout.addWidget(self.unit_combo)
        form_layout1.addLayout(unit_layout)
        
        layout.addLayout(form_layout1)
        
        # Category and Supplier
        form_layout2 = QHBoxLayout()
        
        category_layout = QVBoxLayout()
        category_label = QLabel("Categorie:")
        self.category_combo = QComboBox()
        self.category_combo.setStyleSheet(STYLES['combo_box'])
        self.load_categories()
        category_layout.addWidget(category_label)
        category_layout.addWidget(self.category_combo)
        form_layout2.addLayout(category_layout)
        
        supplier_layout = QVBoxLayout()
        supplier_label = QLabel("Furnizor:")
        self.supplier_combo = QComboBox()
        self.supplier_combo.setStyleSheet(STYLES['combo_box'])
        self.load_suppliers()
        supplier_layout.addWidget(supplier_label)
        supplier_layout.addWidget(self.supplier_combo)
        form_layout2.addLayout(supplier_layout)
        
        layout.addLayout(form_layout2)
        
        # Quantity and Price
        form_layout3 = QHBoxLayout()
        
        quantity_layout = QVBoxLayout()
        quantity_label = QLabel("Cantitate:")
        self.quantity_input = QSpinBox()
        self.quantity_input.setMaximum(999999)
        quantity_layout.addWidget(quantity_label)
        quantity_layout.addWidget(self.quantity_input)
        form_layout3.addLayout(quantity_layout)
        
        price_layout = QVBoxLayout()
        price_label = QLabel("Pret unitar (cu TVA):")
        self.price_input = QDoubleSpinBox()
        self.price_input.setMaximum(999999.99)
        self.price_input.setSuffix(" RON")
        price_layout.addWidget(price_label)
        price_layout.addWidget(self.price_input)
        form_layout3.addLayout(price_layout)
        
        layout.addLayout(form_layout3)
        
        # Dimensions checkbox and inputs
        dimensions_layout = QVBoxLayout()
        self.use_dimensions = QCheckBox("Adauga dimensiuni")
        self.use_dimensions.stateChanged.connect(self.toggle_dimensions)
        dimensions_layout.addWidget(self.use_dimensions)
        
        self.dimensions_widget = QWidget()
        dimensions_input_layout = QHBoxLayout(self.dimensions_widget)
        dimensions_input_layout.setContentsMargins(0, 0, 0, 0)
        
        self.width_input = QDoubleSpinBox()
        self.width_input.setMaximum(999999.99)
        self.height_input = QDoubleSpinBox()
        self.height_input.setMaximum(999999.99)
        
        dimensions_input_layout.addWidget(QLabel("Latime:"))
        dimensions_input_layout.addWidget(self.width_input)
        dimensions_input_layout.addWidget(QLabel("Inaltime:"))
        dimensions_input_layout.addWidget(self.height_input)
        
        self.dimension_unit = QComboBox()
        self.dimension_unit.addItems(["metri", "centimetri"])
        dimensions_input_layout.addWidget(self.dimension_unit)
        
        dimensions_layout.addWidget(self.dimensions_widget)
        self.dimensions_widget.setVisible(False)
        layout.addLayout(dimensions_layout)
        
        # Description
        description_label = QLabel("Descriere:")
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        layout.addWidget(description_label)
        layout.addWidget(self.description_input)
        
        # Alert Threshold
        threshold_layout = QHBoxLayout()
        threshold_label = QLabel("Prag minim:")
        self.threshold_input = QSpinBox()
        self.threshold_input.setMaximum(999999)
        threshold_layout.addWidget(threshold_label)
        threshold_layout.addWidget(self.threshold_input)
        threshold_layout.addStretch()
        layout.addLayout(threshold_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Anuleaza")
        cancel_btn.setStyleSheet(STYLES['button'] % (COLORS['gray'], '#757575', '#616161'))
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("Salveaza")
        save_btn.setStyleSheet(STYLES['button'] % (COLORS['success'], '#43A047', '#388E3C'))
        save_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_categories(self):
        self.category_combo.clear()
        self.category_combo.addItem("-- Selecteaza categoria --", None)
        categories = get_all_categories()
        for category in categories:
            self.category_combo.addItem(category.name, category.id)
    
    def load_suppliers(self):
        self.supplier_combo.clear()
        self.supplier_combo.addItem("-- Selecteaza furnizorul --", None)
        suppliers = get_all_suppliers()
        for supplier in suppliers:
            self.supplier_combo.addItem(supplier.name, supplier.id)
    
    def toggle_dimensions(self, state):
        self.dimensions_widget.setVisible(state == Qt.Checked)
        if not state == Qt.Checked:
            self.width_input.setValue(0)
            self.height_input.setValue(0)
    
    def get_values(self):
        # Get dimensions only if checkbox is checked
        width = height = None
        if self.use_dimensions.isChecked():
            width = self.width_input.value()
            height = self.height_input.value()
            if self.dimension_unit.currentText() == "centimetri":
                width = width / 100
                height = height / 100
        
        return (
            self.name_input.text(),
            self.quantity_input.value(),
            self.price_input.value(),
            self.unit_combo.currentData(),
            self.category_combo.currentData(),
            self.supplier_combo.currentData(),
            None,  # material_type removed
            width,
            height,
            self.description_input.toPlainText(),
            self.threshold_input.value()
        )
    
    def load_product_data(self):
        self.name_input.setText(self.product.name)
        self.quantity_input.setValue(self.product.quantity)
        self.price_input.setValue(self.product.unit_price)
        
        # Set dimensions if they exist
        if self.product.width is not None and self.product.height is not None and (self.product.width > 0 or self.product.height > 0):
            self.use_dimensions.setChecked(True)
            width = self.product.width
            height = self.product.height
            if width < 1 and height < 1:
                self.dimension_unit.setCurrentText("centimetri")
                width *= 100
                height *= 100
            else:
                self.dimension_unit.setCurrentText("metri")
            self.width_input.setValue(width)
            self.height_input.setValue(height)
        else:
            self.use_dimensions.setChecked(False)
        
        self.description_input.setText(self.product.description or "")
        self.threshold_input.setValue(self.product.alert_threshold)
        
        # Set measure unit
        index = self.unit_combo.findData(self.product.measure_unit)
        if index >= 0:
            self.unit_combo.setCurrentIndex(index)
        
        if self.product.category_id:
            index = self.category_combo.findData(self.product.category_id)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
        
        if self.product.supplier_id:
            index = self.supplier_combo.findData(self.product.supplier_id)
            if index >= 0:
                self.supplier_combo.setCurrentIndex(index)
    
    def accept(self):
        if not self.name_input.text():
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Numele produsului este obligatoriu.")
            msg.setWindowTitle("Atentie")
            msg.setStyleSheet('''
                QMessageBox {
                    background-color: white;
                }
                QPushButton {
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 13px;
                    color: white;
                    background-color: #FFC107;
                }
            ''')
            msg.exec_()
            return
        super().accept()
    
    def reject(self):
        super().reject() 