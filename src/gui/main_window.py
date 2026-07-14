from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

# ייבוא המסכים והרכיבים המעוצבים שלך (העיצוב המקורי שלך נשמר במלואו!)
from src.gui.workout.video_widget import VideoWidget
from src.gui.workout.workout_dashboard import WorkoutDashboard
from src.gui.components.selection_screen import SelectionScreen
from src.gui.components.nexus_alert import NexusAlert
from src.gui.auth.auth_screens import LoginScreen, RegisterScreen

# ייבוא 5 המנג'רים האמיתיים שהעלית עכשיו
from src.gui.managers.timer_manager import TimerManager
from src.gui.managers.auth_manager import AuthManager
from src.gui.managers.location_manager import LocationManager
from src.gui.managers.voice_manager import VoiceManager
from src.gui.managers.session_manager import SessionManager
from src.gui.managers.emergency_manager import EmergencyManager

from src.ai.workout_worker import VideoWorker

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("AI NEXUS - Fitness Intelligence")
        self.setGeometry(100, 100, 1200, 750)
        self.setStyleSheet("background-color: #080b0e;")
        
        # אתחול ה-Worker של המצלמה וה-AI ברקע
        self.video_worker = VideoWorker()
        self.video_worker.main_window_ref = self
        self.video_worker.start()

        self.video_panel = VideoWidget(self)

        # אתחול 5 המנג'רים העצמאיים
        self.timer_manager = TimerManager()
        self.auth_manager = AuthManager()
        self.location_manager = LocationManager()
        self.voice_manager = VoiceManager()
        self.session_manager = SessionManager(self.video_worker)
        self.emergency_manager = EmergencyManager(self.video_panel)
        self.emergency_active = False
        
        # טיימר קטן שנשאר במיין אך ורק בשביל לנהל את הטיקים של ה-Get Ready במסך
        self.ui_countdown_timer = QTimer(self)
        self.ui_countdown_timer.timeout.connect(self.session_manager.handle_countdown_tick)

        # בניית המסכים והעברתם לתוך ה-StackedWidget
        self.pages = QStackedWidget()
        self.setCentralWidget(self.pages)
        
        self.login_page = LoginScreen()
        self.register_page = RegisterScreen()
        self.selection_page = SelectionScreen()
        self.workout_page = QWidget()
        self.setup_workout_ui()
        
        self.pages.addWidget(self.login_page)       # 0
        self.pages.addWidget(self.register_page)    # 1
        self.pages.addWidget(self.selection_page)   # 2
        self.pages.addWidget(self.workout_page)     # 3
        
        # חיבור רשת הצינורות (Signals) שמקשרת את המסכים למנג'רים
        self._connect_signals()


    def setup_workout_ui(self):
        layout = QVBoxLayout(self.workout_page)
        layout.setContentsMargins(15, 15, 15, 15)
        
        self.header_label = QLabel("AI SESSION ACTIVE")
        self.header_label.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        self.header_label.setStyleSheet("color: #ffffff; letter-spacing: 2px; margin-bottom: 10px;")
        layout.addWidget(self.header_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        content = QHBoxLayout()
        content.addWidget(self.video_panel, stretch=3)
        
        self.dashboard = WorkoutDashboard(self)
        self.dashboard.setFixedWidth(320)
        
        # חיבור כפתורי הדשבורד ישירות למנג'רים המתאימים להם
        self.dashboard.pause_btn.clicked.connect(self.timer_manager.toggle_pause)
        # self.dashboard.exit_session_btn.clicked.connect(self.session_manager.reset_and_clean_session)
        # השורה החדשה: מפעילה את פונקציית היציאה והחלפת המסכים המלאה של ה-GUI (כאילו האימון הסתיים בכישלון מתוכנן)
        self.dashboard.exit_session_btn.clicked.connect(lambda: self.handle_gui_session_timeout(is_success=False))
        
        content.addWidget(self.dashboard, stretch=1)
        layout.addLayout(content)

        # הוספת מנהל החירום הגרפי מעל פאנל הוידאו
        self.emergency_manager = EmergencyManager(self.video_panel)
        self.emergency_active = False # דגל ששומר אם אנחנו בחירום


    def _connect_signals(self):        
        # א) הזרמת הוידאו והמדדים מה-Worker למקומות החדשים שלהם
        self.video_worker.frame_ready.connect(self.video_panel.update_frame)
        self.video_worker.metrics_ready.connect(self.session_manager.process_live_metrics)

        # ב) חיבור דפי הלוגין והרגיסטר ל-AuthManager הלוגי
        self.login_page.login_requested.connect(self.auth_manager.login)
        self.login_page.go_to_register.connect(lambda: self.pages.setCurrentIndex(1))
        
        self.register_page.register_requested.connect(self.auth_manager.register)
        self.register_page.go_to_login.connect(lambda: self.pages.setCurrentIndex(0))
        
        self.selection_page.launch_workout.connect(self.session_manager.start_countdown_phase)
        self.selection_page.logout_clicked.connect(self.auth_manager.logout)
        
        # ג) המיין מקשיב לסטטוס האימות של ה-AuthManager ומעדכן את ה-GUI
        self.auth_manager.login_success.connect(self.handle_gui_login_success)
        self.auth_manager.login_failed.connect(lambda msg: self.login_page.error_label.setText(msg))
        self.auth_manager.registration_success.connect(self.handle_gui_registration_success)
        self.auth_manager.registration_failed.connect(lambda msg: self.register_page.error_label.setText(msg))
        self.auth_manager.login_failed.connect(lambda _: self.pages.setCurrentIndex(0)) # חזרה ללוגין ביציאה
        # חזרה למסך הלוגין ברגע שהתבצע ניתוק מאובטח בהצלחה
        self.auth_manager.logout_success.connect(lambda: self.pages.setCurrentIndex(0))

        # ד) המיין מקשיב למהלכי ה-Countdown של ה-SessionManager
        self.session_manager.countdown_tick_received.connect(self.handle_gui_countdown_tick)
        self.session_manager.countdown_finished.connect(self.handle_gui_countdown_finished)

        # ה) עדכון זמנים: טיק השעון ב-TimerManager מניע את הזמן בתוך ה-SessionManager
        self.timer_manager.time_updated.connect(lambda remaining_seconds: self.session_manager.handle_timer_tick())
        self.timer_manager.pause_state_changed.connect(self.handle_gui_pause_state_changed)
        # self.timer_manager.timeout_triggered.connect(self.session_manager.handle_timer_tick) # סנכרון סוף זמן

        # עדכוני מדדים בלייב וסיום האימון
        self.session_manager.ui_metrics_updated.connect(self.handle_gui_metrics_updated)
        self.session_manager.session_completed.connect(self.handle_gui_session_timeout)

        # --- חיבור מערכת בטיחות וחירום ---
        self.video_worker.sos_countdown_started.connect(self.play_warning_speech)
        self.video_worker.emergency_trigger.connect(self.trigger_emergency_protocol)

    # ======== 🎨 GUIפונקציות ה ========

    def handle_gui_login_success(self, user_data):
        self.login_page.error_label.setText("")
        NexusAlert.show_message("Access Granted", f"Welcome back, {user_data['username']}!\nWe are so glad to see you again.", is_success=True, parent=self)
        self.selection_page.welcome_label.setText(f"WELCOME, {user_data['username'].upper()}")
        self.pages.setCurrentIndex(2)


    def handle_gui_registration_success(self, user_data):
        NexusAlert.show_message("Profile Initialized", f"Welcome to NEXUS, {user_data['username']}!\nYour physical and SOS parameters are locked.", is_success=True, parent=self)
        # ניקוי השדות המקורי שלך
        for field in [self.register_page.user_input, self.register_page.pwd_input, self.register_page.age_input, 
                      self.register_page.height_input, self.register_page.weight_input, self.register_page.ice_name_input, self.register_page.ice_phone_input]:
            field.clear()
        self.register_page.error_label.setText("")
        self.selection_page.welcome_label.setText(f"WELCOME, {user_data['username'].upper()}")
        self.pages.setCurrentIndex(2)


    def handle_gui_countdown_tick(self, seconds, speak_title):
        if speak_title:
            self.voice_manager.reset()
            self.voice_manager.speak_safe(f"Get ready for {speak_title}! Starting in 3. 2. 1.")
            # הפעלת ה-Live GPS דרך המנג'ר שלו
            self.location_manager.trigger_live_geolocation_tracking(self.auth_manager.current_user["id"])
            self.pages.setCurrentIndex(3)
            
        self.header_label.setText(f"STARTING IN {seconds}...")
        self.dashboard.status_label.setText(f"STARTING ({seconds})")
        self.dashboard.status_label.setStyleSheet("color: #f1c40f; background: transparent; border: none;")
        self.ui_countdown_timer.start(1000)


    def handle_gui_countdown_finished(self):
        self.ui_countdown_timer.stop()
        self.header_label.setText("AI SESSION ACTIVE")
        self.dashboard.status_label.setText("GO!")
        self.dashboard.status_label.setStyleSheet("color: #00ff66; background: transparent; border: none;")
        # הפעלת שעון הספירה לאחור דרך ה-TimerManager
        self.timer_manager.start_workout(self.session_manager.stored_config["time_limit"])


    def handle_gui_pause_state_changed(self, is_paused):
        self.session_manager.set_paused(is_paused)
        if is_paused:
            self.dashboard.status_label.setText("SESSION PAUSED")
            self.dashboard.status_label.setStyleSheet("color: #ff3333; background: transparent; border: none;")
            self.dashboard.set_paused_ui(True)
            self.voice_manager.speak_safe("Session paused.")
        else:
            self.dashboard.status_label.setText("GO!")
            self.dashboard.status_label.setStyleSheet("color: #00ff66; background: transparent; border: none;")
            self.dashboard.set_paused_ui(False)
            self.voice_manager.speak_safe("Resuming session.")


    def handle_gui_metrics_updated(self, target_goal, reps_left, time_left, is_active, feedback):
        self.dashboard.update_ui_metrics(
            target_goal=target_goal, reps_left=reps_left, time_left=time_left, is_active=is_active, feedback=feedback
        )
        if feedback and not self.session_manager.is_paused:
            self.voice_manager.speak_safe(feedback)


    def handle_gui_session_timeout(self, is_success):
        self.timer_manager.stop_workout()
        if is_success:
            self.voice_manager.speak_safe("Amazing job! You absolutely crushed it!")
            NexusAlert.show_message("Goal Reached!", "Phenomenal pace!\nYou hit your target perfectly.\nKeep up this incredible energy!", is_success=True, parent=self)
        else:
            self.voice_manager.speak_safe("Bummer! Time is up. Let's try again.")
            NexusAlert.show_message("BUMMER!", "Time slipped away!\nDon't sweat it – reset your pace,\nand let's try again!", is_success=False, parent=self)
        
        # איפוס נתונים בטוח וחזרה למסך הבית
        self.session_manager.reset_and_clean_session()
        self.header_label.setText("AI SESSION ACTIVE")
        self.dashboard.status_label.setText("INITIALIZING...")
        self.dashboard.status_label.setStyleSheet("color: #00f3ff; background: transparent; border: none;")
        self.dashboard.set_paused_ui(False)
        self.selection_page.go_back_to_cards()
        self.pages.setCurrentIndex(2)


    def closeEvent(self, event):
        print("[SHUTDOWN] Stopping background camera thread safely...")
        self.timer_manager.stop_workout()
        self.session_manager.reset_and_clean_session()
        self.video_worker.stop()
        event.accept()


    # ======== 🚨 פרוטוקול חירום (SOS) ========

    def play_warning_speech(self):
        print("[GUI] Warning timer started! Playing priority speech IMMEDIATELY.")
        warning_text = "Fall detected. Emergency protocol will be activated in 10 seconds. Please show signs of life."
        # קוראים לדיבור דרך ה-voice_manager החדש!
        self.voice_manager.speak_safe(warning_text, priority=True)

    def trigger_emergency_protocol(self):
        print("[GUI] Emergency signal received! Showing dramatic overlay.")
        if not hasattr(self, 'emergency_active') or not self.emergency_active:
            self.emergency_active = True
            # נעילת האימון דרך ה-SessionManager
            self.session_manager.set_paused(True)
            self.session_manager.is_workout_active = False
            # הקפצת המסך האדום דרך מנהל החירום
            self.emergency_manager.show_emergency()
            # דיבור סופי
            self.voice_manager.speak_safe("Emergency detected! Calling emergency services.", priority=True)
