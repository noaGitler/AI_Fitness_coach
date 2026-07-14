from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class StatsCard(QFrame):
    def __init__(self, title, initial_value, parent=None):
        super().__init__(parent)
        self.setFixedSize(280, 110)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(2)
        
        self.title_label = QLabel(title.upper())
        self.title_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignLeft)
        
        self.value_label = QLabel(str(initial_value))
        self.value_label.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        layout.addWidget(self.value_label, alignment=Qt.AlignmentFlag.AlignRight)
        
      
        self.setObjectName("StatsCard")
        self.title_label.setObjectName("StatsTitle")
        self.value_label.setObjectName("StatsValue")



    def update_value(self, new_value):
        self.value_label.setText(str(new_value))





# from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
# from PyQt6.QtCore import Qt
# from PyQt6.QtGui import QFont

# class StatsCard(QFrame):
#     def __init__(self, title, initial_value="0", parent=None):
#         super().__init__(parent)
        
#         # הגדרת מבנה פנימי של הכרטיסייה (מלמעלה למטה)
#         layout = QVBoxLayout(self)
#         layout.setContentsMargins(12, 12, 12, 12)
#         layout.setSpacing(4)
        
#         # 1. כותרת המדד (טקסט קטן, אפור-רובוטי עדין)
#         self.title_label = QLabel(title.upper())
#         self.title_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
#         self.title_label.setStyleSheet("color: #8a99a6; background: transparent; border: none;")
#         self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
#         layout.addWidget(self.title_label)
        
#         # 2. ערך המדד (מספר ענק, לבן-מבריק ודיגיטלי)
#         self.value_label = QLabel(initial_value)
#         self.value_label.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
#         self.value_label.setStyleSheet("color: #ffffff; background: transparent; border: none;")
#         self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         layout.addWidget(self.value_label)
        
#         # 3. עיצוב ה-QSS העתידני: רקע Dark מטאלי עם מסגרת ניאון טורקיז זוהרת (בהשראת Agibot!)
#         self.setStyleSheet("""
#             StatsCard {
#                 background-color: #1a1f24;
#                 border: 2px solid #00f3ff;
#                 border_radius: 8px;
#             }
#         """)
        
#     def update_value(self, new_value):
#         """פונקציה ציבורית המאפשרת ללולאה הראשית לעדכן את המספר בשידור חי"""
#         self.value_label.setText(str(new_value))