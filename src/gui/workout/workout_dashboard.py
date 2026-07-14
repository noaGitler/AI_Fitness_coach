# from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QLineEdit, QPushButton
# from PyQt6.QtCore import Qt
# from PyQt6.QtGui import QFont
# from src.gui.components.stats_card import StatsCard

# class WorkoutDashboard(QFrame):
#     def __init__(self, parent=None):
#         super().__init__(parent)
        
#         layout = QVBoxLayout(self)
#         layout.setContentsMargins(15, 20, 15, 20)
#         layout.setSpacing(15)
#         layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
#         self.status_title = QLabel("WORKOUT STATUS")
#         self.status_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
#         self.status_title.setStyleSheet("color: #8a99a6; background: transparent; border: none;")
#         layout.addWidget(self.status_title)
        
#         self.status_label = QLabel("READY")
#         self.status_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
#         self.status_label.setStyleSheet("color: #00ff66; background: transparent; border: none;")
#         layout.addWidget(self.status_label)
        
#         self.goal_card = StatsCard("Target Goal", "0", self)
#         self.left_card = StatsCard("Reps Remaining", "0", self)
#         self.angle_card = StatsCard("Elbow Angle", "0°", self)
        
#         layout.addWidget(self.goal_card)
#         layout.addWidget(self.left_card)
#         layout.addWidget(self.angle_card)
        
#         self.goal_input = QLineEdit(self)
#         self.set_goal_btn = QPushButton("LAUNCH WORKOUT", self)
#         self.goal_input.setVisible(False)
#         self.set_goal_btn.setVisible(False)
        
#         # תיקון סופי לדשבורד: מגדירים במפורש ל-QFrame!
#         self.setStyleSheet("""
#             QFrame {
#                 background-color: #101418;
#                 border-radius: 12px;
#                 border: 1px solid #1c232a;
#             }
#         """)

#     def update_ui_metrics(self, target_goal, reps_left, current_angle, is_active, feedback):
#         self.goal_card.update_value(target_goal)
#         self.left_card.update_value(reps_left)
#         self.angle_card.update_value(f"{int(current_angle)}°" if current_angle > 0 else "0°")
        
#         if feedback and "ERROR" in feedback:
#             self.status_label.setText("ERROR")
#             self.status_label.setStyleSheet("color: #ff3333; background: transparent; border: none;")
#         elif is_active:
#             self.status_label.setText("TRAINING")
#             self.status_label.setStyleSheet("color: #00f3ff; background: transparent; border: none;")
#         else:
#             self.status_label.setText("READY")
#             self.status_label.setStyleSheet("color: #00ff66; background: transparent; border: none;")











# from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QLineEdit, QPushButton
# from PyQt6.QtCore import Qt
# from PyQt6.QtGui import QFont
# from src.gui.components.stats_card import StatsCard

# class WorkoutDashboard(QFrame):
#     def __init__(self, parent=None):
#         super().__init__(parent)
        
#         layout = QVBoxLayout(self)
#         layout.setContentsMargins(10, 0, 10, 0)
#         layout.setSpacing(15)
#         layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
#         self.status_title = QLabel("WORKOUT STATUS")
#         self.status_title.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
#         self.status_title.setStyleSheet("color: #8a99a6; background: transparent; border: none;")
#         layout.addWidget(self.status_title)
        
#         self.status_label = QLabel("READY")
#         self.status_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
#         self.status_label.setStyleSheet("color: #00ff66; background: transparent; border: none;")
#         layout.addWidget(self.status_label)
        
#         self.goal_card = StatsCard("Target Goal", "0", self)
#         self.left_card = StatsCard("Reps Remaining", "0", self)
#         self.angle_card = StatsCard("Elbow Angle", "0°", self)
        
#         layout.addWidget(self.goal_card)
#         layout.addWidget(self.left_card)
#         layout.addWidget(self.angle_card)

