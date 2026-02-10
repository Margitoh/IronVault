
from PySide6.QtWidgets import QSplashScreen, QProgressBar, QVBoxLayout, QLabel, QWidget, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QSize
from PySide6.QtGui import QPixmap, QFont, QColor

class PulsingSplashScreen(QSplashScreen):
    def __init__(self):
        # Create a basic pixmap for the splash (transparent background)
        pixmap = QPixmap(400, 300)
        pixmap.fill(Qt.transparent)
        super().__init__(pixmap)
        
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Main Layout Container
        self.container = QWidget(self)
        self.container.setGeometry(0, 0, 400, 300)
        self.container.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border: 1px solid #333;
                border-radius: 12px;
            }
        """)

        layout = QVBoxLayout(self.container)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        # Icon Label (The pulsing part)
        self.icon_label = QLabel("🔒")
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("font-size: 80px; color: #7f5af0; background: transparent; border: none;")
        layout.addWidget(self.icon_label)

        # App Name
        self.title_label = QLabel("IronVault")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #ffffff; background: transparent; border: none;")
        layout.addWidget(self.title_label)

        # Subtitle / Status
        self.status_label = QLabel("Initializing Safe Environment...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 14px; color: #888888; background: transparent; border: none;")
        layout.addWidget(self.status_label)

        # Loading Bar (Visual candy)
        self.progress = QProgressBar()
        self.progress.setRange(0, 0) # Indeterminate
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(4)
        self.progress.setFixedWidth(200)
        self.progress.setStyleSheet("""
            QProgressBar {
                background-color: #333;
                border-radius: 2px;
                border: none;
            }
            QProgressBar::chunk {
                background-color: #7f5af0;
                border-radius: 2px;
            }
        """)
        # Layout alignment for progress bar
        layout.addWidget(self.progress, alignment=Qt.AlignCenter)

        # Setup Pulsing Animation
        self.setup_pulse_animation()

    def setup_pulse_animation(self):
        # We'll animate opacity of the icon
        self.opacity_effect = QGraphicsOpacityEffect(self.icon_label)
        self.icon_label.setGraphicsEffect(self.opacity_effect)

        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(1000) # 1 second cycle
        self.anim.setStartValue(1.0)
        self.anim.setKeyValueAt(0.5, 0.4) # Fade out halfway
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.anim.setLoopCount(-1) # Infinite loop
        self.anim.start()

    def show_message(self, msg):
        self.status_label.setText(msg)
        QTimer.singleShot(100, lambda: None) # Force event loop update if needed
