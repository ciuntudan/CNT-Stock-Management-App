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