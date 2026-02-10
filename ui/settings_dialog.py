
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, 
                               QHBoxLayout, QGroupBox, QMessageBox, QFileDialog, QLineEdit)
from PySide6.QtCore import Qt
from core.backup_manager import BackupManager
import os
import shutil

from PySide6.QtGui import QIcon
from core.utils import resource_path

class SettingsDialog(QDialog):
    def __init__(self, parent=None, db_path="vault.db", encryption_key=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedSize(500, 350)
        self.setWindowIcon(QIcon(resource_path("ironvault.ico"))) # Force Icon
        
        self.db_path = db_path
        self.encryption_key = encryption_key
        
        # Backup Manager
        self.backup_manager = BackupManager()
        
        # Stylesheet
        self.setStyleSheet("""
            QDialog { background-color: #202020; color: #e0e0e0; }
            QGroupBox { 
                border: 1px solid #404040; 
                border-radius: 6px; 
                margin-top: 20px; 
                padding-top: 15px;
                color: #e0e0e0;
                font-weight: bold;
            }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; }
            QLabel { color: #cccccc; font-size: 13px; }
            QLineEdit {
                background-color: #333;
                border: 1px solid #444;
                color: #e0e0e0;
                padding: 6px;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #333;
                border: 1px solid #444;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #444; }
            QPushButton#Primary { background-color: #7f5af0; border: none; }
            QPushButton#Primary:hover { background-color: #6a46cd; }
            QPushButton#Danger { background-color: #ef476f; border: none; }
            QPushButton#Danger:hover { background-color: #d63d60; }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # --- Backup / Sync Section ---
        sync_group = QGroupBox("Backup & Sync Location")
        sync_layout = QVBoxLayout(sync_group)
        sync_layout.setSpacing(10)
        
        lbl = QLabel("Select a folder to sync your vault to (e.g. Google Drive, OneDrive, USB):")
        lbl.setWordWrap(True)
        sync_layout.addWidget(lbl)
        
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setReadOnly(True)
        self.path_input.setPlaceholderText("No folder selected")
        if self.backup_manager.backup_path:
            self.path_input.setText(self.backup_manager.backup_path)
            
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_folder)
        
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(browse_btn)
        sync_layout.addLayout(path_layout)
        
        # Sync Actions
        actions_layout = QHBoxLayout()
        self.sync_now_btn = QPushButton("Sync Now (Backup)")
        self.sync_now_btn.clicked.connect(self.backup_db)
        
        self.restore_btn = QPushButton("Restore (Import)")
        self.restore_btn.clicked.connect(self.restore_db)
        
        actions_layout.addWidget(self.sync_now_btn)
        actions_layout.addWidget(self.restore_btn)
        sync_layout.addLayout(actions_layout)
        
        # Info
        info_lbl = QLabel("IronVault will automatically update the backup in this folder when you make changes.")
        info_lbl.setStyleSheet("color: #777; font-size: 11px;")
        info_lbl.setWordWrap(True)
        sync_layout.addWidget(info_lbl)

        layout.addWidget(sync_group)
        
        # --- Import / Export Section ---
        data_group = QGroupBox("Data Management")
        data_layout = QHBoxLayout(data_group)
        
        export_btn = QPushButton("Export CSV")
        export_btn.clicked.connect(self.export_csv)
        
        import_btn = QPushButton("Import CSV")
        import_btn.clicked.connect(self.import_csv) 
        
        data_layout.addWidget(export_btn)
        data_layout.addWidget(import_btn)
        
        layout.addWidget(data_group)
        
        layout.addStretch()

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Backup Folder")
        if folder:
            self.path_input.setText(folder)
            self.backup_manager.set_backup_path(folder)
            QMessageBox.information(self, "Success", "Backup location set!\nAuto-sync is now active for this folder.")

    def backup_db(self):
        if not self.encryption_key:
            QMessageBox.critical(self, "Error", "Encryption key not available.")
            return

        success, msg = self.backup_manager.backup_db(self.db_path, self.encryption_key)
        if success:
            QMessageBox.information(self, "Success", msg)
        else:
            QMessageBox.warning(self, "Error", msg)

    def restore_db(self):
        if not self.encryption_key:
             QMessageBox.critical(self, "Error", "Encryption key not available.")
             return

        reply = QMessageBox.question(self, "Restore Database", 
                                     "This will OVERWRITE your local database with the version from the backup folder.\nAre you sure?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return

        success, msg = self.backup_manager.restore_db(self.db_path, self.encryption_key)
        if success:
            QMessageBox.information(self, "Success", "Restored successfully!\nPlease restart the application.")
        else:
            QMessageBox.warning(self, "Error", msg)

    def export_csv(self):
        if self.parent():
            self.parent().export_passwords()

    def import_csv(self):
        if self.parent():
            self.parent().import_passwords()

from PySide6.QtWidgets import QApplication
