import sys
import time
from PySide6.QtWidgets import QApplication, QDialog
from PySide6.QtCore import QTimer
from ui.splash_screen import PulsingSplashScreen
from ui.styles import DARK_THEME_QSS
from core.utils import resource_path # Added import
from PySide6.QtGui import QIcon

# Global reference to keep the window alive
main_window = None

def main():
    global main_window
    app = QApplication(sys.argv)
    app.setStyle("Fusion") 
    app.setStyleSheet(DARK_THEME_QSS)
    
    # Set Global Icon
    app.setWindowIcon(QIcon(resource_path("ironvault.ico")))

    splash = PulsingSplashScreen()
    splash.show()
    app.processEvents()

    def init_app():
        global main_window
        splash.show_message("Loading Core Muscles...")
        app.processEvents()
        
        # --- Defer Heavy Imports ---
        # This allows the splash to show up INSTANTLY before Python loads completely
        from ui.login_dialog import LoginDialog
        from ui.main_window import MainWindow
        from database.db_manager import DBManager
        # ---------------------------

        splash.show_message("Initializing Secure Vault...")
        app.processEvents()
        
        # Initialize Database
        db_mgr = DBManager()
        
        splash.show_message("Verifying Integrity...")
        app.processEvents()
        time.sleep(0.5) # Small delay for UX 'weight'

        splash.show_message("Ready.")
        app.processEvents()
        time.sleep(0.2)

        login = LoginDialog(db_mgr)
        
        # We can hide splash now, or after login success. 
        # Standard desktop app behavior: Splash -> Login.
        splash.finish(login) 

        if login.exec() == QDialog.Accepted:
            encryption_key = login.key
            # Use global variable to prevent Garbage Collection
            main_window = MainWindow(encryption_key, db_mgr)
            main_window.show()
        else:
            sys.exit(0)

    # Run init heavily AFTER the event loop has started and splash is painted
    QTimer.singleShot(100, init_app)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