#         self.feedback_label = QLabel("Waiting for movement pattern...")
#         self.feedback_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
#         self.feedback_label.setWordWrap(True)
#         self.feedback_label.setMinimumHeight(70)
#         self.feedback_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
#         self.feedback_label.setStyleSheet("color: #e2e8f0; background: transparent; border: none; line-height: 16px;")
#         layout.addWidget(self.feedback_label)
        
#         # --- הוספת כפתור ה-PAUSE / RESUME החדש למערכת ---
#         self.pause_btn = QPushButton("PAUSE", self)
#         self.pause_btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
#         self.pause_btn.setCursor(Qt.CursorShape.PointingHandCursor)
#         self.pause_btn.setStyleSheet("""
#             QPushButton {
#                 color: #00f3ff;
#                 background: transparent;
#                 border: 1px solid #00f3ff;
#                 padding: 8px;
#                 border-radius: 5px;
#                 margin-top: 10px;
#             }
#             QPushButton:hover { background-color: #09252c; color: #ffffff; }
#         """)
#         layout.addWidget(self.pause_btn)

#         # כפתור ה-QUIT המקורי שלכן (שומר על העיצוב המקורי)
#         self.exit_session_btn = QPushButton("QUIT", self)
#         self.exit_session_btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
#         self.exit_session_btn.setCursor(Qt.CursorShape.PointingHandCursor)
#         self.exit_session_btn.setStyleSheet("""
#             QPushButton {
#                 color: #ff3333;
#                 background: transparent;
#                 border: 1px solid #ff3333;
#                 padding: 8px;
#                 border-radius: 5px;
#                 margin-top: 5px;
#             }
#             QPushButton:hover { background-color: #2a1111; }
#         """)
#         layout.addWidget(self.exit_session_btn)
        
#         # layout.addWidget(self.pause_btn)
#         # layout.addWidget(self.exit_session_btn)
        
#         # self.goal_input = QLineEdit(self)
#         # self.set_goal_btn = QPushButton("LAUNCH WORKOUT", self)
#         # self.goal_input.setVisible(False)
#         # self.set_goal_btn.setVisible(False)
        
#         # self.setStyleSheet("""
#         #     QFrame {
#         #         background-color: #101418;
#         #         border-radius: 12px;
#         #         border: 1px solid #1c232a;
#         #     }
#         # """)


#     def set_paused_ui(self, is_paused):
#         """משנה את הנראות והצבעים של כפתור העצירה בלייב"""
#         if is_paused:
#             self.pause_btn.setText("RESUME")
#             self.pause_btn.setStyleSheet("""
#                 QPushButton {
#                     color: #0c0f12;
#                     background-color: #00ff66;
#                     border: none;
#                     padding: 8px;
#                     border-radius: 5px;
#                     margin-top: 10px;
#                 }
#                 QPushButton:hover { background-color: #ffffff; }
#             """)
#         else:
#             self.pause_btn.setText("PAUSE")
#             self.pause_btn.setStyleSheet("""
#                 QPushButton {
#                     color: #00f3ff;
#                     background: transparent;
#                     border: 1px solid #00f3ff;
#                     padding: 8px;
#                     border-radius: 5px;
#                     margin-top: 10px;
#                 }
#                 QPushButton:hover { background-color: #09252c; color: #ffffff; }
#             """)

#     # def update_ui_metrics(self, target_goal, reps_left, current_angle, is_active, feedback):
#     #     self.goal_card.update_value(target_goal)
#     #     self.left_card.update_value(reps_left)
#     #     self.angle_card.update_value(f"{int(current_angle)}°" if current_angle > 0 else "0°")
        
#     #     if feedback and "ERROR" in feedback:
#     #         self.status_label.setText("ERROR")
#     #         self.status_label.setStyleSheet("color: #ff3333; background: transparent; border: none;")
#     #     elif is_active:
#     #         self.status_label.setText("TRAINING")
#     #         self.status_label.setStyleSheet("color: #00f3ff; background: transparent; border: none;")
#     #     else:
#     #         self.status_label.setText("READY")
#     #         self.status_label.setStyleSheet("color: #00ff66; background: transparent; border: none;")

