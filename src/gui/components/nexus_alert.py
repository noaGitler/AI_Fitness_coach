from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class NexusAlert(QDialog):
    """חלונית הודעות גנרית ואטומה לחלוטין בסטייל סייברפאנק - פתרון סופי לבעיית השקיפות"""
    def __init__(self, title_text, msg_text, is_success=True, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        
        # משאירים את הרקע החיצוני שקוף אך ורק בשביל הפינות המעוגלות של הקצוות
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(360, 220)
        
        # לוח ראשי חיצוני שמחזיק את הכל
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # --- תיקון הקסם: יצירת קונטיינר פנימי אטום לחלוטין שמסתיר את מה שמאחור ---
        self.container = QFrame(self)
        accent_color = "#00ff66" if is_success else "#ff3333"
        
        # צביעת הריבוע הפנימי בשחור עמוק, אטום ומקובע
        self.container.setStyleSheet(f"""
            QFrame {{
                background-color: #0c0f12;
                border: 2px solid {accent_color};
                border-radius: 12px;
            }}
        """)
        
        # לוגיקת הפריסה הפנימית של הטקסטים בתוך הקונטיינר האטום
        container_layout = QVBoxLayout(self.container)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.setContentsMargins(25, 20, 25, 20)
        
        # 1. כותרת החלונית
        title = QLabel(title_text.upper())
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {accent_color}; letter-spacing: 2px; background: transparent; border: none;")
        container_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 2. תוכן ההודעה
        msg = QLabel(msg_text)
        msg.setFont(QFont("Segoe UI", 11))
        msg.setWordWrap(True)
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg.setStyleSheet("color: #ffffff; background: transparent; border: none; margin-top: 10px; margin-bottom: 15px;")
        container_layout.addWidget(msg)
        
        # 3. כפתור אישור
        btn = QPushButton("ACKNOWLEDGE")
        btn.setFixedWidth(140)
        btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #101418;
                color: {accent_color};
                border: 1px solid {accent_color};
                padding: 8px;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {accent_color};
                color: #0c0f12;
            }}
        """)
        btn.clicked.connect(self.accept)
        container_layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # הוספת הקונטיינר המעוצב לתוך הדיאלוג הראשי
        main_layout.addWidget(self.container)

    @staticmethod
    def show_message(title, message, is_success=True, parent=None):
        alert = NexusAlert(title, message, is_success, parent)
        alert.exec()