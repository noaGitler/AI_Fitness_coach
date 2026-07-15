from PyQt6.QtWidgets import QLabel, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap, QColor
import cv2
import os

class DemoVideoWidget(QLabel):
    """A small widget that plays a looping demo clip of the correct exercise form."""
    
    # Maps exercise name keywords to their demo video asset
    VIDEO_MAPPING = {
        "knee_extension": "assets/robot_knee.mp4",
        "knee extension": "assets/robot_knee.mp4",
        "knee":           "assets/robot_knee.mp4",
        
        "bicep_curl":     "assets/robot_bicep.mp4",
        "bicep curl":     "assets/robot_bicep.mp4",
        "bicep":           "assets/robot_bicep.mp4",

        "squat":          "assets/robot_squat.mp4", 
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(160, 200)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.setObjectName("DemoWidget")
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 243, 255, 100))
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)
        
        self.demo_cap = None
        self.max_loops = 2  # each video in the system will play exactly twice in succession
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
        """Replays the demo clip from the start (e.g. on manual request)."""
        if self.demo_cap is not None:
            self.demo_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.loop_count = 0
            self.play_timer.start(33)

    def play_next_frame(self):
        """Advances the demo clip by one frame, looping up to max_loops times."""
        if self.demo_cap is None:
            return
            
        ret, frame = self.demo_cap.read()
        if not ret:
            self.loop_count += 1
            if self.loop_count >= self.max_loops:
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
        """Applies a smoothing filter and renders the frame as a scaled pixmap."""
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
        """Releases the video capture resource when the widget closes."""
        self.play_timer.stop()
        if self.demo_cap is not None:
            self.demo_cap.release()
        super().closeEvent(event)