#     # def set_paused_ui(self, is_paused):
#     #     """פונקציה שמשנה את עיצוב כפתור ההשהיה כשהאימון מוקפא"""
#     #     if is_paused:
#     #         self.pause_btn.setText("RESUME")
#     #         self.pause_btn.setStyleSheet("""
#     #             QPushButton { background-color: #2ecc71; color: #101418; padding: 12px; border-radius: 6px; border: none; }
#     #             QPushButton:hover { background-color: #27ae60; }
#     #         """)
#     #     else:
#     #         self.pause_btn.setText("PAUSE")
#     #         self.pause_btn.setStyleSheet("""
#     #             QPushButton { background-color: #f1c40f; color: #101418; padding: 12px; border-radius: 6px; border: none; }
#     #             QPushButton:hover { background-color: #f39c12; }
#     #         """)

#     def update_ui_metrics(self, target_goal, reps_left, time_left, is_active, feedback):
#         """מעדכן את כל המדדים תוך שימוש בפונקציית update_value המקורית שלכן"""
#         self.goal_card.update_value(str(target_goal))
#         self.progress_card.update_value(str(reps_left))
        
#         minutes = time_left // 60
#         seconds = time_left % 60
#         time_string = f"{minutes:02d}:{seconds:02d}"
#         self.time_card.update_value(time_string)
        
#         if time_left <= 10 and is_active:
#             self.time_card.value_label.setStyleSheet("color: #ff3333; font-weight: bold;")
#         else:
#             self.time_card.value_label.setStyleSheet("color: #e2e8f0; font-weight: bold;")

#         if feedback:
#             self.feedback_label.setText(feedback)
#             if "ERROR" in feedback or "FIX" in feedback:
#                 self.feedback_label.setStyleSheet("color: #ff3333; font-weight: bold; background: transparent; border: none;")
#             else:
#                 self.feedback_label.setStyleSheet("color: #00ff66; font-weight: bold; background: transparent; border: none;")
#         else:
#             if not is_active:
#                 self.feedback_label.setText("Session paused or waiting...")
#                 self.feedback_label.setStyleSheet("color: #8a99a6; background: transparent; border: none;")










from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from src.gui.components.stats_card import StatsCard

