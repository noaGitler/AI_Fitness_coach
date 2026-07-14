from PyQt6.QtWidgets import QLabel, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap, QColor
import cv2
import os

class VideoWidget(QLabel):
    """חלונית המצלמה החיה של המתאמן - מוגדלת לחוויית UX מקסימלית"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText("WAITING FOR STREAM...")
        self.setFixedSize(800, 600)
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
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        qt_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_img)
        
        scaled_pixmap = pixmap.scaled(
            800, 600, 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(scaled_pixmap)


class DemoVideoWidget(QLabel):
    """חלונית הדגמה מקצועית - מניחה שכל הסרטונים נורמלו לחזרה 1 ומריצה אותם פעמיים"""
    
    # מילון נקי, פשוט ויעיל של מפתח-ערך
    VIDEO_MAPPING = {
        "knee_extension": "assets/robot_knee.mp4",
        "knee extension": "assets/robot_knee.mp4",
        "knee":           "assets/robot_knee.mp4",
        
        "bicep_curl":     "assets/robot_bicep.mp4",
        "bicep curl":     "assets/robot_bicep.mp4",
        "bicep":           "assets/robot_bicep.mp4",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(160, 200)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                background-color: #050709;
                border: 2px solid #00f3ff;
                border-radius: 8px;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 243, 255, 100))
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)
        
        self.demo_cap = None
        self.max_loops = 2  # כל סרטון במערכת יתנגן בדיוק פעמיים ברצף!
        self.loop_count = 0
        
        self.play_timer = QTimer(self)
        self.play_timer.timeout.connect(self.play_next_frame)

    def has_demo_video(self, exercise_name):
        if not exercise_name:
            return False
        exercise_clean = exercise_name.lower()
        return any(key in exercise_clean for key in self.VIDEO_MAPPING.keys())

    def set_active_exercise(self, exercise_name):
        if self.demo_cap is not None:
            self.demo_cap.release()
            self.demo_cap = None
        self.play_timer.stop()
        self.clear()
        
        exercise_clean = exercise_name.lower() if exercise_name else ""
        video_path = None
        
        for key, path in self.VIDEO_MAPPING.items():
            if key in exercise_clean:
                video_path = path
                break
                
        if video_path and os.path.exists(video_path):
            self.demo_cap = cv2.VideoCapture(video_path)
            self.loop_count = 0
            self.setVisible(True)
            self.play_timer.start(33)
        else:
            self.setVisible(False)

    def trigger_manual_demo(self):
        if self.demo_cap is not None:
            self.demo_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.loop_count = 0
            self.play_timer.start(33)

    def play_next_frame(self):
        if self.demo_cap is None:
            return
            
        ret, frame = self.demo_cap.read()
        if not ret:
            self.loop_count += 1
            if self.loop_count >= self.max_loops:
                # סיום הלולאות: עצירה חזרה בפריים 0 (עמידת מוצא ישר) למניעת פריים קפוא באמצע תנועה
                self.play_timer.stop()
                self.demo_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret_reset, reset_frame = self.demo_cap.read()
                if ret_reset:
                    self.display_frame(reset_frame)
                return
            else:
                self.demo_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.demo_cap.read()
                if not ret:
                    return

        self.display_frame(frame)

    def display_frame(self, frame):
        frame = cv2.bilateralFilter(frame, d=5, sigmaColor=40, sigmaSpace=40)
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        qt_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_img)
        
        scaled_pixmap = pixmap.scaled(
            self.width() - 4, self.height() - 4,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(scaled_pixmap)

    def closeEvent(self, event):
        self.play_timer.stop()
        if self.demo_cap is not None:
            self.demo_cap.release()
        super().closeEvent(event)







# from PyQt6.QtWidgets import QLabel
# from PyQt6.QtCore import Qt
# from PyQt6.QtGui import QImage, QPixmap
# import cv2

# class VideoWidget(QLabel):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         self.setText("WAITING FOR STREAM...")
        
#         # מבטלים את המתיחה בכוח כדי למנוע את המריחה!
#         self.setScaledContents(False)
        
#         # קובעים מידות קבועות ויציבות לפאנל הוידאו
#         self.setFixedSize(640, 480)
        
#         # תיקון ה-Unknown property: מגדירים במפורש ל-QLabel!
#         self.setStyleSheet("""
#             QLabel {
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
        
#         # המרת פריים ל-RGB
#         rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         qt_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
#         pixmap = QPixmap.fromImage(qt_img)
        
#         # התאמה פרופורציונלית מושלמת (4:3) שומרת על יחס הגוף המקורי שלך בלי למרוח כלום!
#         scaled_pixmap = pixmap.scaled(
#             640, 
#             480, 
#             Qt.AspectRatioMode.KeepAspectRatio, 
#             Qt.TransformationMode.SmoothTransformation
#         )
        
#         self.setPixmap(scaled_pixmap)







# # from PyQt6.QtWidgets import QLabel
# # from PyQt6.QtCore import Qt
# # from PyQt6.QtGui import QImage, QPixmap
# # import cv2

# # class VideoWidget(QLabel):
# #     def __init__(self, parent=None):
# #         super().__init__(parent)
# #         self.setAlignment(Qt.AlignmentFlag.AlignCenter)
# #         self.setText("WAITING FOR STREAM...")
        
# #         # 1. פקודת הקסם: אומרת ל-PyQt6 למתוח/לכווץ את התמונה אוטומטית לפי גודל הרכיב
# #         self.setScaledContents(True)
        
# #         # 2. קיבוע מידות ברזולוציה מושלמת: מונע לחלוטין את אפקט "כדור השלג" וההתרחבות!
# #         self.setMinimumSize(640, 480)
# #         self.setMaximumSize(800, 600)
        
# #         self.setStyleSheet("""
# #             VideoWidget {
# #                 background-color: #050709;
# #                 border: 2px solid #1c232a;
# #                 border-radius: 12px;
# #                 color: #8a99a6;
# #             }
# #         """)

# #     def update_frame(self, frame):
# #         if frame is None:
# #             return
            
# #         h, w, ch = frame.shape
# #         bytes_per_line = ch * w
        
# #         # המרת הפריים מ-BGR של OpenCV ל-RGB של PyQt6
# #         rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
# #         qt_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
# #         pixmap = QPixmap.fromImage(qt_img)
        
# #         # פשוט דוחפים את התמונה פנימה, והגדרת ה-setScaledContents דואגת להתאמה חלקה
# #         self.setPixmap(pixmap)




# # from PyQt6.QtWidgets import QLabel
# # from PyQt6.QtCore import Qt
# # from PyQt6.QtGui import QImage, QPixmap
# # import cv2

# # class VideoWidget(QLabel):
# #     def __init__(self, parent=None):
# #         super().__init__(parent)
# #         self.setText("Camera Loading...")
# #         self.setAlignment(Qt.AlignmentFlag.AlignCenter)
# #         self.setStyleSheet("background-color: black; color: white; border_radius: 10px;")
        
# #     def update_frame(self, frame):
# #         frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
# #         h, w, ch = frame_rgb.shape
# #         bytes_per_line = ch * w
        
# #         qt_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
# #         pixmap = QPixmap.fromImage(qt_image)
        
# #         scaled_pixmap = pixmap.scaled(self.width(), self.height(), Qt.AspectRatioMode.KeepAspectRatio)
# #         self.setPixmap(scaled_pixmap)