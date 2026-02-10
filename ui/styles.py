# IronVault Dark Theme (Obsidian-inspired)

# Color Palette
# Background: #1e1e1e
# Sidebar: #252526
# Card Bg: #2d2d2d
# Accent: #7f5af0 (Purple)
# Text Main: #e0e0e0
# Text Muted: #858585
# Border: #3e3e3e

DARK_THEME_QSS = """
/* --- Global Reset --- */
QWidget {
    background-color: #1e1e1e;
    color: #e0e0e0;
    font-family: 'Segoe UI', 'Roboto', sans-serif;
    font-size: 14px;
}

/* --- Main Window --- */
QMainWindow {
    background-color: #1e1e1e;
}

/* --- Sidebar (QListWidget) --- */
QListWidget {
    background-color: #252526;
    border: none;
    border-right: 1px solid #333333;
    outline: 0;
    padding-top: 10px; /* Reduced from 20px */
}

QListWidget::item {
    height: 36px; /* Reduced from 48px */
    padding-left: 12px;
    color: #a0a0a0;
    border: none;
    margin: 2px 8px; /* Reduced margin */
    border-radius: 4px;
}

QListWidget::item:selected {
    background-color: #37373d;
    color: #ffffff;
}

QListWidget::item:hover {
    background-color: #2a2d2e;
    color: #ffffff;
}

/* --- Buttons --- */
QPushButton {
    background-color: #2d2d2d;
    border: 1px solid #3e3e3e;
    border-radius: 4px;
    padding: 6px 12px; /* Reduced padding */
    color: #cccccc;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #3e3e3e;
    border-color: #555555;
    color: #ffffff;
}

QPushButton:pressed {
    background-color: #7f5af0;
    border-color: #7f5af0;
    color: #ffffff;
}

/* Primary Action Button Style */
QPushButton#PrimaryBtn {
    background-color: #7f5af0;
    color: #ffffff;
    border: none;
}
QPushButton#PrimaryBtn:hover {
    background-color: #7251d8;
}

/* --- Input Fields --- */
QLineEdit {
    background-color: #2d2d2d;
    border: 1px solid #3e3e3e;
    border-radius: 4px;
    padding: 6px 8px; /* Reduced padding */
    color: #ffffff;
    font-size: 13px; /* Slightly smaller font */
}

QLineEdit:focus {
    border: 1px solid #7f5af0;
    background-color: #323232;
}

/* --- Scroll Area & Bars --- */
QScrollArea {
    border: none;
    background-color: #1e1e1e;
}

QScrollBar:vertical {
    background: #1e1e1e;
    width: 10px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #424242;
    min-height: 30px;
    border-radius: 5px;
    margin: 1px;
}
QScrollBar::handle:vertical:hover {
    background: #505050;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* --- Cards (Custom Widget: PasswordCard) --- */
QFrame#PasswordCard {
    background-color: #252526;
    border: 1px solid #333333;
    border-radius: 6px;
}

QFrame#PasswordCard:hover {
    background-color: #2d2d2d;
    border: 1px solid #7f5af0;
}

QLabel#CardTitle {
    font-size: 14px; /* Reduced from 16px */
    font-weight: 700;
    color: #ffffff;
    margin-top: 4px;
}

QLabel#CardCategory {
    font-size: 11px; /* Reduced from 12px */
    font-weight: 500;
    color: #858585;
    background-color: #1e1e1e;
    padding: 2px 6px;
    border-radius: 8px;
}

/* --- Login Dialog Specifics --- */
QLabel#LoginTitle {
    font-size: 20px;
    font-weight: bold;
    margin-bottom: 10px;
}

"""
