
from PySide6.QtCore import QThread, Signal
from core.backup_manager import BackupManager

class SyncWorker(QThread):
    finished = Signal(bool, str) # success, message

    def __init__(self, backup_manager, encryption_key, action="backup", db_path="vault.db"):
        super().__init__()
        self.backup_manager = backup_manager
        self.encryption_key = encryption_key
        self.action = action
        self.db_path = db_path

    def run(self):
        if self.action == "backup":
            success, msg = self.backup_manager.backup_db(self.db_path, self.encryption_key)
            self.finished.emit(success, msg)
        elif self.action == "restore":
            success, msg = self.backup_manager.restore_db(self.db_path, self.encryption_key)
            self.finished.emit(success, msg)
