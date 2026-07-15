from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from src.gui.components.stats_card import StatsCard

class WorkoutDashboard(QFrame):
    """The live stats panel: goal/reps/time cards, AI feedback, and the pause/quit buttons."""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 15, 10, 15)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # 1. System status
        self.status_title = QLabel("WORKOUT STATUS")
        self.status_title.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        layout.addWidget(self.status_title)
        
        self.status_label = QLabel("READY")
        self.status_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        layout.addWidget(self.status_label)
        
        # 2. Live metric cards
        self.goal_card = StatsCard("Target Goal", "0", self)
        self.progress_card = StatsCard("Reps Remaining", "0", self)
        self.time_card = StatsCard("Session Time Left", "00:00", self)
        
        layout.addWidget(self.goal_card)
        layout.addWidget(self.progress_card)
        layout.addWidget(self.time_card)

        # 3. Live AI feedback area
        self.feedback_title = QLabel("AI REAL-TIME FEEDBACK")
        self.feedback_title.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        layout.addWidget(self.feedback_title)

        self.feedback_label = QLabel("Waiting for movement pattern...")
        self.feedback_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.feedback_label.setWordWrap(True)
        self.feedback_label.setMinimumHeight(70)
        self.feedback_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.feedback_label)
        
        # 4. The PAUSE / RESUME button
        self.pause_btn = QPushButton("PAUSE", self)
        self.pause_btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.pause_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.pause_btn)

        # 5. The QUIT button to end the workout
        self.exit_session_btn = QPushButton("QUIT", self)
        self.exit_session_btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.exit_session_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.exit_session_btn)
        
        self.setObjectName("WorkoutDashboard")
        self.status_title.setObjectName("DashboardStatusTitle")
        self.status_label.setObjectName("DashboardStatusLabel")
        self.feedback_title.setObjectName("FeedbackTitle")
        self.feedback_label.setObjectName("FeedbackLabel")
        self.pause_btn.setObjectName("PauseBtn")
        self.exit_session_btn.setObjectName("QuitBtn")

    def set_paused_ui(self, is_paused):
        """Updates the visibility and appearance of the pause button"""
        if is_paused:
            self.pause_btn.setText("RESUME")
            self.pause_btn.setProperty("class", "ResumeActive")
            self.status_label.setText("PAUSED")
            self.status_label.setProperty("class", "StatusPaused")
        else:
            self.pause_btn.setText("PAUSE")
            self.pause_btn.setProperty("class", "")
            self.status_label.setText("TRAINING")
            self.status_label.setProperty("class", "StatusTraining")
            
        # Force a style refresh for the affected widgets
        for widget in [self.pause_btn, self.status_label]:
            widget.style().unpolish(widget)
            widget.style().polish(widget)

    def update_ui_metrics(self, target_goal, reps_left, time_left, is_active, feedback):
        """Updates all the live metric cards and the feedback/status labels."""
        self.goal_card.update_value(str(target_goal))
        self.progress_card.update_value(str(reps_left))
        
        minutes = int(time_left) // 60
        seconds = int(time_left) % 60
        time_string = f"{minutes:02d}:{seconds:02d}"
        self.time_card.update_value(time_string)
        
        if time_left <= 10 and is_active:
            self.time_card.value_label.setProperty("class", "TimeWarning")
        else:
            self.time_card.value_label.setProperty("class", "")
        self.time_card.value_label.style().unpolish(self.time_card.value_label)
        self.time_card.value_label.style().polish(self.time_card.value_label)
        
        if feedback:
            self.feedback_label.setText(feedback)
            if "ERROR" in feedback or "FIX" in feedback:
                self.feedback_label.setProperty("class", "FeedbackError")
                self.status_label.setText("FIX FORM")
                self.status_label.setProperty("class", "StatusError")
            else:
                self.feedback_label.setProperty("class", "FeedbackNormal")
                if is_active:
                    self.status_label.setText("TRAINING")
                    self.status_label.setProperty("class", "StatusTraining")
        else:
            if not is_active:
                self.feedback_label.setText("Session paused or waiting...")
                self.feedback_label.setProperty("class", "FeedbackWaiting")

        for widget in [self.feedback_label, self.status_label]:
            widget.style().unpolish(widget)
            widget.style().polish(widget)

    def set_sos_ui(self, is_sos):
        """Switches the dashboard into (or out of) the SOS/emergency visual state."""
        if is_sos:
            self.status_label.setText("⚠️ SOS COUNTDOWN")
            self.status_label.setProperty("class", "StatusSos")
            self.feedback_label.setText("FALL DETECTED! Starting 10s emergency protocol. Please respond or move!")
            self.feedback_label.setProperty("class", "FeedbackSos")
        else:
            self.status_label.setText("TRAINING")
            self.status_label.setProperty("class", "StatusTraining")
            self.feedback_label.setProperty("class", "")
            
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)
        self.feedback_label.style().unpolish(self.feedback_label)
        self.feedback_label.style().polish(self.feedback_label)
