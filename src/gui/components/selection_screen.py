from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame, QStackedWidget, QRadioButton, QButtonGroup
from PyQt6.QtCore import Qt
from PyQt6.QtCore import pyqtSignal as Signal
from PyQt6.QtGui import QFont

class ExerciseCard(QFrame):
    clicked = Signal(object) 

    def __init__(self, name, description, icon_char="💪", accent_color="#00f3ff", allows_reps=True, allows_static=False):
        super().__init__()
        self.setFixedSize(260, 270)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.name = name
        self.allows_reps = allows_reps
        self.allows_static = allows_static
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(15, 20, 15, 20)
        layout.setSpacing(10)

        icon_label = QLabel(icon_char)
        icon_label.setFont(QFont("Segoe UI", 36))
        icon_label.setStyleSheet("background: transparent; border: none; padding: 0px;")
        layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignCenter)

        title = QLabel(name.upper())
        title.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        title.setStyleSheet("color: #f1f5f9; background: transparent; border: none; margin-top: 5px;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        desc = QLabel(description)
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("color: #94a3b8; font-size: 12px; background: transparent; border: none; line-height: 14px;")
        layout.addWidget(desc)

        self.select_btn = QPushButton("SELECT")
        self.select_btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.select_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.select_btn.setFixedWidth(140)
        self.select_btn.setStyleSheet(f"""
            QPushButton {{ background-color: {accent_color}; color: #080b0e; border: none; padding: 8px; border-radius: 6px; margin-top: 5px; }}
            QPushButton:hover {{ background-color: #ffffff; }}
        """)
        self.select_btn.clicked.connect(lambda: self.clicked.emit(self))
        layout.addWidget(self.select_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setStyleSheet(f"""
            QFrame {{ background-color: #11161b; border: 1px solid #222d37; border-radius: 14px; }}
            QFrame:hover {{ border: 1px solid {accent_color}; background-color: #151b22; }}
        """)

    def mousePressEvent(self, event):
        self.clicked.emit(self)


class SelectionScreen(QWidget):
    launch_workout = Signal(dict)
    logout_clicked = Signal()

    def __init__(self):
        super().__init__()
        
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(40, 20, 40, 20) # איוורור שוליים עליונים
        main_layout.setSpacing(15)

        header_wrapper = QWidget()
        header_layout = QHBoxLayout(header_wrapper)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.addStretch(1)
        
        self.welcome_label = QLabel("AI NEXUS COACH")
        self.welcome_label.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        self.welcome_label.setStyleSheet("color: #f8fafc; letter-spacing: 5px;")
        header_layout.addWidget(self.welcome_label, alignment=Qt.AlignmentFlag.AlignCenter)
        header_layout.addStretch(1)
        
        self.logout_btn = QPushButton("LOG OUT")
        self.logout_btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.logout_btn.setFixedWidth(90)
        self.logout_btn.setStyleSheet("""
            QPushButton { color: #cbd5e1; background-color: transparent; border: 1px solid #334155; padding: 6px 10px; border-radius: 5px; }
            QPushButton:hover { border: 1px solid #f1f5f9; background-color: #1e293b; color: #ffffff; }
        """)
        self.logout_btn.clicked.connect(self.logout_clicked.emit)
        header_layout.addWidget(self.logout_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        main_layout.addWidget(header_wrapper)

        self.sub_label = QLabel("CHOOSE YOUR PROGRAM")
        self.sub_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.sub_label.setStyleSheet("color: #00f3ff; letter-spacing: 2px;")
        main_layout.addWidget(self.sub_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack)

        self.cards_widget = QWidget()
        cards_layout = QHBoxLayout(self.cards_widget)
        cards_layout.setSpacing(25)
        cards_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # יצירת ארבעת כרטיסי התרגילים (התרגיל החדש שלך שולב כאן ככרטיס חזרות!)
        self.bicep_card = ExerciseCard("Bicep Curls", "Build arm strength with real-time posture monitoring.", "💪", "#00f3ff", allows_reps=True, allows_static=False)
        self.knee_card = ExerciseCard("Knee Extension", "Master your Développé control and leg extension posture.", "🩰", "#00ff66", allows_reps=True, allows_static=False)
        self.squat_card = ExerciseCard("Squats", "Master your form, depth, and lower body power.", "🏋️", "#ff007f", allows_reps=True, allows_static=True)
        self.plank_card = ExerciseCard("Plank Hold", "Core alignment and trunk stability static tracker.", "⏳", "#f1c40f", allows_reps=False, allows_static=True)

        # חיבור אירוע הלחיצה (clicked) של כל הכרטיסים אל פונקציית הבחירה
        self.bicep_card.clicked.connect(self.select_exercise)
        self.knee_card.clicked.connect(self.select_exercise)
        self.squat_card.clicked.connect(self.select_exercise)
        self.plank_card.clicked.connect(self.select_exercise)

        # הוספת הכרטיסים לסידור הרוחבי (Layout) על המסך
        cards_layout.addWidget(self.bicep_card)
        cards_layout.addWidget(self.knee_card)
        cards_layout.addWidget(self.squat_card)
        cards_layout.addWidget(self.plank_card)
        self.content_stack.addWidget(self.cards_widget)

        # --- מסך הזנת יעד מאוורר וגמיש (מונע דחיסה) ---
        self.goal_widget = QWidget()
        goal_layout = QVBoxLayout(self.goal_widget)
        goal_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        goal_layout.setSpacing(12) 

        self.selected_title = QLabel("SELECTED PROGRAM")
        self.selected_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.selected_title.setStyleSheet("color: #f1f5f9; margin-bottom: 5px;")
        goal_layout.addWidget(self.selected_title, alignment=Qt.AlignmentFlag.AlignCenter)

        self.mode_container = QWidget()
        mode_layout = QHBoxLayout(self.mode_container)
        mode_layout.setContentsMargins(0, 0, 0, 0)
        mode_layout.setSpacing(20)
        
        self.mode_group = QButtonGroup(self)
        self.rb_reps = QRadioButton("Count Reps")
        self.rb_static = QRadioButton("Static Hold")
        
        radio_style = """
            QRadioButton { color: #94a3b8; font-size: 13px; background: transparent; }
            QRadioButton:checked { color: #00f3ff; font-weight: bold; }
        """
        for rb in [self.rb_reps, self.rb_static]:
            rb.setStyleSheet(radio_style)
            self.mode_group.addButton(rb)
            mode_layout.addWidget(rb)
            
        self.rb_reps.toggled.connect(self.adjust_input_fields_visibility)
        goal_layout.addWidget(self.mode_container, alignment=Qt.AlignmentFlag.AlignCenter)

        label_style = "color: #8a99a6; font-size: 11px; font-weight: bold; letter-spacing: 0.5px; margin-top: 4px;"
        
        self.reps_label = QLabel("🎯 REPS TO BEAT:")
        self.reps_label.setStyleSheet(label_style)
        goal_layout.addWidget(self.reps_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.input_field = QLineEdit()
        self.input_field.setFixedWidth(280) 
        goal_layout.addWidget(self.input_field, alignment=Qt.AlignmentFlag.AlignCenter)

        self.time_label = QLabel("⚡ BEAT THE CLOCK (SECONDS):")
        self.time_label.setStyleSheet(label_style)
        goal_layout.addWidget(self.time_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.time_field = QLineEdit()
        self.time_field.setFixedWidth(280) 
        goal_layout.addWidget(self.time_field, alignment=Qt.AlignmentFlag.AlignCenter)

        fields_style = """
            QLineEdit {
                padding: 11px;
                font-size: 13px;
                border: 1px solid #222d37;
                border-radius: 8px;
                background-color: #11161b;
                color: #f1f5f9;
            }
            QLineEdit:focus { border: 1px solid #00f3ff; }
        """
        self.input_field.setStyleSheet(fields_style)
        self.time_field.setStyleSheet(fields_style)

        self.start_btn = QPushButton("LAUNCH TRAINING SESSION")
        self.start_btn.setFixedWidth(280)
        self.start_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_btn.setStyleSheet("""
            QPushButton { background-color: #00f3ff; color: #080b0e; padding: 14px; border-radius: 8px; border: none; margin-top: 15px; }
            QPushButton:hover { background-color: #00bfff; }
        """)
        self.start_btn.clicked.connect(self.emit_launch)
        goal_layout.addWidget(self.start_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.back_btn = QPushButton("← Back to Exercises")
        self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_btn.setStyleSheet("color: #8a99a6; background: transparent; border: none; font-size: 13px; margin-top: 5px;")
        self.back_btn.clicked.connect(self.go_back_to_cards)
        goal_layout.addWidget(self.back_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.content_stack.addWidget(self.goal_widget)
        self.current_card = None

    def select_exercise(self, card_object):
        self.current_card = card_object
        self.selected_title.setText(f"SELECTED PROGRAM: {card_object.name.upper()}")
        self.sub_label.setText("CONFIGURE YOUR TARGETS")
        
        self.input_field.clear()
        self.time_field.setText("60") 
        
        if card_object.allows_reps and card_object.allows_static:
            self.mode_container.setVisible(True)
            self.rb_reps.setChecked(True)
            self.input_field.setText("30") 
        else:
            self.mode_container.setVisible(False)
            if card_object.allows_reps:
                self.rb_reps.setChecked(True)
                self.input_field.setText("30")
            else:
                self.rb_static.setChecked(True)
                
        self.adjust_input_fields_visibility()
        self.content_stack.setCurrentIndex(1)
        self.logout_btn.setVisible(False)

    def adjust_input_fields_visibility(self):
        if self.rb_reps.isChecked():
            self.reps_label.setVisible(True)
            self.input_field.setVisible(True)
            self.reps_label.setText("🎯 REPS TO BEAT:")
            self.time_label.setText("⚡ BEAT THE CLOCK (SECONDS):")
        else:
            self.reps_label.setVisible(False)
            self.input_field.setVisible(False)
            self.time_label.setText("🔥 HOLD UNTIL DETONATION (SECONDS):")

    def go_back_to_cards(self):
        self.sub_label.setText("CHOOSE YOUR PROGRAM")
        self.content_stack.setCurrentIndex(0)
        self.logout_btn.setVisible(True)

    def emit_launch(self):
        if not self.current_card: return
        
        mode = "reps" if self.rb_reps.isChecked() else "static"
        time_text = self.time_field.text().strip()
        rep_text = self.input_field.text().strip()
        
        if not time_text.isdigit() or int(time_text) <= 0:
            return
            
        target_goal = int(rep_text) if (mode == "reps" and rep_text.isdigit()) else int(time_text)
        
        config = {
            "exercise_name": self.current_card.name,
            "mode": mode,
            "target_goal": target_goal,
            "time_limit": int(time_text)
        }
        
        self.launch_workout.emit(config)
        self.logout_btn.setVisible(True)











# from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame, QStackedWidget, QRadioButton, QButtonGroup
# from PyQt6.QtCore import Qt
# from PyQt6.QtCore import pyqtSignal as Signal
# from PyQt6.QtGui import QFont

# class ExerciseCard(QFrame):
#     clicked = Signal(object) 

#     def __init__(self, name, description, icon_char="💪", accent_color="#00f3ff", allows_reps=True, allows_static=False):
#         super().__init__()
#         self.setFixedSize(260, 270)
#         self.setCursor(Qt.CursorShape.PointingHandCursor)
#         self.name = name
#         self.allows_reps = allows_reps
#         self.allows_static = allows_static
        
#         layout = QVBoxLayout(self)
#         layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         layout.setContentsMargins(15, 20, 15, 20)
#         layout.setSpacing(10)

#         icon_label = QLabel(icon_char)
#         icon_label.setFont(QFont("Segoe UI", 36))
#         icon_label.setStyleSheet("background: transparent; border: none; padding: 0px;")
#         layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignCenter)

#         title = QLabel(name.upper())
#         title.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
#         title.setStyleSheet("color: #f1f5f9; background: transparent; border: none; margin-top: 5px;")
#         layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

#         desc = QLabel(description)
#         desc.setWordWrap(True)
#         desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         desc.setStyleSheet("color: #94a3b8; font-size: 12px; background: transparent; border: none; line-height: 14px;")
#         layout.addWidget(desc)

#         self.select_btn = QPushButton("SELECT")
#         self.select_btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
#         self.select_btn.setCursor(Qt.CursorShape.PointingHandCursor)
#         self.select_btn.setFixedWidth(140)
#         self.select_btn.setStyleSheet(f"""
#             QPushButton {{ background-color: {accent_color}; color: #080b0e; border: none; padding: 8px; border-radius: 6px; margin-top: 5px; }}
#             QPushButton:hover {{ background-color: #ffffff; }}
#         """)
#         self.select_btn.clicked.connect(lambda: self.clicked.emit(self))
#         layout.addWidget(self.select_btn, alignment=Qt.AlignmentFlag.AlignCenter)

#         self.setStyleSheet(f"""
#             QFrame {{ background-color: #11161b; border: 1px solid #222d37; border-radius: 14px; }}
#             QFrame:hover {{ border: 1px solid {accent_color}; background-color: #151b22; }}
#         """)

#     def mousePressEvent(self, event):
#         self.clicked.emit(self)


# class SelectionScreen(QWidget):
#     launch_workout = Signal(dict)
#     logout_clicked = Signal()

#     def __init__(self):
#         super().__init__()
        
#         main_layout = QVBoxLayout(self)
#         main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         main_layout.setContentsMargins(40, 20, 40, 20) # איוורור שוליים עליונים
#         main_layout.setSpacing(15)

#         header_wrapper = QWidget()
#         header_layout = QHBoxLayout(header_wrapper)
#         header_layout.setContentsMargins(0, 0, 0, 0)
#         header_layout.addStretch(1)
        
#         self.welcome_label = QLabel("AI NEXUS COACH")
#         self.welcome_label.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
#         self.welcome_label.setStyleSheet("color: #f8fafc; letter-spacing: 5px;")
#         header_layout.addWidget(self.welcome_label, alignment=Qt.AlignmentFlag.AlignCenter)
#         header_layout.addStretch(1)
        
#         self.logout_btn = QPushButton("LOG OUT")
#         self.logout_btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
#         self.logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
#         self.logout_btn.setFixedWidth(90)
#         self.logout_btn.setStyleSheet("""
#             QPushButton { color: #cbd5e1; background-color: transparent; border: 1px solid #334155; padding: 6px 10px; border-radius: 5px; }
#             QPushButton:hover { border: 1px solid #f1f5f9; background-color: #1e293b; color: #ffffff; }
#         """)
#         self.logout_btn.clicked.connect(self.logout_clicked.emit)
#         header_layout.addWidget(self.logout_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
#         main_layout.addWidget(header_wrapper)

#         self.sub_label = QLabel("CHOOSE YOUR PROGRAM")
#         self.sub_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
#         self.sub_label.setStyleSheet("color: #00f3ff; letter-spacing: 2px;")
#         main_layout.addWidget(self.sub_label, alignment=Qt.AlignmentFlag.AlignCenter)

#         self.content_stack = QStackedWidget()
#         main_layout.addWidget(self.content_stack)

#         self.cards_widget = QWidget()
#         cards_layout = QHBoxLayout(self.cards_widget)
#         cards_layout.setSpacing(25)
#         cards_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

#         self.bicep_card = ExerciseCard("Bicep Curls", "Build arm strength with real-time posture monitoring.", "💪", "#00f3ff", allows_reps=True, allows_static=False)
#         self.squat_card = ExerciseCard("Squats", "Master your form, depth, and lower body power.", "🦵", "#00ff66", allows_reps=True, allows_static=True)
#         self.plank_card = ExerciseCard("Plank Hold", "Core alignment and trunk stability static tracker.", "⏳", "#f1c40f", allows_reps=False, allows_static=True)

#         self.bicep_card.clicked.connect(self.select_exercise)
#         self.squat_card.clicked.connect(self.select_exercise)
#         self.plank_card.clicked.connect(self.select_exercise)

#         cards_layout.addWidget(self.bicep_card)
#         cards_layout.addWidget(self.squat_card)
#         cards_layout.addWidget(self.plank_card)
#         self.content_stack.addWidget(self.cards_widget)

#         # --- מסך הזנת יעד מאוורר וגמיש (מונע דחיסה) ---
#         self.goal_widget = QWidget()
#         goal_layout = QVBoxLayout(self.goal_widget)
#         goal_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         goal_layout.setSpacing(12) # הגדלת המרווח הפנימי בין תיבה לתיבה!

#         self.selected_title = QLabel("SELECTED PROGRAM")
#         self.selected_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
#         self.selected_title.setStyleSheet("color: #f1f5f9; margin-bottom: 5px;")
#         goal_layout.addWidget(self.selected_title, alignment=Qt.AlignmentFlag.AlignCenter)

#         self.mode_container = QWidget()
#         mode_layout = QHBoxLayout(self.mode_container)
#         mode_layout.setContentsMargins(0, 0, 0, 0)
#         mode_layout.setSpacing(20)
        
#         self.mode_group = QButtonGroup(self)
#         self.rb_reps = QRadioButton("Count Reps")
#         self.rb_static = QRadioButton("Static Hold")
        
#         radio_style = """
#             QRadioButton { color: #94a3b8; font-size: 13px; background: transparent; }
#             QRadioButton:checked { color: #00f3ff; font-weight: bold; }
#         """
#         for rb in [self.rb_reps, self.rb_static]:
#             rb.setStyleSheet(radio_style)
#             self.mode_group.addButton(rb)
#             mode_layout.addWidget(rb)
            
#         self.rb_reps.toggled.connect(self.adjust_input_fields_visibility)
#         goal_layout.addWidget(self.mode_container, alignment=Qt.AlignmentFlag.AlignCenter)

#         # כותרות הסבר יוקרתיות ומרווחות מעל המלבנים
#         label_style = "color: #8a99a6; font-size: 11px; font-weight: bold; letter-spacing: 0.5px; margin-top: 4px;"
        
#         self.reps_label = QLabel("🎯 REPS TO BEAT:")
#         self.reps_label.setStyleSheet(label_style)
#         goal_layout.addWidget(self.reps_label, alignment=Qt.AlignmentFlag.AlignCenter)

#         self.input_field = QLineEdit()
#         self.input_field.setFixedWidth(280) # הרחבה קלה של המלבן ל-280
#         goal_layout.addWidget(self.input_field, alignment=Qt.AlignmentFlag.AlignCenter)

#         self.time_label = QLabel("⚡ BEAT THE CLOCK (SECONDS):")
#         self.time_label.setStyleSheet(label_style)
#         goal_layout.addWidget(self.time_label, alignment=Qt.AlignmentFlag.AlignCenter)

#         self.time_field = QLineEdit()
#         self.time_field.setFixedWidth(280) # הרחבה קלה של המלבן ל-280
#         goal_layout.addWidget(self.time_field, alignment=Qt.AlignmentFlag.AlignCenter)

#         fields_style = """
#             QLineEdit {
#                 padding: 11px;
#                 font-size: 13px;
#                 border: 1px solid #222d37;
#                 border-radius: 8px;
#                 background-color: #11161b;
#                 color: #f1f5f9;
#             }
#             QLineEdit:focus { border: 1px solid #00f3ff; }
#         """
#         self.input_field.setStyleSheet(fields_style)
#         self.time_field.setStyleSheet(fields_style)

#         self.start_btn = QPushButton("LAUNCH TRAINING SESSION")
#         self.start_btn.setFixedWidth(280)
#         self.start_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
#         self.start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
#         self.start_btn.setStyleSheet("""
#             QPushButton { background-color: #00f3ff; color: #080b0e; padding: 14px; border-radius: 8px; border: none; margin-top: 15px; }
#             QPushButton:hover { background-color: #00bfff; }
#         """)
#         self.start_btn.clicked.connect(self.emit_launch)
#         goal_layout.addWidget(self.start_btn, alignment=Qt.AlignmentFlag.AlignCenter)

#         self.back_btn = QPushButton("← Back to Exercises")
#         self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
#         self.back_btn.setStyleSheet("color: #8a99a6; background: transparent; border: none; font-size: 13px; margin-top: 5px;")
#         self.back_btn.clicked.connect(self.go_back_to_cards)
#         goal_layout.addWidget(self.back_btn, alignment=Qt.AlignmentFlag.AlignCenter)

#         self.content_stack.addWidget(self.goal_widget)
#         self.current_card = None

#     def select_exercise(self, card_object):
#         self.current_card = card_object
#         self.selected_title.setText(f"SELECTED PROGRAM: {card_object.name.upper()}")
#         self.sub_label.setText("CONFIGURE YOUR TARGETS")
        
#         self.input_field.clear()
#         self.time_field.setText("60") 
        
#         if card_object.allows_reps and card_object.allows_static:
#             self.mode_container.setVisible(True)
#             self.rb_reps.setChecked(True)
#             self.input_field.setText("30") 
#         else:
#             self.mode_container.setVisible(False)
#             if card_object.allows_reps:
#                 self.rb_reps.setChecked(True)
#                 self.input_field.setText("30")
#             else:
#                 self.rb_static.setChecked(True)
                
#         self.adjust_input_fields_visibility()
#         self.content_stack.setCurrentIndex(1)
#         self.logout_btn.setVisible(False)

#     def adjust_input_fields_visibility(self):
#         if self.rb_reps.isChecked():
#             self.reps_label.setVisible(True)
#             self.input_field.setVisible(True)
#             self.reps_label.setText("🎯 REPS TO BEAT:")
#             self.time_label.setText("⚡ BEAT THE CLOCK (SECONDS):")
#         else:
#             self.reps_label.setVisible(False)
#             self.input_field.setVisible(False)
#             self.time_label.setText("🔥 HOLD UNTIL DETONATION (SECONDS):")

#     def go_back_to_cards(self):
#         self.sub_label.setText("CHOOSE YOUR PROGRAM")
#         self.content_stack.setCurrentIndex(0)
#         self.logout_btn.setVisible(True)

#     def emit_launch(self):
#         if not self.current_card: return
        
#         mode = "reps" if self.rb_reps.isChecked() else "static"
#         time_text = self.time_field.text().strip()
#         rep_text = self.input_field.text().strip()
        
#         if not time_text.isdigit() or int(time_text) <= 0:
#             return
            
#         target_goal = int(rep_text) if (mode == "reps" and rep_text.isdigit()) else int(time_text)
        
#         config = {
#             "exercise_name": self.current_card.name,
#             "mode": mode,
#             "target_goal": target_goal,
#             "time_limit": int(time_text)
#         }
        
#         self.launch_workout.emit(config)
#         self.logout_btn.setVisible(True)

