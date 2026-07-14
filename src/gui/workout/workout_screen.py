from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.gui.workout.camera_widget import VideoWidget
from src.gui.workout.demo_widget import DemoVideoWidget
from src.gui.workout.workout_dashboard import WorkoutDashboard

class WorkoutScreen(QWidget):
    """מסך האימון הפעיל - אחראי על סידור הרכיבים הוויזואליים בלבד"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # כותרת עליונה
        self.header_label = QLabel("AI SESSION ACTIVE")
        self.header_label.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        layout.addWidget(self.header_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # שורת התוכן הראשית
        content = QHBoxLayout()
        content.setSpacing(20) 
        
        # 1. בלוק שמאל: המצלמה המוגדלת
        self.video_panel = VideoWidget(self)
        video_container = QVBoxLayout()
        video_container.addWidget(self.video_panel)
        content.addLayout(video_container, stretch=0)
        
        # 2. בלוק מרכז: עמדת רובוט ההדגמה והכפתור (מיושרים לתחתית)
        demo_container = QVBoxLayout()
        demo_container.setSpacing(10)
        demo_container.addStretch() 
        
        self.demo_video_panel = DemoVideoWidget(self)
        self.demo_video_panel.setVisible(False)
        
        self.replay_demo_btn = QPushButton("🔄 REPLAY DEMO", self)
        self.replay_demo_btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.replay_demo_btn.setFixedSize(160, 32)
        self.replay_demo_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.replay_demo_btn.setVisible(False)
        
        demo_container.addWidget(self.demo_video_panel, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)
        demo_container.addWidget(self.replay_demo_btn, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)
        content.addLayout(demo_container, stretch=0)
        
        # 3. בלוק ימין: דשבורד הנתונים
        self.dashboard = WorkoutDashboard(self)
        self.dashboard.setFixedWidth(320)
        content.addWidget(self.dashboard, stretch=0)
        
        layout.addLayout(content)

        self.header_label.setObjectName("SelectedProgramTitle")
        # self.replay_demo_btn.setObjectName("PauseBtn")
        self.replay_demo_btn.setObjectName("ReplayDemoBtn")