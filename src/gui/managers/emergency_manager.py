from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import QObject, Qt
from PyQt6.QtGui import QFont

class EmergencyManager(QObject):
    """
    Builds and controls the full-screen red emergency overlay shown when a
    fall/emergency is triggered.
    """
    def __init__(self, main_window=None):  # receives the MainWindow as its parent
        super().__init__(main_window)
        self.main_window = main_window
        
        # The overlay sits directly on top of the whole MainWindow and blocks everything behind it
        self.overlay = QWidget(self.main_window)
        self.overlay.setObjectName("EmergencyOverlay")        
        
        layout = QVBoxLayout(self.overlay)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.text_label = QLabel("EMERGENCY DETECTED!\nCalling Emergency Services...")
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_label.setObjectName("EmergencyText")
        layout.addWidget(self.text_label)
        
        # Exit/cancel button in the middle of the red screen
        self.exit_btn = QPushButton("I'M OK - CLOSE & RESET", self.overlay)
        self.exit_btn.setObjectName("EmergencyExitBtn") # תוכלי לעצב אותו ב-QSS
        self.exit_btn.setFixedSize(250, 50)
        self.exit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.exit_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.overlay.hide()

    def show_emergency(self):
        """Function that displays the red screen and blocks access to the rest of the application"""
        if self.main_window:
            # Spans across the entire MainWindow and physically blocks access to the rest of the buttons!
            self.overlay.resize(self.main_window.size())
            self.overlay.move(0, 0)
            self.overlay.raise_()  # Pushes the red screen to the top layer in the UI
            
        self.overlay.show()
        print("[SOS] !!! EMERGENCY CALL PLACED TO AUTHORITIES !!!")












# from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
# from PyQt6.QtCore import QObject, Qt
# from PyQt6.QtGui import QFont

# class EmergencyManager(QObject):
#     def __init__(self, parent_widget=None):
#         super().__init__(parent_widget)
#         self.parent = parent_widget
        
#         # יצירת ה-Overlay
#         self.overlay = QWidget(self.parent)
#         self.overlay.setObjectName("EmergencyOverlay")        
#         layout = QVBoxLayout(self.overlay)
        
#         self.text_label = QLabel("EMERGENCY DETECTED!\nCalling Emergency Services...")
        
#         self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
#         self.text_label.setObjectName("EmergencyText")

#         layout.addWidget(self.text_label)
        
#         # מתחיל מוסתר
#         self.overlay.hide()

#     def show_emergency(self):
#         """פונקציה שנקראת ברגע האמת ומתאימה את עצמה לוידאו"""
#         if self.parent:
#             # שינוי הגודל והמיקום כדי לכסות 100% מהוידאו
#             self.overlay.resize(self.parent.size())
#             self.overlay.move(0, 0)
            
#         self.overlay.show()
#         print("[SOS] !!! EMERGENCY CALL PLACED TO AUTHORITIES !!!")