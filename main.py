import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from ui.main_window import MainWindow
from database.models import init_db
from utils.pdf_generator import generate_invoice_pdf

def main():
    # Create database directory if it doesn't exist
    os.makedirs('database', exist_ok=True)
    
    # Initialize database
    init_db()
    
    # Create and start application
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("favicon.png"))  # Set application-wide icon
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 