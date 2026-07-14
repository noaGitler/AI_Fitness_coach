from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
import cv2

class VideoWidget(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText("WAITING FOR STREAM...")
        
        # מבטלים את המתיחה בכוח כדי למנוע את המריחה!
        self.setScaledContents(False)
        
        # קובעים מידות קבועות ויציבות לפאנל הוידאו
        self.setFixedSize(640, 480)
        
        # תיקון ה-Unknown property: מגדירים במפורש ל-QLabel!
        self.setStyleSheet("""
            QLabel {
                background-color: #050709;
                border: 2px solid #1c232a;
                border-radius: 12px;
                color: #8a99a6;
            }
        """)

    def update_frame(self, frame):
        if frame is None:
            return
            
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        
        # המרת פריים ל-RGB
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        qt_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_img)
        
        # התאמה פרופורציונלית מושלמת (4:3) שומרת על יחס הגוף המקורי שלך בלי למרוח כלום!
        scaled_pixmap = pixmap.scaled(
            640, 
            480, 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        
        self.setPixmap(scaled_pixmap)







# from PyQt6.QtWidgets import QLabel
# from PyQt6.QtCore import Qt
# from PyQt6.QtGui import QImage, QPixmap
# import cv2

# class VideoWidget(QLabel):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         self.setText("WAITING FOR STREAM...")
        
#         # 1. פקודת הקסם: אומרת ל-PyQt6 למתוח/לכווץ את התמונה אוטומטית לפי גודל הרכיב
#         self.setScaledContents(True)
        
#         # 2. קיבוע מידות ברזולוציה מושלמת: מונע לחלוטין את אפקט "כדור השלג" וההתרחבות!
#         self.setMinimumSize(640, 480)
#         self.setMaximumSize(800, 600)
        
#         self.setStyleSheet("""
#             VideoWidget {
#                 background-color: #050709;
#                 border: 2px solid #1c232a;
#                 border-radius: 12px;
#                 color: #8a99a6;
#             }
#         """)

#     def update_frame(self, frame):
#         if frame is None:
#             return
            
#         h, w, ch = frame.shape
#         bytes_per_line = ch * w
        
#         # המרת הפריים מ-BGR של OpenCV ל-RGB של PyQt6
#         rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
#         qt_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
#         pixmap = QPixmap.fromImage(qt_img)
        
#         # פשוט דוחפים את התמונה פנימה, והגדרת ה-setScaledContents דואגת להתאמה חלקה
#         self.setPixmap(pixmap)




# from PyQt6.QtWidgets import QLabel
# from PyQt6.QtCore import Qt
# from PyQt6.QtGui import QImage, QPixmap
# import cv2

# class VideoWidget(QLabel):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.setText("Camera Loading...")
#         self.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         self.setStyleSheet("background-color: black; color: white; border_radius: 10px;")
        
#     def update_frame(self, frame):
#         frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         h, w, ch = frame_rgb.shape
#         bytes_per_line = ch * w
        
#         qt_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
#         pixmap = QPixmap.fromImage(qt_image)
        
#         scaled_pixmap = pixmap.scaled(self.width(), self.height(), Qt.AspectRatioMode.KeepAspectRatio)
#         self.setPixmap(scaled_pixmap)