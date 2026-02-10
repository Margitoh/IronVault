from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                               QListWidget, QListWidgetItem, QLineEdit, 
                               QScrollArea, QGridLayout, QLabel, QFrame, QPushButton, QMessageBox, QMenu, QMenuBar, QFileDialog, QInputDialog)
from PySide6.QtCore import Qt,  Signal
from PySide6.QtGui import QIcon, QClipboard, QGuiApplication, QAction
from ui.add_entry_dialog import AddEntryDialog
from ui.settings_dialog import SettingsDialog


from core.security import SecurityManager
from core.backup_manager import BackupManager # Changed import
import json
import csv
import os
from PySide6.QtCore import QThread, Signal # Added imports

class PasswordCard(QFrame):
    copyRequested = Signal(object) # Emit (ciphertext, nonce)
    deleteRequested = Signal(str) # Emit uuid
    editRequested = Signal(object) # Emit full entry data

    def __init__(self, uuid, title, category, username, email, ciphertext, nonce, password, note):
        super().__init__()
        self.uuid = uuid
        self.ciphertext = ciphertext
        self.nonce = nonce
        self.full_data = {
            "uuid": uuid,
            "title": title,
            "category": category,
            "username": username,
            "email": email,
            "ciphertext": ciphertext,
            "nonce": nonce,
            "password": password,
            "note": note
        }

        self.setObjectName("PasswordCard")
        # Dynamic height based on content? Fixed for now, but slightly taller.
        self.setFixedSize(220, 180) 
        
        # Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(5)
        
        # Icon (Top Left) or Centered? Let's keep it clean.
        # layout.addWidget(QLabel("🔒"), alignment=Qt.AlignCenter)

        # Title
        self.title_label = QLabel(title)
        self.title_label.setObjectName("CardTitle")
        self.title_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.title_label)
        
        # Category Badge
        cat_container = QWidget()
        cat_layout = QHBoxLayout(cat_container)
        cat_layout.setContentsMargins(0,0,0,0)
        cat_layout.setSpacing(0)
        self.cat_label = QLabel(category.upper())
        self.cat_label.setObjectName("CardCategory")
        cat_layout.addWidget(self.cat_label)
        cat_layout.addStretch()
        layout.addWidget(cat_container)

        # Content Container (Username/Email)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        if username:
            usr_lbl = QLabel(f"👤 {username}")
            usr_lbl.setStyleSheet("color: #aaa; font-size: 12px;")
            info_layout.addWidget(usr_lbl)
            
        if email:
            email_lbl = QLabel(f"📧 {email}")
            email_lbl.setStyleSheet("color: #aaa; font-size: 12px;")
            info_layout.addWidget(email_lbl)
            
        layout.addLayout(info_layout)
        
        layout.addStretch()

        # Buttons Layout
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(5)
        btn_layout.setContentsMargins(0, 5, 0, 0)

        # Copy Button
        self.copy_btn = QPushButton("Copy Pwd")
        self.copy_btn.setCursor(Qt.PointingHandCursor)
        self.copy_btn.setStyleSheet("""
            QPushButton { 
                background-color: #333; 
                border: 1px solid #444; 
                font-size: 11px;
                padding: 4px 8px;
                border-radius: 4px;
                color: #ccc;
            }
            QPushButton:hover {
                background-color: #7f5af0;
                color: white;
                border-color: #7f5af0;
            }
        """)
        self.copy_btn.clicked.connect(self.request_copy)
        btn_layout.addWidget(self.copy_btn)

        # Edit Button
        self.edit_btn = QPushButton("Edit")
        self.edit_btn.setCursor(Qt.PointingHandCursor)
        self.edit_btn.setStyleSheet("""
            QPushButton { 
                background-color: #333; 
                border: 1px solid #444; 
                font-size: 11px;
                padding: 4px 8px;
                border-radius: 4px;
                color: #ccc;
            }
            QPushButton:hover {
                background-color: #2cb67d;
                color: white;
                border-color: #2cb67d;
            }
        """)
        self.edit_btn.clicked.connect(lambda: self.editRequested.emit(self.full_data))
        btn_layout.addWidget(self.edit_btn)

        # Delete Button
        self.del_btn = QPushButton("Del")
        self.del_btn.setCursor(Qt.PointingHandCursor)
        self.del_btn.setStyleSheet("""
            QPushButton { 
                background-color: #333; 
                border: 1px solid #444; 
                font-size: 11px;
                padding: 4px 8px;
                border-radius: 4px;
                color: #ccc;
            }
            QPushButton:hover {
                background-color: #ef476f;
                color: white;
                border-color: #ef476f;
            }
        """)
        self.del_btn.clicked.connect(lambda: self.deleteRequested.emit(self.uuid))
        btn_layout.addWidget(self.del_btn)

        # Update Layout
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def request_copy(self):
        # We already have the password decrypted in full_data for display purposes on edit?
        # Actually, for Security, we should probably encrypt 'full_data' or not store the password there?
        # But the Requirement was "Notebook like", "Everything nice and readable".
        # And "Show filled fields".
        # Copy button should just copy the password.
        
        # NOTE: In a real high-security app, we wouldn't keep the password in memory 
        # inside the widget. But for this local "notebook", it makes things snappier.
        # However, to use the existing flow:
        self.copyRequested.emit(self.full_data['password']) 


