from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTableWidget, QTableWidgetItem, QLabel,
                             QLineEdit, QMessageBox, QFileDialog, QInputDialog,
                             QSpinBox, QDoubleSpinBox, QTextEdit, QComboBox,
                             QTabWidget, QDialog, QFrame, QHeaderView, QButtonGroup,
                             QStackedWidget, QGridLayout, QCheckBox, QScrollArea,
                             QProgressBar)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon, QPixmap
from database.operations import (
    add_product, get_all_products, update_product, delete_product,
    search_products, get_low_stock_products, get_all_categories,
    get_all_suppliers, get_product_history, get_product_by_id
)
from database.models import MeasureUnit
from utils.export import export_to_excel, export_to_csv
from datetime import datetime
import operator

# Modern color scheme
COLORS = {
    'primary': '#2196F3',      # Blue
    'secondary': '#FF4081',    # Pink
    'success': '#4CAF50',      # Green
    'warning': '#FFC107',      # Amber
    'danger': '#F44336',       # Red
    'light': '#FAFAFA',       # Almost White
    'dark': '#212121',        # Almost Black
    'gray': '#9E9E9E',         # Medium Gray
    'title_bar': '#2C3E50'    # Dark Blue for title bar
}

STYLES = {
    'main_window': '''
        QMainWindow {
            background-color: #FAFAFA;
        }
        QLabel {
            font-size: 14px;
        }
        QPushButton {
            font-size: 14px;
        }
        QComboBox {
            font-size: 14px;
        }
        QLineEdit {
            font-size: 14px;
        }
        QSpinBox, QDoubleSpinBox {
            font-size: 14px;
        }
        QTableWidget {
            font-size: 14px;
        }
        QMenuBar {
            background-color: ''' + COLORS['title_bar'] + ''';
            color: white;
        }
        QMenuBar::item {
            background-color: transparent;
            padding: 8px 12px;
            color: white;
        }
        QMenuBar::item:selected {
            background-color: #34495E;
        }
        QTitleBar {
            background-color: ''' + COLORS['title_bar'] + ''';
            color: white;
        }
        QMainWindow::title {
            background-color: ''' + COLORS['title_bar'] + ''';
            color: white;
            height: 35px;
        }
    ''',
    'search_input': '''
        QLineEdit {
            padding: 10px;
            border: 2px solid #E0E0E0;
            border-radius: 4px;
            background-color: white;
            font-size: 14px;
        }
        QLineEdit:focus {
            border-color: #2196F3;
        }
    ''',
    'table': '''
        QTableWidget {
            border: none;
            background-color: white;
            gridline-color: #E0E0E0;
            font-size: 14px;
        }
        QTableWidget::item {
            padding: 8px;
        }
        QTableWidget::item:selected {
            background-color: #E3F2FD;
            color: #212121;
        }
        QHeaderView::section {
            background-color: #F5F5F5;
            padding: 12px;
            border: none;
            border-bottom: 2px solid #E0E0E0;
            font-weight: bold;
            font-size: 14px;
        }
    ''',
    'button': '''
        QPushButton {
            padding: 10px 20px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 14px;
            color: white;
            background-color: %s;
            border: none;
        }
        QPushButton:hover {
            background-color: %s;
        }
        QPushButton:pressed {
            background-color: %s;
        }
        QPushButton:disabled {
            background-color: #BDBDBD;
        }
    ''',
    'combo_box': '''
        QComboBox {
            padding: 10px;
            border: 2px solid #E0E0E0;
            border-radius: 4px;
            background-color: white;
            font-size: 14px;
        }
        QComboBox::drop-down {
            border: none;
            width: 24px;
        }
        QComboBox::down-arrow {
            image: url(down_arrow.png);
            width: 14px;
            height: 14px;
        }
    ''',
    'tab_widget': '''
        QTabWidget::pane {
            border: none;
            background-color: white;
        }
        QTabBar::tab {
            padding: 12px 24px;
            background-color: #F5F5F5;
            border: none;
            color: #757575;
            font-size: 14px;
        }
        QTabBar::tab:selected {
            background-color: white;
            color: #2196F3;
            border-bottom: 2px solid #2196F3;
        }
        QTabBar::tab:hover:!selected {
            background-color: #EEEEEE;
        }
    '''
}

class ModernFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet('''
            ModernFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #E0E0E0;
            }
        ''')

