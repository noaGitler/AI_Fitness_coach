from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
import cv2

class VideoWidget(QLabel):
    """A simple QLabel that displays live camera frames (converted from OpenCV to Qt)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("Camera Loading...")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background-color: black; color: white; border-radius: 10px;")
        
    def update_frame(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        
        qt_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        
        scaled_pixmap = pixmap.scaled(self.width(), self.height(), Qt.AspectRatioMode.KeepAspectRatio)
        self.setPixmap(scaled_pixmap)