from ui.settings_dialog import SettingsDialog
from ui.sync_worker import SyncWorker 
from core.utils import resource_path # Added import

class MainWindow(QMainWindow):
    def __init__(self, encryption_key, db_manager):
        super().__init__()
        self.encryption_key = encryption_key
        self.db_manager = db_manager
        
        # Initialize Backup Manager
        self.backup_manager = BackupManager()
        
        # Check for auto-sync on startup
        self.perform_startup_sync()
        
        self.setWindowTitle("IronVault")
        self.resize(1000, 700)
        self.setWindowIcon(QIcon(resource_path("ironvault.ico")))

        # --- Menu Bar ---
        self.create_menu_bar()

        # --- Layouts ---
        main_widget_container = QWidget()
        self.setCentralWidget(main_widget_container)
        
        main_layout = QHBoxLayout(main_widget_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # === SIDEBAR ===
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(250)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(20, 30, 20, 20)
        sidebar_layout.setSpacing(10)

        # App Title in Sidebar
        app_logo_lbl = QLabel("IronVault")
        app_logo_lbl.setStyleSheet("font-size: 24px; font-weight: bold; color: #7f5af0; margin-bottom: 20px;")
        sidebar_layout.addWidget(app_logo_lbl)

        # Navigation Buttons
        self.btn_all = QPushButton("All Items")
        self.btn_all.setCheckable(True)
        self.btn_all.setChecked(True)
        self.btn_all.clicked.connect(lambda: self.filter_items(category="All"))
        
        self.btn_favorites = QPushButton("Favorites")
        self.btn_favorites.setCheckable(True)
        self.btn_favorites.clicked.connect(lambda: self.filter_items(category="Backlog")) # TODO: Implement Logic

        sidebar_layout.addWidget(self.btn_all)
        sidebar_layout.addWidget(self.btn_favorites)
        
        sidebar_layout.addSpacing(20)
        sidebar_layout.addWidget(QLabel("CATEGORIES"))
        
        # Categories (dummy for now, dynamic later?)
        cats = ["Personal", "Work", "Social", "Finance"]
        for c in cats:
            btn = QPushButton(c)
            btn.setCheckable(True)
            # Logic to handle category filtering would go here
            btn.clicked.connect(lambda checked, cat=c: self.filter_items(category=cat))
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()
        
        # Bottom Actions
        self.settings_btn = QPushButton("⚙ Settings")
        self.settings_btn.setObjectName("SettingsBtn")
        self.settings_btn.setStyleSheet("background: transparent; text-align: left; color: #888; padding: 10px;")
        self.settings_btn.setCursor(Qt.PointingHandCursor)
        self.settings_btn.clicked.connect(self.open_settings)
        sidebar_layout.addWidget(self.settings_btn)

        main_layout.addWidget(self.sidebar)

        # === CONTENT AREA ===
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(40, 40, 40, 40)
        content_layout.setSpacing(20)

        # Header: Search & Add
        header_layout = QHBoxLayout()
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search Vault...")
        self.search_bar.setFixedWidth(300)
        self.search_bar.textChanged.connect(self.filter_items)
        header_layout.addWidget(self.search_bar)
        
        header_layout.addStretch()
        
        self.add_btn = QPushButton("➕ New Item")
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.setObjectName("AddButton")
        self.add_btn.setFixedSize(120, 40)
        self.add_btn.clicked.connect(self.show_add_dialog)
        header_layout.addWidget(self.add_btn)
        
        content_layout.addLayout(header_layout)

        # Scroll Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background-color: #1e1e1e;") 
        self.grid_layout = QGridLayout(self.scroll_content)
        self.grid_layout.setSpacing(20)
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        self.scroll.setWidget(self.scroll_content)
        content_layout.addWidget(self.scroll)

        # Add Content Layout
        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        main_layout.addWidget(content_widget)

        # Load Items
        self.load_items()

    def create_menu_bar(self):
        menu_bar = self.menuBar()
        menu_bar.setStyleSheet("""
            QMenuBar {
                background-color: #252526;
                color: #e0e0e0;
            }
            QMenuBar::item:selected {
                background-color: #3e3e3e;
            }
            QMenu {
                background-color: #252526;
                color: #e0e0e0;
                border: 1px solid #3e3e3e;
            }
            QMenu::item:selected {
                background-color: #7f5af0;
            }
        """)
        
        file_menu = menu_bar.addMenu("File")
        
        export_action = QAction("Export Passwords (CSV)", self)
        export_action.triggered.connect(self.export_passwords)
        file_menu.addAction(export_action)
        
        import_action = QAction("Import Passwords (CSV)", self)
        import_action.triggered.connect(self.import_passwords)
        file_menu.addAction(import_action)

        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def load_items(self):
        # Clear Layout
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Fetch from DB
        try:
            entries = self.db_manager.get_all_entries()
            
            row, col = 0, 0
            for entry in entries:
                # entry is a Row object
                uuid = entry['uuid']
                category = entry['category']
                title = entry['title']
                username = entry['username']
                # Check if email column exists (migration handle implicit by row factory if present)
                email = entry['email'] if 'email' in entry.keys() else ""
                
                ciphertext = entry['ciphertext']
                nonce = entry['nonce']
                
                # Decrypt Data to separate Password and Note
                try:
                    decrypted_data = SecurityManager.decrypt(nonce, ciphertext, self.encryption_key)
                    # Try to parse JSON
                    try:
                        secret_obj = json.loads(decrypted_data)
                        password = secret_obj.get("password", "")
                        note = secret_obj.get("note", "")
                    except json.JSONDecodeError:
                        # Legacy format: just the password
                        password = decrypted_data
                        note = ""
                except Exception as e:
                    print(f"Failed to decrypt {title}: {e}")
                    password = "ERROR"
                    note = "Decryption Failed"

                card = PasswordCard(uuid, title, category, username, email, ciphertext, nonce, password, note)
                card.copyRequested.connect(self.copy_password)
                card.deleteRequested.connect(self.delete_item)
                card.editRequested.connect(self.edit_item)
                
                self.grid_layout.addWidget(card, row, col)
                
                col += 1
                if col > 3: # 4 columns
                    col = 0
                    row += 1
        except Exception as e:
            print(f"Error loading items: {e}")

    def perform_startup_sync(self):
        # Only sync if path is set
        if self.backup_manager.backup_path:
            print(f"Auto-Sync: Folder set to {self.backup_manager.backup_path}. Checking...")
            # Ideally verify timestamps, but for "notebook like" simplicity, maybe we don't auto-overwrite?
            # Or we just ensure it exists.
            # User wants "sync", implying bidirectional or just backup?
            # Creating a backup on start is safe. Restoring is dangerous without asking.
            # Let's just create a fresh backup on start to be safe? 
            # Or better: do nothing on start, just on change/close.
            pass

    def trigger_auto_sync(self):
        if self.backup_manager.backup_path:
            print("Auto-Sync: Change detected. Backing up...")
            self.sync_thread = SyncWorker(self.backup_manager, self.encryption_key, "backup", "vault.db")
            self.sync_thread.start()

    def closeEvent(self, event):
        if self.backup_manager.backup_path:
            # Blocking upload on close to ensure data safety
            print("Auto-Sync: Closing... Backing up...")
            success, msg = self.backup_manager.backup_db("vault.db", self.encryption_key)
            print(f"Close Sync: {msg}")
        event.accept()

    def show_add_dialog(self):
        dialog = AddEntryDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            try:
                self.db_manager.add_entry(
                    self.encryption_key, 
                    data['category'], 
                    data['title'], 
                    data['username'],
                    data['email'],
                    data['password'],
                    data['note']
                )
                self.load_items()
                self.trigger_auto_sync() # Hook
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save: {e}")

    def copy_password(self, password):
        try:
            clipboard = QGuiApplication.clipboard()
            clipboard.setText(password)
            # Optional: Show toast
        except Exception as e:
             QMessageBox.critical(self, "Error", f"Failed to copy: {e}")

    def delete_item(self, uuid):
        reply = QMessageBox.question(self, 'Delete Item', 
                                     "Delete this password?\nThis cannot be undone.",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                self.db_manager.delete_entry(uuid)
                self.load_items()
                self.trigger_auto_sync() # Hook
            except Exception as e:
                 QMessageBox.critical(self, "Error", f"Failed to delete: {e}")

    def edit_item(self, entry_data):
        # entry_data is the full_data dict from the card
        dialog = EditEntryDialog(self, 
                                 uuid=entry_data['uuid'],
                                 title=entry_data['title'],
                                 category=entry_data['category'],
                                 username=entry_data['username'],
                                 email=entry_data['email'],
                                 password=entry_data['password'],
                                 note=entry_data['note'])
        
        if dialog.exec():
            new_data = dialog.get_data()
            try:
                self.db_manager.update_entry(
                    new_data['uuid'],
                    self.encryption_key,
                    new_data['category'],
                    new_data['title'],
                    new_data['username'],
                    new_data['email'],
                    new_data['password'],
                    new_data['note']
                )
                self.load_items()
                self.trigger_auto_sync() # Hook
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update: {e}")

    def export_passwords(self):
        reply = QMessageBox.warning(self, "Export Passwords", 
                                    "WARNING: This will export all passwords to a plain text CSV file.\nAnyone with this file can see your passwords.\n\nContinue?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return

        path, _ = QFileDialog.getSaveFileName(self, "Export CSV", "", "CSV Files (*.csv)")
        if not path:
            return

        try:
            entries = self.db_manager.get_all_entries()
            with open(path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Category', 'Title', 'Username', 'Email', 'Password', 'Note'])
                
                for entry in entries:
                    try:
                        decrypted_data = SecurityManager.decrypt(entry['nonce'], entry['ciphertext'], self.encryption_key)
                        try:
                            secret_obj = json.loads(decrypted_data)
                            pwd = secret_obj.get("password","")
                            note = secret_obj.get("note","")
                        except:
                            pwd = decrypted_data
                            note = ""
                            
                        email = entry['email'] if 'email' in entry.keys() else ""
                        
                        writer.writerow([
                            entry['category'], 
                            entry['title'], 
                            entry['username'], 
                            email,
                            pwd, 
                            note
                        ])
                    except:
                        writer.writerow([entry['category'], entry['title'], "ERROR", "ERROR", "DECRYPTION_FAILED", ""])
            
            QMessageBox.information(self, "Success", f"Exported {len(entries)} items to {path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed: {e}")

    def import_passwords(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import CSV", "", "CSV Files (*.csv)")
        if not path:
            return

        try:
            with open(path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                # We should support basic import (Category, Title, Password) and extended
                headers = reader.fieldnames
                
                count = 0
                for row in reader:
                    cat = row.get('Category', 'Uncategorized')
                    title = row.get('Title', 'Untitled')
                    user = row.get('Username', '')
                    email = row.get('Email', '')
                    pwd = row.get('Password', '')
                    note = row.get('Note', '')
                    
                    self.db_manager.add_entry(
                        self.encryption_key,
                        cat, title, user, email, pwd, note
                    )
                    count += 1
            
            self.load_items()
            QMessageBox.information(self, "Success", f"Imported {count} items.")
        except Exception as e:
             QMessageBox.critical(self, "Error", f"Import failed: {e}")

    def open_settings(self):
        dialog = SettingsDialog(self, db_path="vault.db", encryption_key=self.encryption_key)
        dialog.exec()

    def filter_items(self, text):
        text = text.lower()
        for i in range(self.grid_layout.count()):
            widget = self.grid_layout.itemAt(i).widget()
            if isinstance(widget, PasswordCard):
                if (text in widget.full_data['title'].lower() or 
                    text in widget.full_data['category'].lower() or 
                    text in widget.full_data['username'].lower()):
                    widget.show()
                else:
                    widget.hide()