class HistoryDialog(QDialog):
    def __init__(self, product_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Istoric modificari")
        self.setup_ui()
        self.load_history(product_id)
        
        # Set dialog size and style
        self.setMinimumWidth(600)
        self.setStyleSheet('''
            QDialog {
                background-color: #FAFAFA;
            }
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
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # History table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels([
            "Data", "Camp", "Valoare veche", "Valoare noua"
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_table.verticalHeader().setVisible(False)
        layout.addWidget(self.history_table)
        
        # Close button
        button_layout = QHBoxLayout()
        close_btn = QPushButton("Inchide")
        close_btn.setStyleSheet(STYLES['button'] % (COLORS['gray'], '#757575', '#616161'))
        close_btn.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
    
    def load_history(self, product_id):
        history = get_product_history(product_id)
        self.history_table.setRowCount(0)
        
        for entry in history:
            row = self.history_table.rowCount()
            self.history_table.insertRow(row)
            
            date_item = QTableWidgetItem(entry.changed_at.strftime("%Y-%m-%d %H:%M"))
            field_item = QTableWidgetItem(entry.field_name)
            old_value_item = QTableWidgetItem(entry.old_value or "")
            new_value_item = QTableWidgetItem(entry.new_value or "")
            
            items = [date_item, field_item, old_value_item, new_value_item]
            for col, item in enumerate(items):
                item.setTextAlignment(Qt.AlignCenter)
                self.history_table.setItem(row, col, item)

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("Despre Aplicatie")
        self.setMinimumWidth(400)
        layout = QVBoxLayout(self)
        
        # Add logo
        logo_label = QLabel()
        logo_pixmap = QPixmap("bbr_black.png")
        scaled_pixmap = logo_pixmap.scaled(200, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(scaled_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)
        
        # Add version and copyright info
        info_text = QLabel(
            "CNT Stock Management\n"
            "Versiunea 1.0\n\n"
            "© 2024 CNT. Toate drepturile rezervate."
        )
        info_text.setStyleSheet('''
            font-size: 14px;
            color: #2C3E50;
        ''')
        info_text.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_text)
        
        # Add close button
        button_layout = QHBoxLayout()
        close_btn = QPushButton("Inchide")
        close_btn.setStyleSheet(STYLES['button'] % (COLORS['gray'], '#757575', '#616161'))
        close_btn.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_initial_data()
    
    def setup_ui(self):
        self.setWindowTitle("CNT Stock Management")
        self.setMinimumSize(1200, 800)
        
        # Set window flags for custom title bar
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowSystemMenuHint | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        
        # Set the stylesheet including title bar styling
        self.setStyleSheet(STYLES['main_window'])
        self.setWindowIcon(QIcon("favicon.png"))  # Set window icon
        self.showMaximized()  # Make window start maximized
        
        # Create central widget with horizontal layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create left menu
        menu_frame = QFrame()
        menu_frame.setStyleSheet('''
            QFrame {
                background-color: #2C3E50;
                min-width: 220px;
                max-width: 220px;
            }
            QPushButton {
                text-align: left;
                padding: 12px 20px;
                border: none;
                border-radius: 0;
                color: #ECF0F1;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #34495E;
            }
            QPushButton:checked {
                background-color: #2196F3;
            }
        ''')
        menu_layout = QVBoxLayout(menu_frame)
        menu_layout.setContentsMargins(0, 0, 0, 0)
        menu_layout.setSpacing(0)
        
        # Add logo area
        logo_frame = QFrame()
        logo_frame.setStyleSheet('''
            QFrame {
                background-color: #1F2937;
                min-height: 120px;
                max-height: 120px;
            }
        ''')
        logo_layout = QVBoxLayout(logo_frame)
        
        # Add logo image
        logo_label = QLabel()
        logo_pixmap = QPixmap("bbr_black.png")
        scaled_pixmap = logo_pixmap.scaled(180, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(scaled_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        logo_layout.addWidget(logo_label)
        
        menu_layout.addWidget(logo_frame)
        
        # Create menu buttons
        self.menu_buttons = {}
        menu_items = [
            ("Acasa", self.show_home_page),
            ("Stocuri", self.show_inventory_page),
            ("Comenzi", self.show_orders_page),
            ("Angajati", self.show_customers_page),
            ("Furnizori", self.show_suppliers_page),
            ("Rapoarte", self.show_reports_page),
        ]
        
        button_group = QButtonGroup(self)
        for text, slot in menu_items:
            btn = QPushButton(text)
            btn.setCheckable(True)
            button_group.addButton(btn)
            menu_layout.addWidget(btn)
            btn.clicked.connect(slot)
            self.menu_buttons[text] = btn
        
        menu_layout.addStretch()
        main_layout.addWidget(menu_frame)
        
        # Create stacked widget for pages
        self.pages = QStackedWidget()
        self.pages.setStyleSheet('''
            QStackedWidget {
                background-color: #FAFAFA;
            }
        ''')
        main_layout.addWidget(self.pages)
        
        # Create all pages
        self.home_page = self.create_home_page()
        self.inventory_page = self.create_inventory_page()
        self.orders_page = self.create_orders_page()
        self.customers_page = self.create_customers_page()
        self.suppliers_page = self.create_suppliers_page()
        self.reports_page = self.create_reports_page()
        
        # Add pages to stacked widget
        self.pages.addWidget(self.home_page)
        self.pages.addWidget(self.inventory_page)
        self.pages.addWidget(self.orders_page)
        self.pages.addWidget(self.customers_page)
        self.pages.addWidget(self.suppliers_page)
        self.pages.addWidget(self.reports_page)
        
        # Show home page by default
        self.menu_buttons["Acasa"].setChecked(True)
        self.show_home_page()
        
        # Add About button at the bottom of the menu
        about_btn = QPushButton("Despre")
        about_btn.setStyleSheet('''
            QPushButton {
                text-align: center;
                padding: 12px 20px;
                border: none;
                border-radius: 0;
                color: #ECF0F1;
                font-size: 14px;
                background-color: #1F2937;
            }
            QPushButton:hover {
                background-color: #374151;
            }
        ''')
        about_btn.clicked.connect(self.show_about_dialog)
        menu_layout.addWidget(about_btn)
    
    def create_home_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Welcome section
        welcome_frame = ModernFrame()
        welcome_layout = QVBoxLayout(welcome_frame)
        
        # Add logo to welcome section
        logo_label = QLabel()
        logo_pixmap = QPixmap("bbr_black.png")
        scaled_pixmap = logo_pixmap.scaled(300, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(scaled_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        welcome_layout.addWidget(logo_label)
        
        welcome_title = QLabel("CNT Stock Management App")
        welcome_title.setStyleSheet('''
            font-size: 28px;
            font-weight: bold;
            color: #2C3E50;
            margin-bottom: 10px;
        ''')
        welcome_title.setAlignment(Qt.AlignCenter)
        
        welcome_text = QLabel(
            "Bun venit in aplicatia de gestiune!\n"
        )
        welcome_text.setStyleSheet('''
            font-size: 18px;
            color: #34495E;
        ''')
        welcome_text.setAlignment(Qt.AlignCenter)
        
        welcome_layout.addWidget(welcome_title)
        welcome_layout.addWidget(welcome_text)
        layout.addWidget(welcome_frame)
        
        # Quick stats section
        stats_layout = QHBoxLayout()
        
        # Low stock items card
        low_stock_frame = ModernFrame()
        low_stock_layout = QVBoxLayout(low_stock_frame)
        low_stock_title = QLabel("Stocuri reduse")
        low_stock_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #E74C3C;")
        self.low_stock_count = QLabel("0")
        self.low_stock_count.setStyleSheet("font-size: 36px; font-weight: bold; color: #E74C3C;")
        low_stock_layout.addWidget(low_stock_title)
        low_stock_layout.addWidget(self.low_stock_count)
        stats_layout.addWidget(low_stock_frame)
        
        # Total products card
        total_products_frame = ModernFrame()
        total_products_layout = QVBoxLayout(total_products_frame)
        total_products_title = QLabel("Numar total de produse")
        total_products_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2980B9;")
        self.total_products_count = QLabel("0")
        self.total_products_count.setStyleSheet("font-size: 36px; font-weight: bold; color: #2980B9;")
        total_products_layout.addWidget(total_products_title)
        total_products_layout.addWidget(self.total_products_count)
        stats_layout.addWidget(total_products_frame)
        
        layout.addLayout(stats_layout)
        
        # VAT Calculator section
        calculator_frame = ModernFrame()
        calculator_layout = QVBoxLayout(calculator_frame)
        
        # Calculator title
        calc_title = QLabel("Calculator TVA (19%)")
        calc_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2C3E50; margin-bottom: 10px;")
        calculator_layout.addWidget(calc_title)
        
        # Price type selector
        price_type_layout = QHBoxLayout()
        price_type_label = QLabel("Tipul pretului:")
        self.price_type_combo = QComboBox()
        self.price_type_combo.addItems(["Pret fara TVA", "Pret cu TVA"])
        self.price_type_combo.setStyleSheet('''
            QComboBox {
                padding: 5px;
                border: 2px solid #E0E0E0;
                border-radius: 4px;
                background-color: white;
                min-width: 150px;
            }
            QComboBox:focus {
                border-color: #2196F3;
            }
        ''')
        self.price_type_combo.currentIndexChanged.connect(self.update_vat_calculation)
        price_type_layout.addWidget(price_type_label)
        price_type_layout.addWidget(self.price_type_combo)
        price_type_layout.addStretch()
        calculator_layout.addLayout(price_type_layout)
        
        # Input fields
        input_layout = QHBoxLayout()
        
        # Price input
        price_layout = QVBoxLayout()
        self.price_label = QLabel("Pret fara TVA:")
        self.calc_price_input = QDoubleSpinBox()
        self.calc_price_input.setMaximum(999999.99)
        self.calc_price_input.setSuffix(" LEI")
        self.calc_price_input.valueChanged.connect(self.update_vat_calculation)
        price_layout.addWidget(self.price_label)
        price_layout.addWidget(self.calc_price_input)
        input_layout.addLayout(price_layout)
        
        # Quantity input
        quantity_layout = QVBoxLayout()
        quantity_label = QLabel("Cantitate:")
        self.calc_quantity_input = QSpinBox()
        self.calc_quantity_input.setMaximum(999999)
        self.calc_quantity_input.setValue(1)  # Set default value to 1
        self.calc_quantity_input.valueChanged.connect(self.update_vat_calculation)
        quantity_layout.addWidget(quantity_label)
        quantity_layout.addWidget(self.calc_quantity_input)
        input_layout.addLayout(quantity_layout)
        
        calculator_layout.addLayout(input_layout)
        
        # Results
        results_layout = QGridLayout()
        results_layout.setVerticalSpacing(10)
        results_layout.setHorizontalSpacing(20)
        
        # Without VAT
        results_layout.addWidget(QLabel("Pret fara TVA:"), 0, 0)
        self.price_without_vat = QLabel("0.00 LEI")
        self.price_without_vat.setStyleSheet("font-weight: bold;")
        results_layout.addWidget(self.price_without_vat, 0, 1)
        
        # VAT amount
        results_layout.addWidget(QLabel("Valoare TVA (19%):"), 1, 0)
        self.vat_amount = QLabel("0.00 LEI")
        self.vat_amount.setStyleSheet("font-weight: bold;")
        results_layout.addWidget(self.vat_amount, 1, 1)
        
        # Total with VAT
        results_layout.addWidget(QLabel("Pret total cu TVA:"), 2, 0)
        self.total_with_vat = QLabel("0.00 LEI")
        self.total_with_vat.setStyleSheet("font-weight: bold; color: #2980B9;")
        results_layout.addWidget(self.total_with_vat, 2, 1)
        
        calculator_layout.addLayout(results_layout)
        layout.addWidget(calculator_frame)
        
        # Add Total Stock Value section
        stock_value_frame = ModernFrame()
        stock_value_layout = QVBoxLayout(stock_value_frame)
        
        stock_value_title = QLabel("Valoarea Totala a Stocului")
        stock_value_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2C3E50;")
        stock_value_layout.addWidget(stock_value_title)
        
        # Total values grid
        values_grid = QGridLayout()
        values_grid.setColumnStretch(1, 1)
        
        # Overall total
        values_grid.addWidget(QLabel("Valoare totala (cu TVA):"), 0, 0)
        self.home_total_value_label = QLabel()
        self.home_total_value_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2980B9;")
        values_grid.addWidget(self.home_total_value_label, 0, 1)
        
        values_grid.addWidget(QLabel("Valoare totala (fara TVA):"), 1, 0)
        self.home_total_value_no_vat_label = QLabel()
        self.home_total_value_no_vat_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2980B9;")
        values_grid.addWidget(self.home_total_value_no_vat_label, 1, 1)
        
        values_grid.addWidget(QLabel("TVA total:"), 2, 0)
        self.home_total_vat_label = QLabel()
        self.home_total_vat_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2980B9;")
        values_grid.addWidget(self.home_total_vat_label, 2, 1)
        
        stock_value_layout.addLayout(values_grid)
        layout.addWidget(stock_value_frame)
        
        layout.addStretch()
        return page
    
    def update_vat_calculation(self):
        price = self.calc_price_input.value()
        quantity = self.calc_quantity_input.value()
        is_price_with_vat = self.price_type_combo.currentText() == "Pret cu TVA"
        
        # Update price label based on selection
        self.price_label.setText("Pret cu TVA:" if is_price_with_vat else "Pret fara TVA:")
        
        if is_price_with_vat:
            # If price includes VAT, calculate backwards
            total_with_vat = price * quantity
            total_without_vat = total_with_vat / 1.19
            vat = total_with_vat - total_without_vat
        else:
            # If price is without VAT, calculate forward
            total_without_vat = price * quantity
            vat = total_without_vat * 0.19
            total_with_vat = total_without_vat + vat
        
        self.price_without_vat.setText(f"{total_without_vat:.2f} LEI")
        self.vat_amount.setText(f"{vat:.2f} LEI")
        self.total_with_vat.setText(f"{total_with_vat:.2f} LEI")
    
    def show_home_page(self):
        self.pages.setCurrentWidget(self.home_page)
        self.update_home_stats()
    
    def show_inventory_page(self):
        self.pages.setCurrentWidget(self.inventory_page)
    
    def show_orders_page(self):
        self.pages.setCurrentWidget(self.orders_page)
    
    def show_customers_page(self):
        self.pages.setCurrentWidget(self.customers_page)
    
    def show_suppliers_page(self):
        self.pages.setCurrentWidget(self.suppliers_page)
    
    def show_reports_page(self):
        self.pages.setCurrentWidget(self.reports_page)
    
    def update_home_stats(self):
        # Update low stock count
        low_stock_products = get_low_stock_products()
        self.low_stock_count.setText(str(len(low_stock_products)))
        
        # Update total products count
        all_products = get_all_products()
        self.total_products_count.setText(str(len(all_products)))
        
        # Calculate and update total stock value
        total_value = 0
        total_value_no_vat = 0
        for product in all_products:
            value = product.quantity * product.unit_price
            value_no_vat = value / 1.19
            total_value += value
            total_value_no_vat += value_no_vat
        
        self.home_total_value_label.setText(f"{total_value:.2f} LEI")
        self.home_total_value_no_vat_label.setText(f"{total_value_no_vat:.2f} LEI")
        self.home_total_vat_label.setText(f"{(total_value - total_value_no_vat):.2f} LEI")
    
    def create_inventory_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Top section with search and buttons
        top_frame = ModernFrame()
        top_layout = QVBoxLayout(top_frame)
        
        # Search bar
        search_layout = QHBoxLayout()
        search_label = QLabel("Cauta produse")
        search_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #212121;")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cauta dupa nume sau descriere...")
        self.search_input.setStyleSheet(STYLES['search_input'])
        self.search_input.textChanged.connect(self.search_products)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        top_layout.addLayout(search_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        add_btn = QPushButton("+ Adauga produs")
        add_btn.setStyleSheet(STYLES['button'] % (COLORS['primary'], '#1976D2', '#1565C0'))
        add_btn.clicked.connect(self.add_product)
        button_layout.addWidget(add_btn)
        
        edit_btn = QPushButton("Editeaza")
        edit_btn.setStyleSheet(STYLES['button'] % (COLORS['secondary'], '#EC407A', '#D81B60'))
        edit_btn.clicked.connect(self.edit_product)
        button_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("Sterge")
        delete_btn.setStyleSheet(STYLES['button'] % (COLORS['danger'], '#E53935', '#D32F2F'))
        delete_btn.clicked.connect(self.delete_product)
        button_layout.addWidget(delete_btn)
        
        history_btn = QPushButton("Istoric")
        history_btn.setStyleSheet(STYLES['button'] % (COLORS['primary'], '#1976D2', '#1565C0'))
        history_btn.clicked.connect(self.show_history)
        button_layout.addWidget(history_btn)
        
        button_layout.addStretch()
        
        export_combo = QComboBox()
        export_combo.addItems(["Export...", "Export in Excel", "Export in CSV"])
        export_combo.setStyleSheet(STYLES['combo_box'])
        export_combo.currentTextChanged.connect(self.handle_export)
        button_layout.addWidget(export_combo)
        
        top_layout.addLayout(button_layout)
        layout.addWidget(top_frame)
        
        # Product table
        table_frame = ModernFrame()
        table_layout = QVBoxLayout(table_frame)
        
        self.product_table = QTableWidget()
        self.product_table.setColumnCount(11)  # Updated column count
        self.product_table.setHorizontalHeaderLabels([
            "ID", "Nume", "Categorie", "Cantitate", "Unitate", "Pret unitar(LEI)",
            "Pret fara TVA", "Total cu TVA", "Total fara TVA", "Dimensiuni", "Prag minim"
        ])
        self.product_table.setStyleSheet(STYLES['table'])
        self.product_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.product_table.verticalHeader().setVisible(False)
        table_layout.addWidget(self.product_table)
        
        layout.addWidget(table_frame)
        
        return page
    
    def create_orders_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 20, 0, 0)
        
        frame = ModernFrame()
        frame_layout = QVBoxLayout(frame)
        
        # Add "Coming Soon" label with modern styling
        label = QLabel("Comenzi - In curand...")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet('''
            QLabel {
                font-size: 24px;
                color: #9E9E9E;
                font-weight: bold;
            }
        ''')
        frame_layout.addWidget(label)
        
        layout.addWidget(frame)
        return widget
    
    def create_customers_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 20, 0, 0)
        
        frame = ModernFrame()
        frame_layout = QVBoxLayout(frame)
        
        label = QLabel("Angajati - In curand...")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet('''
            QLabel {
                font-size: 24px;
                color: #9E9E9E;
                font-weight: bold;
            }
        ''')
        frame_layout.addWidget(label)
        
        layout.addWidget(frame)
        return widget
    
    def create_suppliers_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 20, 0, 0)
        
        frame = ModernFrame()
        frame_layout = QVBoxLayout(frame)
        
        label = QLabel("Furnizori - In curand...")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet('''
            QLabel {
                font-size: 24px;
                color: #9E9E9E;
                font-weight: bold;
            }
        ''')
        frame_layout.addWidget(label)
        
        layout.addWidget(frame)
        return widget
    
    def create_reports_page(self):
        return ReportsPage()

    def refresh_table(self):
        self.product_table.setRowCount(0)
        products = get_all_products()
        
        for product in products:
            row = self.product_table.rowCount()
            self.product_table.insertRow(row)
            
            # Calculate prices
            price_without_vat = product.unit_price / 1.19
            total_with_vat = product.unit_price * product.quantity
            total_without_vat = price_without_vat * product.quantity
            
            # Format dimensions if they exist
            dimensions = ""
            if product.width and product.height:
                if product.width < 1 and product.height < 1:
                    # Convert to cm if in meters and less than 1
                    dimensions = f"{product.width * 100:.1f} x {product.height * 100:.1f} cm"
                else:
                    dimensions = f"{product.width:.2f} x {product.height:.2f} m"
            
            # Create items with styling
            items = [
                QTableWidgetItem(str(product.id)),
                QTableWidgetItem(product.name),
                QTableWidgetItem(product.category.name if product.category else ""),
                QTableWidgetItem(str(product.quantity)),
                QTableWidgetItem(product.measure_unit.value),
                QTableWidgetItem(f"{product.unit_price:.2f} LEI"),
                QTableWidgetItem(f"{price_without_vat:.2f} LEI"),
                QTableWidgetItem(f"{total_with_vat:.2f} LEI"),
                QTableWidgetItem(f"{total_without_vat:.2f} LEI"),
                QTableWidgetItem(dimensions),
                QTableWidgetItem(str(product.alert_threshold))
            ]
            
            # Apply styling and set items
            for col, item in enumerate(items):
                item.setTextAlignment(Qt.AlignCenter)
                if col == 3 and product.quantity <= product.alert_threshold:
                    item.setForeground(QColor(COLORS['danger']))
                    item.setFont(QFont("", -1, QFont.Bold))
                # Highlight total columns
                if col in [7, 8]:  # Total columns
                    item.setBackground(QColor("#E3F2FD"))
                self.product_table.setItem(row, col, item)
    
    def search_products(self):
        search_term = self.search_input.text()
        self.product_table.setRowCount(0)
        
        if search_term:
            products = search_products(search_term)
        else:
            products = get_all_products()
        
        for product in products:
            row = self.product_table.rowCount()
            self.product_table.insertRow(row)
            
            # Calculate prices
            price_without_vat = product.unit_price / 1.19
            total_with_vat = product.unit_price * product.quantity
            total_without_vat = price_without_vat * product.quantity
            
            # Format dimensions if they exist
            dimensions = ""
            if product.width and product.height:
                if product.width < 1 and product.height < 1:
                    # Convert to cm if in meters and less than 1
                    dimensions = f"{product.width * 100:.1f} x {product.height * 100:.1f} cm"
                else:
                    dimensions = f"{product.width:.2f} x {product.height:.2f} m"
            
            items = [
                QTableWidgetItem(str(product.id)),
                QTableWidgetItem(product.name),
                QTableWidgetItem(product.category.name if product.category else ""),
                QTableWidgetItem(str(product.quantity)),
                QTableWidgetItem(product.measure_unit.value),
                QTableWidgetItem(f"{product.unit_price:.2f} LEI"),
                QTableWidgetItem(f"{price_without_vat:.2f} LEI"),
                QTableWidgetItem(f"{total_with_vat:.2f} LEI"),
                QTableWidgetItem(f"{total_without_vat:.2f} LEI"),
                QTableWidgetItem(dimensions),
                QTableWidgetItem(str(product.alert_threshold))
            ]
            
            for col, item in enumerate(items):
                item.setTextAlignment(Qt.AlignCenter)
                if col == 3 and product.quantity <= product.alert_threshold:
                    item.setForeground(QColor(COLORS['danger']))
                    item.setFont(QFont("", -1, QFont.Bold))
                # Highlight total columns
                if col in [7, 8]:  # Total columns
                    item.setBackground(QColor("#E3F2FD"))
                self.product_table.setItem(row, col, item)
    
    def add_product(self):
        dialog = ProductDialog(self)
        if dialog.exec_():
            name, quantity, price, unit, category_id, supplier_id, material_type, width, height, description, threshold = dialog.get_values()
            add_product(
                name=name,
                quantity=quantity,
                unit_price=price,
                measure_unit=unit,
                category_id=category_id,
                supplier_id=supplier_id,
                description=description,
                alert_threshold=threshold,
                width=width,
                height=height,
                material_type=material_type
            )
            self.refresh_table()
    
    def edit_product(self):
        current_row = self.product_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Atentie", "Va rugam selectati un produs pentru editare.")
            return
        
        product_id = int(self.product_table.item(current_row, 0).text())
        product = get_product_by_id(product_id)
        
        if not product:
            QMessageBox.warning(self, "Eroare", "Produsul nu a fost gasit.")
            return
        
        dialog = ProductDialog(self, product)
        if dialog.exec_():
            name, quantity, price, unit, category_id, supplier_id, material_type, width, height, description, threshold = dialog.get_values()
            update_product(
                product_id,
                name=name,
                quantity=quantity,
                unit_price=price,
                measure_unit=unit,
                category_id=category_id,
                supplier_id=supplier_id,
                material_type=material_type,
                width=width,
                height=height,
                description=description,
                alert_threshold=threshold
            )
            self.refresh_table()
    
    def delete_product(self):
        current_row = self.product_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Atentie", "Va rugam selectati un produs pentru stergere.")
            return
        
        product_id = int(self.product_table.item(current_row, 0).text())
        product_name = self.product_table.item(current_row, 1).text()
        
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(f"Sunteti sigur ca doriti sa stergeti {product_name}?")
        msg.setWindowTitle("Confirmare stergere")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.button(QMessageBox.Yes).setText("Da")
        msg.button(QMessageBox.No).setText("Nu")
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
            }
            QPushButton[text="Da"] {
                background-color: #F44336;
            }
            QPushButton[text="Nu"] {
                background-color: #9E9E9E;
            }
        ''')
        
        if msg.exec_() == QMessageBox.Yes:
            delete_product(product_id)
            self.refresh_table()
    
    def handle_export(self, option):
        if option == "Export in Excel":
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export in Excel", "", "Excel Files (*.xlsx)")
            if filename:
                if not filename.endswith('.xlsx'):
                    filename += '.xlsx'
                export_to_excel(filename)
                QMessageBox.information(self, "Succes", "Datele au fost exportate cu succes!")
        elif option == "Export in CSV":
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export in CSV", "", "CSV Files (*.csv)")
            if filename:
                if not filename.endswith('.csv'):
                    filename += '.csv'
                export_to_csv(filename)
                QMessageBox.information(self, "Succes", "Datele au fost exportate cu succes!")
    
    def check_low_stock(self):
        low_stock_products = get_low_stock_products()
        if low_stock_products:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Alerta stoc redus")
            
            message = "Urmatoarele produse au stocul redus:\n\n"
            for product in low_stock_products:
                message += f"• {product.name} (Cantitate: {product.quantity})\n"
            
            msg.setText(message)
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
    
    def load_initial_data(self):
        self.refresh_table()
        
        # Set up low stock alert timer
        self.alert_timer = QTimer()
        self.alert_timer.timeout.connect(self.check_low_stock)
        self.alert_timer.start(300000)  # Check every 5 minutes

    def show_history(self):
        current_row = self.product_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Atentie", "Va rugam selectati un produs pentru a vedea istoricul.")
            return
        
        product_id = int(self.product_table.item(current_row, 0).text())
        dialog = HistoryDialog(product_id, self)
        dialog.exec_()

    def show_about_dialog(self):
        dialog = AboutDialog(self)
        dialog.exec_()

class ProductDialog(QDialog):
    def __init__(self, parent=None, product=None):
        super().__init__(parent)
        self.product = product
        self.setWindowTitle("Adauga produs" if not product else "Editeaza produs")
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
        
        # Product Details Frame
        details_frame = ModernFrame()
        details_layout = QVBoxLayout(details_frame)
        
        # Title
        title = QLabel("Detalii produs")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #212121; margin-bottom: 10px;")
        details_layout.addWidget(title)
        
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
        
        details_layout.addLayout(form_layout1)
        
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
        
        details_layout.addLayout(form_layout2)
        
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
        self.price_input.setSuffix(" LEI")
        self.price_input.valueChanged.connect(self.update_vat_calculation)
        price_layout.addWidget(price_label)
        price_layout.addWidget(self.price_input)
        form_layout3.addLayout(price_layout)
        
        details_layout.addLayout(form_layout3)
        
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
        details_layout.addLayout(dimensions_layout)
        
        # Description
        description_label = QLabel("Descriere:")
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        details_layout.addWidget(description_label)
        details_layout.addWidget(self.description_input)
        
        # Alert Threshold
        threshold_layout = QHBoxLayout()
        threshold_label = QLabel("Prag minim:")
        self.threshold_input = QSpinBox()
        self.threshold_input.setMaximum(999999)
        threshold_layout.addWidget(threshold_label)
        threshold_layout.addWidget(self.threshold_input)
        threshold_layout.addStretch()
        details_layout.addLayout(threshold_layout)
        
        layout.addWidget(details_frame)
        
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

class ReportsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        # Create main widget for scroll area
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(30)
        
        # Title
        title = QLabel("Rapoarte si Statistici")
        title.setStyleSheet('''
            font-size: 28px;
            font-weight: bold;
            color: #2C3E50;
            margin-bottom: 20px;
        ''')
        scroll_layout.addWidget(title)
        
        # 1. Stock Overview Section
        overview_frame = ModernFrame()
        overview_layout = QVBoxLayout(overview_frame)
        
        overview_title = QLabel("Privire de Ansamblu asupra Stocului")
        overview_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2C3E50;")
        overview_layout.addWidget(overview_title)
        
        # Overview statistics grid
        stats_grid = QGridLayout()
        stats_grid.setColumnStretch(1, 1)
        
        # Total number of products
        stats_grid.addWidget(QLabel("Numar total de produse:"), 0, 0)
        self.total_products_label = QLabel()
        self.total_products_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2980B9;")
        stats_grid.addWidget(self.total_products_label, 0, 1)
        
        # Products below threshold
        stats_grid.addWidget(QLabel("Produse sub prag minim:"), 1, 0)
        self.low_stock_count_label = QLabel()
        self.low_stock_count_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #E74C3C;")
        stats_grid.addWidget(self.low_stock_count_label, 1, 1)
        
        # Average product price
        stats_grid.addWidget(QLabel("Pret mediu per produs:"), 2, 0)
        self.avg_price_label = QLabel()
        self.avg_price_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2980B9;")
        stats_grid.addWidget(self.avg_price_label, 2, 1)
        
        # Most expensive product
        stats_grid.addWidget(QLabel("Cel mai scump produs:"), 3, 0)
        self.most_expensive_label = QLabel()
        self.most_expensive_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2980B9;")
        stats_grid.addWidget(self.most_expensive_label, 3, 1)
        
        # Least expensive product
        stats_grid.addWidget(QLabel("Cel mai ieftin produs:"), 4, 0)
        self.least_expensive_label = QLabel()
        self.least_expensive_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2980B9;")
        stats_grid.addWidget(self.least_expensive_label, 4, 1)
        
        overview_layout.addLayout(stats_grid)
        scroll_layout.addWidget(overview_frame)
        
        # 2. Total Stock Value Section
        stock_value_frame = ModernFrame()
        stock_value_layout = QVBoxLayout(stock_value_frame)
        
        stock_value_title = QLabel("Valoarea Totala a Stocului")
        stock_value_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2C3E50;")
        stock_value_layout.addWidget(stock_value_title)
        
        # Total values grid
        values_grid = QGridLayout()
        values_grid.setColumnStretch(1, 1)
        
        # Overall total
        values_grid.addWidget(QLabel("Valoare totala (cu TVA):"), 0, 0)
        self.total_value_label = QLabel()
        self.total_value_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2980B9;")
        values_grid.addWidget(self.total_value_label, 0, 1)
        
        values_grid.addWidget(QLabel("Valoare totala (fara TVA):"), 1, 0)
        self.total_value_no_vat_label = QLabel()
        self.total_value_no_vat_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2980B9;")
        values_grid.addWidget(self.total_value_no_vat_label, 1, 1)
        
        values_grid.addWidget(QLabel("TVA total:"), 2, 0)
        self.total_vat_label = QLabel()
        self.total_vat_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2980B9;")
        values_grid.addWidget(self.total_vat_label, 2, 1)
        
        stock_value_layout.addLayout(values_grid)
        
        # Category distribution with progress bars
        categories_frame = QFrame()
        self.categories_layout = QVBoxLayout(categories_frame)
        self.categories_layout.setSpacing(10)
        
        categories_title = QLabel("Distributia Valorii Stocului pe Categorii")
        categories_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2C3E50;")
        self.categories_layout.addWidget(categories_title)
        
        self.category_bars = {}  # Store progress bars for each category
        stock_value_layout.addWidget(categories_frame)
        
        scroll_layout.addWidget(stock_value_frame)
        
        # 3. Low Stock Products Section
        low_stock_frame = ModernFrame()
        low_stock_layout = QVBoxLayout(low_stock_frame)
        
        low_stock_header = QHBoxLayout()
        low_stock_title = QLabel("Produse cu Stoc Redus")
        low_stock_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2C3E50;")
        low_stock_header.addWidget(low_stock_title)
        
        restock_btn = QPushButton("Genereaza Comanda de Aprovizionare")
        restock_btn.setStyleSheet(STYLES['button'] % (COLORS['warning'], '#FFA000', '#FF8F00'))
        restock_btn.clicked.connect(self.generate_restock_order)
        low_stock_header.addWidget(restock_btn)
        
        low_stock_layout.addLayout(low_stock_header)
        
        # Low stock table
        self.low_stock_table = QTableWidget()
        self.low_stock_table.setColumnCount(5)
        self.low_stock_table.setHorizontalHeaderLabels([
            "Nume", "Categorie", "Stoc Actual", "Prag Minim", "Necesar"
        ])
        self.low_stock_table.setStyleSheet(STYLES['table'])
        self.low_stock_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        low_stock_layout.addWidget(self.low_stock_table)
        
        # Low stock visualization with progress bars
        low_stock_viz_frame = QFrame()
        self.low_stock_viz_layout = QVBoxLayout(low_stock_viz_frame)
        
        low_stock_viz_title = QLabel("Distributia Produselor cu Stoc Redus")
        low_stock_viz_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2C3E50;")
        self.low_stock_viz_layout.addWidget(low_stock_viz_title)
        
        self.low_stock_bars = {}  # Store progress bars for low stock
        low_stock_layout.addWidget(low_stock_viz_frame)
        
        scroll_layout.addWidget(low_stock_frame)
        
        # 4. Average Prices Section
        prices_frame = ModernFrame()
        prices_layout = QVBoxLayout(prices_frame)
        
        prices_title = QLabel("Preturi Medii per Categorie")
        prices_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2C3E50;")
        prices_layout.addWidget(prices_title)
        
        # Average prices table
        self.prices_table = QTableWidget()
        self.prices_table.setColumnCount(4)
        self.prices_table.setHorizontalHeaderLabels([
            "Categorie", "Pret Mediu", "Pret Minim", "Pret Maxim"
        ])
        self.prices_table.setStyleSheet(STYLES['table'])
        self.prices_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        prices_layout.addWidget(self.prices_table)
        
        scroll_layout.addWidget(prices_frame)
        
        # Set scroll widget and add to layout
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
    
    def load_data(self):
        products = get_all_products()
        categories = {}  # For category-based calculations
        
        total_value = 0
        total_value_no_vat = 0
        all_prices = []
        
        # Process products
        for product in products:
            value = product.quantity * product.unit_price
            value_no_vat = value / 1.19
            total_value += value
            total_value_no_vat += value_no_vat
            all_prices.append((product.name, product.unit_price))
            
            # Group by category
            category_name = product.category.name if product.category else "Fara categorie"
            if category_name not in categories:
                categories[category_name] = {
                    'value': 0,
                    'value_no_vat': 0,
                    'products': [],
                    'prices': []
                }
            
            categories[category_name]['value'] += value
            categories[category_name]['value_no_vat'] += value_no_vat
            categories[category_name]['products'].append(product)
            categories[category_name]['prices'].append(product.unit_price)
        
        # Update overview statistics
        self.total_products_label.setText(str(len(products)))
        self.low_stock_count_label.setText(str(len([p for p in products if p.quantity <= p.alert_threshold])))
        
        if all_prices:
            avg_price = sum(price for _, price in all_prices) / len(all_prices)
            self.avg_price_label.setText(f"{avg_price:.2f} LEI")
            
            most_expensive = max(all_prices, key=lambda x: x[1])
            least_expensive = min(all_prices, key=lambda x: x[1])
            
            self.most_expensive_label.setText(f"{most_expensive[0]} ({most_expensive[1]:.2f} LEI)")
            self.least_expensive_label.setText(f"{least_expensive[0]} ({least_expensive[1]:.2f} LEI)")
        else:
            self.avg_price_label.setText("0.00 LEI")
            self.most_expensive_label.setText("N/A")
            self.least_expensive_label.setText("N/A")
        
        # Update total values
        self.total_value_label.setText(f"{total_value:.2f} LEI")
        self.total_value_no_vat_label.setText(f"{total_value_no_vat:.2f} LEI")
        self.total_vat_label.setText(f"{(total_value - total_value_no_vat):.2f} LEI")
        
        # Create category value chart
        self.update_category_chart(categories)
        
        # Update low stock table and chart
        self.update_low_stock_section(products, categories)
        
        # Update average prices table
        self.update_prices_table(categories)
    
    def update_category_chart(self, categories):
        # Clear existing progress bars
        for widget in self.category_bars.values():
            widget.setParent(None)
        self.category_bars.clear()
        
        # Calculate total value for percentage
        total_value = sum(data['value'] for data in categories.values())
        if total_value == 0:
            return
            
        # Create progress bar for each category
        for category, data in categories.items():
            percentage = (data['value'] / total_value) * 100
            
            container = QWidget()
            container_layout = QHBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            
            label = QLabel(f"{category}:")
            label.setMinimumWidth(150)
            container_layout.addWidget(label)
            
            progress = QProgressBar()
            progress.setMaximum(100)
            progress.setValue(int(percentage))
            progress.setFormat(f"{percentage:.1f}% ({data['value']:.2f} LEI)")
            progress.setStyleSheet('''
                QProgressBar {
                    border: 2px solid #E0E0E0;
                    border-radius: 5px;
                    text-align: center;
                    height: 25px;
                    font-size: 14px;
                }
                QProgressBar::chunk {
                    background-color: #2196F3;
                    border-radius: 3px;
                }
            ''')
            container_layout.addWidget(progress)
            
            self.category_bars[category] = container
            self.categories_layout.addWidget(container)
    
    def update_low_stock_section(self, products, categories):
        # Update table as before
        self.low_stock_table.setRowCount(0)
        low_stock_products = [p for p in products if p.quantity <= p.alert_threshold]
        
        for product in low_stock_products:
            row = self.low_stock_table.rowCount()
            self.low_stock_table.insertRow(row)
            
            category = product.category.name if product.category else "Fara categorie"
            needed = product.alert_threshold - product.quantity
            
            items = [
                QTableWidgetItem(product.name),
                QTableWidgetItem(category),
                QTableWidgetItem(str(product.quantity)),
                QTableWidgetItem(str(product.alert_threshold)),
                QTableWidgetItem(str(needed))
            ]
            
            for col, item in enumerate(items):
                item.setTextAlignment(Qt.AlignCenter)
                self.low_stock_table.setItem(row, col, item)
        
        # Clear existing progress bars
        for widget in self.low_stock_bars.values():
            widget.setParent(None)
        self.low_stock_bars.clear()
        
        # Count low stock by category
        low_stock_by_category = {}
        for product in low_stock_products:
            category = product.category.name if product.category else "Fara categorie"
            low_stock_by_category[category] = low_stock_by_category.get(category, 0) + 1
        
        # Calculate total for percentage
        total_low_stock = len(low_stock_products)
        if total_low_stock == 0:
            return
            
        # Create progress bar for each category
        for category, count in low_stock_by_category.items():
            percentage = (count / total_low_stock) * 100
            
            container = QWidget()
            container_layout = QHBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            
            label = QLabel(f"{category}:")
            label.setMinimumWidth(150)
            container_layout.addWidget(label)
            
            progress = QProgressBar()
            progress.setMaximum(100)
            progress.setValue(int(percentage))
            progress.setFormat(f"{percentage:.1f}% ({count} produse)")
            progress.setStyleSheet('''
                QProgressBar {
                    border: 2px solid #E0E0E0;
                    border-radius: 5px;
                    text-align: center;
                    height: 25px;
                    font-size: 14px;
                }
                QProgressBar::chunk {
                    background-color: #E74C3C;
                    border-radius: 3px;
                }
            ''')
            container_layout.addWidget(progress)
            
            self.low_stock_bars[category] = container
            self.low_stock_viz_layout.addWidget(container)
    
    def update_prices_table(self, categories):
        self.prices_table.setRowCount(0)
        for category, data in categories.items():
            if not data['prices']:
                continue
                
            row = self.prices_table.rowCount()
            self.prices_table.insertRow(row)
            
            avg_price = sum(data['prices']) / len(data['prices'])
            min_price = min(data['prices'])
            max_price = max(data['prices'])
            
            items = [
                QTableWidgetItem(category),
                QTableWidgetItem(f"{avg_price:.2f} LEI"),
                QTableWidgetItem(f"{min_price:.2f} LEI"),
                QTableWidgetItem(f"{max_price:.2f} LEI")
            ]
            
            for col, item in enumerate(items):
                item.setTextAlignment(Qt.AlignCenter)
                self.prices_table.setItem(row, col, item)
    
    def generate_restock_order(self):
        # This is a placeholder for future implementation
        QMessageBox.information(
            self,
            "Info",
            "Functionalitatea de generare a comenzilor de aprovizionare va fi disponibila in curand!"
        )

    def create_reports_page(self):
        return ReportsPage() 