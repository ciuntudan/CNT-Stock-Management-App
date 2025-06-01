# Print Products Stock Management System

A desktop application for managing stock of custom print products built with PyQt5.

## Features

- Modern and intuitive user interface
- Product management (add, edit, delete)
- Stock tracking with low stock alerts
- Search and filter functionality
- Export to Excel/CSV
- Local SQLite database storage

## Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

## Project Structure

- `main.py` - Application entry point
- `database/` - Database models and operations
- `ui/` - UI related files and layouts
- `utils/` - Utility functions
- `resources/` - Application resources 