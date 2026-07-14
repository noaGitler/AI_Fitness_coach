from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import QObject, Qt

class EmergencyManager(QObject):
    def __init__(self, parent_widget=None):
        super().__init__(parent_widget)
        self.parent = parent_widget
        
        # יצירת ה-Overlay
        self.overlay = QWidget(self.parent)
        self.overlay.setStyleSheet("background-color: rgba(200, 0, 0, 120); border-radius: 15px;")
        
        layout = QVBoxLayout(self.overlay)
        
        self.text_label = QLabel("EMERGENCY DETECTED!\nCalling Emergency Services...")
        self.text_label.setStyleSheet("color: white; font-size: 36px; font-weight: bold; background: transparent;")
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.text_label)
        
        # מתחיל מוסתר
        self.overlay.hide()

    def show_emergency(self):
        """פונקציה שנקראת ברגע האמת ומתאימה את עצמה לוידאו"""
        if self.parent:
            # שינוי הגודל והמיקום כדי לכסות 100% מהוידאו
            self.overlay.resize(self.parent.size())
            self.overlay.move(0, 0)
            
        self.overlay.show()
        print("[SOS] !!! EMERGENCY CALL PLACED TO AUTHORITIES !!!")