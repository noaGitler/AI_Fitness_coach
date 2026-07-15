from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
import cv2

class VideoWidget(QLabel):
    """The trainee's live camera feed widget, enlarged for maximum UX."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText("WAITING FOR STREAM...")
        self.setFixedSize(800, 600)

        self.setObjectName("VideoWidget")

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