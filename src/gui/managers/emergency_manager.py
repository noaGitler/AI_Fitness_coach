<<<<<<< HEAD
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
=======
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import QObject, Qt
from PyQt6.QtGui import QFont

class EmergencyManager(QObject):
    def __init__(self, main_window=None):  # שינוי: מקבל את ה-MainWindow כהורה
        super().__init__(main_window)
        self.main_window = main_window
        
        # ה-Overlay כעת יושב ישירות על כל ה-MainWindow וחוסם הכל ברקע!
        self.overlay = QWidget(self.main_window)
        self.overlay.setObjectName("EmergencyOverlay")        
        
        layout = QVBoxLayout(self.overlay)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.text_label = QLabel("EMERGENCY DETECTED!\nCalling Emergency Services...")
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_label.setObjectName("EmergencyText")
        layout.addWidget(self.text_label)
        
        # 🌟 הוספת כפתור יציאה / ביטול במרכז המסך האדום
        self.exit_btn = QPushButton("I'M OK - CLOSE & RESET", self.overlay)
        self.exit_btn.setObjectName("EmergencyExitBtn") # תוכלי לעצב אותו ב-QSS
        self.exit_btn.setFixedSize(250, 50)
        self.exit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.exit_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.overlay.hide()

    def show_emergency(self):
        """פונקציה שמקפיצה את המסך האדום וחוסמת את כל האתר"""
        if self.main_window:
            # מתפרס על פני כל ה-MainWindow וחוסם פיזית גישה לשאר הכפתורים!
            self.overlay.resize(self.main_window.size())
            self.overlay.move(0, 0)
            self.overlay.raise_()  # דוחף את המסך האדום לשכבה הכי עליונה ב-UI
            
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
>>>>>>> upstream/main
