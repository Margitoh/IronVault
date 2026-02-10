from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QWidget, QHBoxLayout, QGraphicsDropShadowEffect
from PySide6.QtGui import QIcon
from core.utils import resource_path
from PySide6.QtCore import Qt, Signal, QThread, QObject
from database.db_manager import DBManager

class LoginWorker(QObject):
    finished = Signal(object) # Emit (success_bool, result_or_error)
    
    def __init__(self, db_path, password, is_new_vault):
        super().__init__()
        self.db_path = db_path
        self.password = password
        self.is_new_vault = is_new_vault

    def run(self):
        # Create a thread-local DBManager
        # SQLite connections cannot be shared across threads
        local_db = DBManager(self.db_path)
        
        try:
            if self.is_new_vault:
                # Initialize
                success, error = local_db.initialize_vault(self.password)
                if success:
                    # Auto-login
                    derived_key = local_db.verify_password(self.password)
                    self.finished.emit((True, derived_key))
                else:
                    self.finished.emit((False, f"Failed to create vault: {error}"))
            else:
                # Login
                derived_key = local_db.verify_password(self.password)
                if derived_key:
                    self.finished.emit((True, derived_key))
                else:
                    self.finished.emit((False, "Incorrect Master Password."))
        except Exception as e:
            self.finished.emit((False, str(e)))
        finally:
            # Explicitly close to be safe, though GC handles it
            if local_db.conn:
                local_db.conn.close()

class LoginDialog(QDialog):
    loginSuccessful = Signal(bytes)

    def __init__(self, security_manager):
        super().__init__()
        self.db_manager = security_manager
        self.setWindowTitle("Login - IronVault")
        self.setFixedSize(400, 250)
        self.setWindowIcon(QIcon(resource_path("ironvault.ico")))
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint) 
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.is_new_vault = self.db_manager.is_new_vault()
        self.key = None

        # Main Layout Container
        self.container = QWidget(self)
        self.container.setObjectName("LoginContainer")
        self.container.setGeometry(10, 10, 340, 240) 
        self.container.setStyleSheet("""
            QWidget#LoginContainer {
                background-color: #252526;
                border: 1px solid #333;
                border-radius: 12px;
            }
        """)

        # Add Shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(Qt.black)
        self.container.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self.container)
        layout.setSpacing(10)
        layout.setContentsMargins(30, 25, 30, 25)

        # Title & Subtitle
        if self.is_new_vault:
            title_text = "Create Master Password"
            subtitle_text = "This password will encrypt your vault.\nIf you lose it, your data is gone forever."
            btn_text = "Create Vault"
        else:
            title_text = "Unlock Vault"
            subtitle_text = "Enter your Master Password to access."
            btn_text = "Unlock"

        title_label = QLabel(title_text)
        title_label.setObjectName("LoginTitle") 
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #fff;")
        layout.addWidget(title_label)

        sub_label = QLabel(subtitle_text)
        sub_label.setAlignment(Qt.AlignCenter)
        sub_label.setWordWrap(True)
        sub_label.setStyleSheet("font-size: 12px; color: #aaa; margin-bottom: 10px;")
        layout.addWidget(sub_label)

        # Password Input
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter Password")
        self.password_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #444;       
                border-radius: 4px;
                padding: 8px 12px;
                background: #1e1e1e;
                color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #7f5af0;
            }
        """)
        self.password_input.returnPressed.connect(self.attempt_login)
        layout.addWidget(self.password_input)

        # Buttons Layout
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        # Exit Button
        self.exit_btn = QPushButton("Exit")
        self.exit_btn.setCursor(Qt.PointingHandCursor)
        self.exit_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #888;
                border: none;
                font-weight: 600;
            }
            QPushButton:hover { color: #fff; }
        """)
        self.exit_btn.clicked.connect(self.reject)
        
        # Action Button
        self.unlock_btn = QPushButton(btn_text)
        self.unlock_btn.setCursor(Qt.PointingHandCursor)
        self.unlock_btn.setObjectName("PrimaryBtn")
        self.unlock_btn.setStyleSheet("""
            QPushButton {
                background-color: #7f5af0;
                color: white;
                border-radius: 4px;
                padding: 8px 24px;
                font-size: 14px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover { background-color: #6a46cd; }
            QPushButton:pressed { background-color: #5a36bd; }
        """)
        self.unlock_btn.clicked.connect(self.attempt_login)

        btn_layout.addWidget(self.exit_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.unlock_btn)

        layout.addLayout(btn_layout)

    def attempt_login(self):
        password = self.password_input.text()
        if not password:
            return

        # UI State: Processing
        self.password_input.setEnabled(False)
        self.unlock_btn.setText("...")
        self.unlock_btn.setEnabled(False)
        self.exit_btn.setEnabled(False)
        
        # Start Thread
        self.thread = QThread()
        # Pass db_path (str) instead of the object, so worker can create its own connection
        self.worker = LoginWorker(self.db_manager.db_path, password, self.is_new_vault)
        self.worker.moveToThread(self.thread)
        
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_login_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        self.thread.start()

    def on_login_finished(self, result):
        success, data = result
        
        # Restore UI State
        self.password_input.setEnabled(True)
        # Reset text based on mode
        self.unlock_btn.setText("Create Vault" if self.is_new_vault else "Unlock")
        self.unlock_btn.setEnabled(True)
        self.exit_btn.setEnabled(True)

        if success:
            derived_key = data
            self.key = derived_key
            self.loginSuccessful.emit(derived_key)
            self.accept()
        else:
            error_msg = data
            if self.is_new_vault:
                QMessageBox.critical(self, "Error", error_msg)
            else:
                 # Shake animation or red border could go here
                 self.password_input.setStyleSheet(self.password_input.styleSheet().replace("#444", "#ff4444"))
                 QMessageBox.warning(self, "Access Denied", error_msg)
                 self.password_input.setFocus()
                 self.password_input.selectAll()