class WorkoutDashboard(QFrame):
    """לוח מדדים מעוצב בלייב - כולל טיימר/מדדים וכפתורי שליטה דינמיים"""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 15, 10, 15)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # 1. סטטוס המערכת
        self.status_title = QLabel("WORKOUT STATUS")
        self.status_title.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.status_title.setStyleSheet("color: #8a99a6; background: transparent; border: none;")
        layout.addWidget(self.status_title)
        
        self.status_label = QLabel("READY")
        self.status_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.status_label.setStyleSheet("color: #00ff66; background: transparent; border: none;")
        layout.addWidget(self.status_label)
        
        # 2. קוביות המדדים המעודכנות
        self.goal_card = StatsCard("Target Goal", "0", self)
        self.progress_card = StatsCard("Reps Remaining", "0", self)
        self.time_card = StatsCard("Session Time Left", "00:00", self)
        
        layout.addWidget(self.goal_card)
        layout.addWidget(self.progress_card)
        layout.addWidget(self.time_card)

        # 3. אזור הפידבק של ה-AI בזמן אמת
        self.feedback_title = QLabel("AI REAL-TIME FEEDBACK")
        self.feedback_title.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.feedback_title.setStyleSheet("color: #8a99a6; letter-spacing: 1px; background: transparent; border: none; margin-top: 10px;")
        layout.addWidget(self.feedback_title)

        self.feedback_label = QLabel("Waiting for movement pattern...")
        self.feedback_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.feedback_label.setWordWrap(True)
        self.feedback_label.setMinimumHeight(70)
        self.feedback_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.feedback_label.setStyleSheet("color: #e2e8f0; background: transparent; border: none; line-height: 16px;")
        layout.addWidget(self.feedback_label)
        
        # 4. כפתור ה-PAUSE / RESUME המעוצב
        self.pause_btn = QPushButton("PAUSE", self)
        self.pause_btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.pause_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.pause_btn.setStyleSheet("""
            QPushButton {
                color: #00f3ff;
                background: transparent;
                border: 1px solid #00f3ff;
                padding: 8px;
                border-radius: 5px;
                margin-top: 10px;
            }
            QPushButton:hover { background-color: #09252c; color: #ffffff; }
        """)
        layout.addWidget(self.pause_btn)

        # 5. כפתור ה-QUIT לסיום האימון
        self.exit_session_btn = QPushButton("QUIT", self)
        self.exit_session_btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.exit_session_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.exit_session_btn.setStyleSheet("""
            QPushButton {
                color: #ff3333;
                background: transparent;
                border: 1px solid #ff3333;
                padding: 8px;
                border-radius: 5px;
                margin-top: 5px;
            }
            QPushButton:hover { background-color: #2a1111; }
        """)
        layout.addWidget(self.exit_session_btn)
        
        # סגנון ה-Frame הכללי של הדשבורד
        self.setStyleSheet("""
            QFrame {
                background-color: #101418;
                border-radius: 12px;
                border: 1px solid #1c232a;
            }
        """)

    def set_paused_ui(self, is_paused):
        """משנה את הנראות והצבעים של כפתור העצירה בלייב"""
        if is_paused:
            self.pause_btn.setText("RESUME")
            self.pause_btn.setStyleSheet("""
                QPushButton {
                    color: #0c0f12;
                    background-color: #00ff66;
                    border: none;
                    padding: 8px;
                    border-radius: 5px;
                    margin-top: 10px;
                }
                QPushButton:hover { background-color: #ffffff; }
            """)
            self.status_label.setText("PAUSED")
            self.status_label.setStyleSheet("color: #f1c40f; background: transparent; border: none;")
        else:
            self.pause_btn.setText("PAUSE")
            self.pause_btn.setStyleSheet("""
                QPushButton {
                    color: #00f3ff;
                    background: transparent;
                    border: 1px solid #00f3ff;
                    padding: 8px;
                    border-radius: 5px;
                    margin-top: 10px;
                }
                QPushButton:hover { background-color: #09252c; color: #ffffff; }
            """)
            self.status_label.setText("TRAINING")
            self.status_label.setStyleSheet("color: #00f3ff; background: transparent; border: none;")

    def update_ui_metrics(self, target_goal, reps_left, time_left, is_active, feedback):
        """מעדכן את כל המדדים בצורה בטוחה ומסונכרנת עם ה-MainWindow"""
        self.goal_card.update_value(str(target_goal))
        self.progress_card.update_value(str(reps_left))
        
        # חישוב הפורמט של הזמן (דקות:שניות) מהשניות שנותרו
        minutes = int(time_left) // 60
        seconds = int(time_left) % 60
        time_string = f"{minutes:02d}:{seconds:02d}"
        self.time_card.update_value(time_string)
        
        # צביעת הטיק של ה-10 שניות האחרונות באדום להתרעה עיצובית חכמה
        if time_left <= 10 and is_active:
            self.time_card.value_label.setStyleSheet("color: #ff3333; font-weight: bold; background: transparent;")
        else:
            self.time_card.value_label.setStyleSheet("color: #e2e8f0; font-weight: bold; background: transparent;")
        
        # ניהול צבעי פידבק וסטטוס דינמיים
        if feedback:
            self.feedback_label.setText(feedback)
            if "ERROR" in feedback or "FIX" in feedback:
                self.feedback_label.setStyleSheet("color: #ff3333; font-weight: bold; background: transparent; border: none;")
                self.status_label.setText("FIX FORM")
                self.status_label.setStyleSheet("color: #ff3333; background: transparent; border: none;")
            else:
                self.feedback_label.setStyleSheet("color: #00ff66; font-weight: bold; background: transparent; border: none;")
                if is_active:
                    self.status_label.setText("TRAINING")
                    self.status_label.setStyleSheet("color: #00f3ff; background: transparent; border: none;")
        else:
            if not is_active:
                self.feedback_label.setText("Session paused or waiting...")
                self.feedback_label.setStyleSheet("color: #8a99a6; background: transparent; border: none;")