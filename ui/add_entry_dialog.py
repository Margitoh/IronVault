from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, 
                               QPushButton, QHBoxLayout, QComboBox, QMessageBox, QTextEdit)
from PySide6.QtCore import Qt

from PySide6.QtGui import QIcon

from PySide6.QtGui import QIcon
from core.utils import resource_path

class AddEntryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Item")
        self.setFixedSize(500, 720) # Increased height
        self.setWindowIcon(QIcon(resource_path("ironvault.ico"))) # Icon Fix
        
        # Modern Dark Theme Stylesheet
        self.setStyleSheet("""
            QDialog {
                background-color: #202020;
                color: #e0e0e0;
            }
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #eeeeee;
                margin-top: 5px;
            }
            QLineEdit, QComboBox, QTextEdit {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 6px;
                padding: 10px 12px;
                color: #ffffff;
                font-size: 14px;
            }
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
                border: 1px solid #7f5af0;
                background-color: #333333;
            }
            /* Styling the drop-down list view */
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                border: 1px solid #3e3e3e;
                selection-background-color: #7f5af0;
                color: #ffffff;
            }
            QPushButton {
                background-color: #7f5af0;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #6a46cd;
            }
            QPushButton:pressed {
                background-color: #5835b0;
            }
            QPushButton#CancelBtn {
                background-color: transparent;
                border: 1px solid #555555;
                color: #cccccc;
            }
            QPushButton#CancelBtn:hover {
                color: #ffffff;
                border-color: #ffffff;
                background-color: rgba(255, 255, 255, 0.05);
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)

        # Title
        layout.addWidget(QLabel("Title (e.g. Netflix)"))
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Service Name")
        layout.addWidget(self.title_input)

        # Category
        layout.addWidget(QLabel("Category"))
        self.category_input = QComboBox()
        self.category_input.addItems(["Personal", "Work", "Social", "Finance", "Shopping", "Entertainment", "Utilities", "Other"])
        self.category_input.setEditable(True) # Allow custom categories
        layout.addWidget(self.category_input)

        # Username
        layout.addWidget(QLabel("Username"))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("username123")
        layout.addWidget(self.username_input)

        # Email
        layout.addWidget(QLabel("Email"))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("user@example.com")
        layout.addWidget(self.email_input)

        # Password
        layout.addWidget(QLabel("Password"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Secret Password")
        layout.addWidget(self.password_input)

        # Note
        layout.addWidget(QLabel("Note (Optional)"))
        self.note_input = QTextEdit()
        self.note_input.setPlaceholderText("Additional details...")
        self.note_input.setFixedHeight(80) 
        layout.addWidget(self.note_input)

        layout.addStretch()

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15) # Spacing between buttons
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("CancelBtn")
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.clicked.connect(self.reject)
        
        self.save_btn = QPushButton("Save Item")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.clicked.connect(self.validate_and_accept)

        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)
        layout.addLayout(btn_layout)

    def validate_and_accept(self):
        if not self.title_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Title is required!")
            return
        # Removed password requirement check as user might just want to store a note or key
        # But usually password manager needs password. Let's keep it but maybe lenient?
        # User said "let me enter...". I'll keep it required for now.
        if not self.password_input.text():
            QMessageBox.warning(self, "Validation Error", "Password is required!")
            return
        self.accept()

    def get_data(self):
        return {
            "title": self.title_input.text().strip(),
            "category": self.category_input.currentText().strip(),
            "username": self.username_input.text().strip(),
            "email": self.email_input.text().strip(),
            "password": self.password_input.text(),
            "note": self.note_input.toPlainText()
        }
