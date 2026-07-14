from PyQt6.QtWidgets import QMainWindow, QStackedWidget
from PyQt6.QtCore import Qt, QTimer

# ייבוא המסכים והרכיבים
from src.gui.workout.workout_screen import WorkoutScreen
from src.gui.components.selection_screen import SelectionScreen
from src.gui.components.nexus_alert import NexusAlert
from src.gui.auth.auth_screens import LoginScreen, RegisterScreen

# ייבוא המנג'רים
from src.gui.managers.timer_manager import TimerManager
from src.gui.managers.auth_manager import AuthManager
from src.gui.managers.location_manager import LocationManager
from src.gui.managers.voice_manager import VoiceManager
from src.gui.managers.session_manager import SessionManager
from src.gui.managers.emergency_manager import EmergencyManager

from src.ai.workout_worker import VideoWorker

class MainWindow(QMainWindow):
    """הבקר המרכזי של האפליקציה - מנהל ניווט מסכים, מנג'רים וקישור אותות (Signals)"""
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("AI NEXUS - Fitness Intelligence")
        self.setGeometry(100, 100, 1200, 750)
        
        # בניית דפי ה-UI בתוך ה-StackedWidget הגלובלי
        self.pages = QStackedWidget()
        self.setCentralWidget(self.pages)
        
        self.login_page = LoginScreen()
        self.register_page = RegisterScreen()
        self.selection_page = SelectionScreen()
        self.workout_page = WorkoutScreen() # המסך החדש והמרופד שלנו!
        
        self.pages.addWidget(self.login_page)       # 0
        self.pages.addWidget(self.register_page)    # 1
        self.pages.addWidget(self.selection_page)   # 2
        self.pages.addWidget(self.workout_page)     # 3
        
        # אתחול ה-Worker של המצלמה וה-AI ברקע
        self.video_worker = VideoWorker()
        self.video_worker.main_window_ref = self
        self.video_worker.start()


        # אתחול מנג'רים עצמאיים
        self.timer_manager = TimerManager()
        self.auth_manager = AuthManager()
        self.location_manager = LocationManager()
        self.voice_manager = VoiceManager()
        self.session_manager = SessionManager(self.video_worker)
        
        # תיקון: מעבירים את ה-video_panel האמיתי שנמצא בתוך ה-workout_page המרופד!
        # self.emergency_manager = EmergencyManager(self.workout_page.video_panel)
        self.emergency_manager = EmergencyManager(self)
        self.emergency_active = False


        # אתחול מנג'רים עצמאיים
        # self.timer_manager = TimerManager()
        # self.auth_manager = AuthManager()
        # self.location_manager = LocationManager()
        # self.voice_manager = VoiceManager()
        # self.session_manager = SessionManager(self.video_worker)
        # self.emergency_manager = EmergencyManager(self.workout_page.video_panel)
        # self.emergency_active = False
        
        # טיימר פנימי לניהול שלבי ה-Countdown במסך
        self.ui_countdown_timer = QTimer(self)
        self.ui_countdown_timer.timeout.connect(self.session_manager.handle_countdown_tick)

        # חיבור רשת הצינורות (Signals) שמקשרת בין המסכים למנג'רים
        self._connect_signals()

    def _connect_signals(self):



       
        # א) הזרמת וידאו ומדדים מה-Worker לרכיבים הייעודיים במסך האימון
        # תיקון: הפנייה ישירה לווידג'ט שבתוך ה-workout_page
        self.video_worker.frame_ready.connect(self.workout_page.video_panel.update_frame)
        self.video_worker.metrics_ready.connect(self.session_manager.process_live_metrics)
        self.workout_page.replay_demo_btn.clicked.connect(self.workout_page.demo_video_panel.trigger_manual_demo)




        # א) הזרמת וידאו ומדדים מה-Worker לרכיבים הייעודיים במסך האימון
        # self.video_worker.frame_ready.connect(self.workout_page.video_panel.update_frame)
        # self.video_worker.metrics_ready.connect(self.session_manager.process_live_metrics)
        # self.workout_page.replay_demo_btn.clicked.connect(self.workout_page.demo_video_panel.trigger_manual_demo)

        # ב) כפתורי הניווט הפנימיים של הדשבורד במסך האימון
        self.workout_page.dashboard.pause_btn.clicked.connect(self.timer_manager.toggle_pause)
        self.workout_page.dashboard.exit_session_btn.clicked.connect(lambda: self.handle_gui_session_timeout(is_success=False))

        # ג) חיבור דפי הלוגין והרגיסטר ל-AuthManager
        self.login_page.login_requested.connect(self.auth_manager.login)
        self.login_page.go_to_register.connect(lambda: self.pages.setCurrentIndex(1))
        
        self.register_page.register_requested.connect(self.auth_manager.register)
        self.register_page.go_to_login.connect(lambda: self.pages.setCurrentIndex(0))
        
        self.selection_page.launch_workout.connect(self.session_manager.start_countdown_phase)
        self.selection_page.logout_clicked.connect(self.auth_manager.logout)
        
        # ד) תגובות לסטטוס האימות מתוך ה-AuthManager
        self.auth_manager.login_success.connect(self.handle_gui_login_success)
        self.auth_manager.login_failed.connect(lambda msg: self.login_page.error_label.setText(msg))
        self.auth_manager.registration_success.connect(self.handle_gui_registration_success)
        self.auth_manager.registration_failed.connect(lambda msg: self.register_page.error_label.setText(msg))
        self.auth_manager.login_failed.connect(lambda _: self.pages.setCurrentIndex(0))
        self.auth_manager.logout_success.connect(lambda: self.pages.setCurrentIndex(0))

        # ה) סנכרון ה-Countdown מול ה-SessionManager
        self.session_manager.countdown_tick_received.connect(self.handle_gui_countdown_tick)
        self.session_manager.countdown_finished.connect(self.handle_gui_countdown_finished)

        # ו) עדכוני זמנים ומצבי עצירה (Pause)
        self.timer_manager.time_updated.connect(lambda remaining_seconds: self.session_manager.handle_timer_tick())
        self.timer_manager.pause_state_changed.connect(self.handle_gui_pause_state_changed)

        # ז) עדכוני מדדים בלייב וסיום האימון
        self.session_manager.ui_metrics_updated.connect(self.handle_gui_metrics_updated)
        self.session_manager.session_completed.connect(self.handle_gui_session_timeout)

        # ח) מערכת בטיחות וחירום
        self.video_worker.sos_countdown_started.connect(self.play_warning_speech)
        self.video_worker.emergency_trigger.connect(self.trigger_emergency_protocol)

        # 🌟 שורה חדשה: חיבור כפתור היציאה מהמסך האדום לפונקציית השחרור מהקיפאון
        self.emergency_manager.exit_btn.clicked.connect(self.handle_emergency_exit)

    # ======== 🎨 פונקציות ניהול ה-GUI ========

    def handle_gui_login_success(self, user_data):
        self.login_page.error_label.setText("")
        NexusAlert.show_message("Access Granted", f"Welcome back, {user_data['username']}!\nWe are so glad to see you again.", is_success=True, parent=self)
        self.selection_page.welcome_label.setText(f"WELCOME, {user_data['username'].upper()}")
        self.pages.setCurrentIndex(2)

    def handle_gui_registration_success(self, user_data):
        NexusAlert.show_message("Profile Initialized", f"Welcome to NEXUS, {user_data['username']}!\nYour physical and SOS parameters are locked.", is_success=True, parent=self)
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
            
            exercise_obj = None
            for attr in ['current_exercise', 'active_exercise', 'exercise']:
                if hasattr(self.session_manager, attr):
                    val = getattr(self.session_manager, attr)
                    if val and not isinstance(val, str):
                        exercise_obj = val
                        break
            
            if exercise_obj:
                self.video_worker.set_exercise(exercise_obj)
            elif hasattr(self.session_manager, 'stored_config') and isinstance(self.session_manager.stored_config, dict):
                possible_obj = self.session_manager.stored_config.get('exercise')
                if possible_obj and not isinstance(possible_obj, str):
                    self.video_worker.set_exercise(possible_obj)

            self.workout_page.demo_video_panel.set_active_exercise(speak_title)
            has_demo = self.workout_page.demo_video_panel.has_demo_video(speak_title)
            self.workout_page.demo_video_panel.setVisible(has_demo)
            self.workout_page.replay_demo_btn.setVisible(has_demo)
            
            self.location_manager.trigger_live_geolocation_tracking(self.auth_manager.current_user["id"])
            self.pages.setCurrentIndex(3)
            
        self.workout_page.header_label.setText(f"STARTING IN {seconds}...")
        self.workout_page.dashboard.status_label.setText(f"STARTING ({seconds})")
        self.ui_countdown_timer.start(1000)

    def handle_gui_countdown_finished(self):
        self.ui_countdown_timer.stop()
        self.workout_page.header_label.setText("AI SESSION ACTIVE")
        self.workout_page.dashboard.status_label.setText("GO!")
        self.timer_manager.start_workout(self.session_manager.stored_config["time_limit"])

    def handle_gui_pause_state_changed(self, is_paused):
        self.session_manager.set_paused(is_paused)
        if is_paused:
            self.workout_page.dashboard.set_paused_ui(True)
            self.voice_manager.speak_safe("Session paused.")
        else:
            self.workout_page.dashboard.set_paused_ui(False)
            self.voice_manager.speak_safe("Resuming session.")

    def handle_gui_metrics_updated(self, target_goal, reps_left, time_left, is_active, feedback):
        is_sos_active = getattr(self, 'emergency_active', False)
        # has_sign_of_life = is_active or (reps_left < target_goal) or (feedback and "FALL" not in feedback.upper() and "SOS" not in feedback.upper())

        has_sign_of_life = is_active or (int(reps_left) < int(target_goal)) or (feedback and "FALL" not in feedback.upper() and "SOS" not in feedback.upper())



        if is_sos_active:
            if has_sign_of_life:
                self.emergency_active = False
                if hasattr(self, 'emergency_manager') and hasattr(self.emergency_manager, 'stop_emergency_protocol'):
                    self.emergency_manager.stop_emergency_protocol()
                
                self.workout_page.header_label.setText("AI SESSION ACTIVE")
                self.workout_page.header_label.setProperty("class", "")
                self.workout_page.header_label.style().unpolish(self.workout_page.header_label)
                self.workout_page.header_label.style().polish(self.workout_page.header_label)
                
                # תיקון: שינוי העיצוב לווידג'ט הנכון בשגרה
                self.workout_page.video_panel.setProperty("class", "")
                self.workout_page.video_panel.style().unpolish(self.workout_page.video_panel)
                self.workout_page.video_panel.style().polish(self.workout_page.video_panel)
                
                self.workout_page.dashboard.set_sos_ui(False)
            else:
                return




        # if is_sos_active:
        #     if has_sign_of_life:
        #         self.emergency_active = False
        #         if hasattr(self, 'emergency_manager') and hasattr(self.emergency_manager, 'stop_emergency_protocol'):
        #             self.emergency_manager.stop_emergency_protocol()
                
        #         self.workout_page.header_label.setText("AI SESSION ACTIVE")
        #         self.workout_page.header_label.setProperty("class", "")
        #         self.workout_page.header_label.style().unpolish(self.workout_page.header_label)
        #         self.workout_page.header_label.style().polish(self.workout_page.header_label)
                
        #         self.workout_page.video_panel.setProperty("class", "")
        #         self.workout_page.video_panel.style().unpolish(self.workout_page.video_panel)
        #         self.workout_page.video_panel.style().polish(self.workout_page.video_panel)
                
        #         self.workout_page.dashboard.set_sos_ui(False)
        #     else:
        #         return

        self.workout_page.dashboard.update_ui_metrics(
            target_goal=target_goal, reps_left=reps_left, time_left=time_left, is_active=is_active, feedback=feedback
        )

        if feedback and not self.session_manager.is_paused:
            self.voice_manager.speak_safe(feedback)

    def handle_gui_session_timeout(self, is_success):
        self.timer_manager.stop_workout()
        self.video_worker.set_exercise(None)

        self.workout_page.demo_video_panel.setVisible(False)
        self.workout_page.replay_demo_btn.setVisible(False)
        self.workout_page.demo_video_panel.set_active_exercise("")
        
        if is_success:
            self.voice_manager.speak_safe("Amazing job! You absolutely crushed it!")
            NexusAlert.show_message("Goal Reached!", "Phenomenal pace!\nYou hit your target perfectly.", is_success=True, parent=self)
        else:
            self.voice_manager.speak_safe("Bummer! Time is up. Let's try again.")
            NexusAlert.show_message("BUMMER!", "Time slipped away!\nLet's try again!", is_success=False, parent=self)
        
        self.session_manager.reset_and_clean_session()
        self.workout_page.header_label.setText("AI SESSION ACTIVE")
        self.workout_page.dashboard.status_label.setText("INITIALIZING...")
        self.workout_page.dashboard.set_paused_ui(False)
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
        self.voice_manager.speak_safe(warning_text, priority=True)
        
        self.workout_page.header_label.setText("🚨 10 SECONDS TO EMERGENCY ACTIVE 🚨")
        self.workout_page.header_label.setProperty("class", "EmergencyAlertText")
        self.workout_page.header_label.style().unpolish(self.workout_page.header_label)
        self.workout_page.header_label.style().polish(self.workout_page.header_label)
        
        self.workout_page.video_panel.setProperty("class", "EmergencyAlertPanel")
        self.workout_page.video_panel.style().unpolish(self.workout_page.video_panel)
        self.workout_page.video_panel.style().polish(self.workout_page.video_panel)
        
        self.workout_page.dashboard.set_sos_ui(True)

    def trigger_emergency_protocol(self):
        print("[GUI] Emergency signal received! Showing dramatic overlay.")
        if not hasattr(self, 'emergency_active') or not self.emergency_active:
            self.emergency_active = True
            self.session_manager.set_paused(True)
            self.session_manager.is_workout_active = False
            self.emergency_manager.show_emergency()
            self.voice_manager.speak_safe("Emergency detected! Calling emergency services.", priority=True)




    def handle_emergency_exit(self):
            print("[SOS] User clicked exit. Clearing freeze and resetting application state...")
            
            # 1. כיבוי סטטוס החירום והסתרת ה-Overlay האדום
            self.emergency_active = False
            if hasattr(self, 'emergency_manager'):
                self.emergency_manager.overlay.hide()
                
            # 2. עצירה מוחלטת של האימון הנוכחי וניקוי ה-AI ברקע
            self.timer_manager.stop_workout()
            self.video_worker.set_exercise(None)
            self.session_manager.reset_and_clean_session()
            
            # 3. החזרת רכיבי ה-UI של מסך האימון לעיצוב הרגיל שלהם (ניקוי מחלקות ה-SOS)
            self.workout_page.header_label.setText("AI SESSION ACTIVE")
            self.workout_page.header_label.setProperty("class", "")
            self.workout_page.header_label.style().unpolish(self.workout_page.header_label)
            self.workout_page.header_label.style().polish(self.workout_page.header_label)
            
            self.workout_page.dashboard.set_sos_ui(False)
            self.workout_page.dashboard.status_label.setText("INITIALIZING...")
            self.workout_page.dashboard.set_paused_ui(False)
            
            # 4. ניווט בטוח בחזרה למסך בחירת התרגילים הראשי
            self.selection_page.go_back_to_cards()
            self.pages.setCurrentIndex(2) # מעבר לעמוד ה-Selection





# from PyQt6.QtWidgets import QMainWindow, QStackedWidget
# from PyQt6.QtCore import Qt, QTimer

# # ייבוא המסכים והרכיבים
# from src.gui.workout.workout_screen import WorkoutScreen
# from src.gui.components.selection_screen import SelectionScreen
# from src.gui.components.nexus_alert import NexusAlert
# from src.gui.auth.auth_screens import LoginScreen, RegisterScreen

# # ייבוא המנג'רים
# from src.gui.managers.timer_manager import TimerManager
# from src.gui.managers.auth_manager import AuthManager
# from src.gui.managers.location_manager import LocationManager
# from src.gui.managers.voice_manager import VoiceManager
# from src.gui.managers.session_manager import SessionManager
# from src.gui.managers.emergency_manager import EmergencyManager

# from src.ai.workout_worker import VideoWorker

# class MainWindow(QMainWindow):
#     """הבקר המרכזי של האפליקציה - מנהל ניווט מסכים, מנג'רים וקישור אותות (Signals)"""
#     def __init__(self):
#         super().__init__()
        
#         self.setWindowTitle("AI NEXUS - Fitness Intelligence")
#         self.setGeometry(100, 100, 1200, 750)
        
#         # בניית דפי ה-UI בתוך ה-StackedWidget הגלובלי
#         self.pages = QStackedWidget()
#         self.setCentralWidget(self.pages)
        
#         self.login_page = LoginScreen()
#         self.register_page = RegisterScreen()
#         self.selection_page = SelectionScreen()
#         self.workout_page = WorkoutScreen() # המסך החדש והמרופד שלנו!
        
#         self.pages.addWidget(self.login_page)       # 0
#         self.pages.addWidget(self.register_page)    # 1
#         self.pages.addWidget(self.selection_page)   # 2
#         self.pages.addWidget(self.workout_page)     # 3
        
#         # אתחול ה-Worker של המצלמה וה-AI ברקע
#         self.video_worker = VideoWorker()
#         self.video_worker.main_window_ref = self
#         self.video_worker.start()

#         # אתחול מנג'רים עצמאיים
#         self.timer_manager = TimerManager()
#         self.auth_manager = AuthManager()
#         self.location_manager = LocationManager()
#         self.voice_manager = VoiceManager()
#         self.session_manager = SessionManager(self.video_worker)
#         self.emergency_manager = EmergencyManager(self.workout_page.video_panel)
#         self.emergency_active = False
        
#         # טיימר פנימי לניהול שלבי ה-Countdown במסך
#         self.ui_countdown_timer = QTimer(self)
#         self.ui_countdown_timer.timeout.connect(self.session_manager.handle_countdown_tick)

#         # חיבור רשת הצינורות (Signals) שמקשרת בין המסכים למנג'רים
#         self._connect_signals()

#     def _connect_signals(self):        
#         # א) הזרמת וידאו ומדדים מה-Worker לרכיבים הייעודיים במסך האימון
#         self.video_worker.frame_ready.connect(self.workout_page.video_panel.update_frame)
#         self.video_worker.metrics_ready.connect(self.session_manager.process_live_metrics)
#         self.workout_page.replay_demo_btn.clicked.connect(self.workout_page.demo_video_panel.trigger_manual_demo)

#         # ב) כפתורי הניווט הפנימיים של הדשבורד במסך האימון
#         self.workout_page.dashboard.pause_btn.clicked.connect(self.timer_manager.toggle_pause)
#         self.workout_page.dashboard.exit_session_btn.clicked.connect(lambda: self.handle_gui_session_timeout(is_success=False))

#         # ג) חיבור דפי הלוגין והרגיסטר ל-AuthManager
#         self.login_page.login_requested.connect(self.auth_manager.login)
#         self.login_page.go_to_register.connect(lambda: self.pages.setCurrentIndex(1))
        
#         self.register_page.register_requested.connect(self.auth_manager.register)
#         self.register_page.go_to_login.connect(lambda: self.pages.setCurrentIndex(0))
        
#         self.selection_page.launch_workout.connect(self.session_manager.start_countdown_phase)
#         self.selection_page.logout_clicked.connect(self.auth_manager.logout)
        
#         # ד) תגובות לסטטוס האימות מתוך ה-AuthManager
#         self.auth_manager.login_success.connect(self.handle_gui_login_success)
#         self.auth_manager.login_failed.connect(lambda msg: self.login_page.error_label.setText(msg))
#         self.auth_manager.registration_success.connect(self.handle_gui_registration_success)
#         self.auth_manager.registration_failed.connect(lambda msg: self.register_page.error_label.setText(msg))
#         self.auth_manager.login_failed.connect(lambda _: self.pages.setCurrentIndex(0))
#         self.auth_manager.logout_success.connect(lambda: self.pages.setCurrentIndex(0))

#         # ה) סנכרון ה-Countdown מול ה-SessionManager
#         self.session_manager.countdown_tick_received.connect(self.handle_gui_countdown_tick)
#         self.session_manager.countdown_finished.connect(self.handle_gui_countdown_finished)

#         # ו) עדכוני זמנים ומצבי עצירה (Pause)
#         self.timer_manager.time_updated.connect(lambda remaining_seconds: self.session_manager.handle_timer_tick())
#         self.timer_manager.pause_state_changed.connect(self.handle_gui_pause_state_changed)

#         # ז) עדכוני מדדים בלייב וסיום האימון
#         self.session_manager.ui_metrics_updated.connect(self.handle_gui_metrics_updated)
#         self.session_manager.session_completed.connect(self.handle_gui_session_timeout)

#         # ח) מערכת בטיחות וחירום
#         self.video_worker.sos_countdown_started.connect(self.play_warning_speech)
#         self.video_worker.emergency_trigger.connect(self.trigger_emergency_protocol)

#     # ======== 🎨 פונקציות ניהול ה-GUI ========

#     def handle_gui_login_success(self, user_data):
#         self.login_page.error_label.setText("")
#         NexusAlert.show_message("Access Granted", f"Welcome back, {user_data['username']}!\nWe are so glad to see you again.", is_success=True, parent=self)
#         self.selection_page.welcome_label.setText(f"WELCOME, {user_data['username'].upper()}")
#         self.pages.setCurrentIndex(2)

#     def handle_gui_registration_success(self, user_data):
#         NexusAlert.show_message("Profile Initialized", f"Welcome to NEXUS, {user_data['username']}!\nYour physical and SOS parameters are locked.", is_success=True, parent=self)
#         for field in [self.register_page.user_input, self.register_page.pwd_input, self.register_page.age_input, 
#                       self.register_page.height_input, self.register_page.weight_input, self.register_page.ice_name_input, self.register_page.ice_phone_input]:
#             field.clear()
#         self.register_page.error_label.setText("")
#         self.selection_page.welcome_label.setText(f"WELCOME, {user_data['username'].upper()}")
#         self.pages.setCurrentIndex(2)

#     def handle_gui_countdown_tick(self, seconds, speak_title):
#         if speak_title:
#             self.voice_manager.reset()
#             self.voice_manager.speak_safe(f"Get ready for {speak_title}! Starting in 3. 2. 1.")
            

#             exercise_obj = None
#             for attr in ['current_exercise', 'active_exercise', 'exercise']:
#                 if hasattr(self.session_manager, attr):
#                     val = getattr(self.session_manager, attr)
#                     if val and not isinstance(val, str):
#                         exercise_obj = val
#                         break
            
#             # אם מצאנו את האובייקט, נעדכן את ה-Worker מיד
#             if exercise_obj:
#                 self.video_worker.set_exercise(exercise_obj)
#             elif hasattr(self.session_manager, 'stored_config') and isinstance(self.session_manager.stored_config, dict):
#                 possible_obj = self.session_manager.stored_config.get('exercise')
#                 if possible_obj and not isinstance(possible_obj, str):
#                     self.video_worker.set_exercise(possible_obj)


#             self.workout_page.demo_video_panel.set_active_exercise(speak_title)
#             has_demo = self.workout_page.demo_video_panel.has_demo_video(speak_title)
#             self.workout_page.demo_video_panel.setVisible(has_demo)
#             self.workout_page.replay_demo_btn.setVisible(has_demo)
            
#             self.location_manager.trigger_live_geolocation_tracking(self.auth_manager.current_user["id"])
#             self.pages.setCurrentIndex(3)
            
#         self.workout_page.header_label.setText(f"STARTING IN {seconds}...")
#         self.workout_page.dashboard.status_label.setText(f"STARTING ({seconds})")
#         self.ui_countdown_timer.start(1000)

#     def handle_gui_countdown_finished(self):
#         self.ui_countdown_timer.stop()
#         self.workout_page.header_label.setText("AI SESSION ACTIVE")
#         self.workout_page.dashboard.status_label.setText("GO!")
#         self.timer_manager.start_workout(self.session_manager.stored_config["time_limit"])

#     def handle_gui_pause_state_changed(self, is_paused):
#         self.session_manager.set_paused(is_paused)
#         if is_paused:
#             self.workout_page.dashboard.status_label.setText("SESSION PAUSED")
#             self.workout_page.dashboard.set_paused_ui(True)
#             self.voice_manager.speak_safe("Session paused.")
#         else:
#             self.workout_page.dashboard.status_label.setText("GO!")
#             self.workout_page.dashboard.set_paused_ui(False)
#             self.voice_manager.speak_safe("Resuming session.")



#     def handle_gui_metrics_updated(self, target_goal, reps_left, time_left, is_active, feedback):
#     # בדיקה האם פרוטוקול החירום/SOS פעיל כרגע במערכת
#         is_sos_active = getattr(self, 'emergency_active', False)

#         # הגדרת "אות חיים": המשתמש פעיל, או שהתחלת לבצע חזרות, או שיש פידבק תנועה תקין
#         has_sign_of_life = is_active or (reps_left < target_goal) or (feedback and "FALL" not in feedback.upper() and "SOS" not in feedback.upper())

#         if is_sos_active:
#             if has_sign_of_life:
#                 # המשתמש הראה אות חיים (זז או השמיע קול) -> עוצרים את ה-SOS מיד!
#                 self.emergency_active = False
#                 if hasattr(self, 'emergency_manager'):
#                     self.emergency_manager.stop_emergency_protocol()
                
#                 # החזרת הרכיבים המדויקים של ה-WorkoutScreen שלך לעיצוב רגיל
#                 self.workout_page.header_label.setText("AI SESSION ACTIVE")
#                 self.workout_page.header_label.setStyleSheet("")
#                 self.workout_page.video_panel.setStyleSheet("")  # מנקה מסגרת אדומה אם הייתה
#                 self.workout_page.dashboard.set_sos_ui(False)    # סגירת חלונית ה-SOS בדשבורד
#             else:
#                 # אם יש SOS ואין אות חיים, חוסמים את שאר המדדים כדי שלא ידרסו את מסך האזעקה
#                 return

#         # עדכון המדדים השוטף בדשבורד שלך (קורה רק בשגרה או כשה-SOS נעצר)
#         self.workout_page.dashboard.update_ui_metrics(
#             target_goal=target_goal, reps_left=reps_left, time_left=time_left, is_active=is_active, feedback=feedback
#         )

#         if feedback and not self.session_manager.is_paused:
#             self.voice_manager.speak_safe(feedback)



#     # def handle_gui_metrics_updated(self, target_goal, reps_left, time_left, is_active, feedback):
#     #     # אם האזעקה הסופית כבר פועלת, לא דורסים את ה-UI עם מדדים רגילים
#     #     if getattr(self, 'emergency_active', False):
#     #         return

#     #     self.workout_page.dashboard.update_ui_metrics(
#     #         target_goal=target_goal, reps_left=reps_left, time_left=time_left, is_active=is_active, feedback=feedback
#     #     )
        
#     #     # 🔥 מנגנון הגנה: אם הסטטוס חזר להיות תקין (למשל קמת מהרצפה והשגיאה נעלמה)
#     #     if feedback and not ("FALL" in feedback.upper() or "SOS" in feedback.upper() or "WAITING" in feedback.upper()):
#     #         if "🚨" in self.workout_page.header_label.text():
#     #             # מחזירים את העיצוב המקורי והנקי שלך לשגרה
#     #             self.workout_page.header_label.setText("AI SESSION ACTIVE")
#     #             self.workout_page.header_label.setStyleSheet("")
#     #             self.workout_page.video_panel.setStyleSheet("")
#     #             self.workout_page.dashboard.set_sos_ui(False)

#     #     if feedback and not self.session_manager.is_paused:
#     #         self.voice_manager.speak_safe(feedback)





#     # def handle_gui_metrics_updated(self, target_goal, reps_left, time_left, is_active, feedback):
#     #     self.workout_page.dashboard.update_ui_metrics(
#     #         target_goal=target_goal, reps_left=reps_left, time_left=time_left, is_active=is_active, feedback=feedback
#     #     )
#     #     if feedback and not self.session_manager.is_paused:
#     #         self.voice_manager.speak_safe(feedback)

#     def handle_gui_session_timeout(self, is_success):
#         self.timer_manager.stop_workout()
        
#         self.video_worker.set_exercise(None)

#         self.workout_page.demo_video_panel.setVisible(False)
#         self.workout_page.replay_demo_btn.setVisible(False)
#         self.workout_page.demo_video_panel.set_active_exercise("")
        
#         if is_success:
#             self.voice_manager.speak_safe("Amazing job! You absolutely crushed it!")
#             NexusAlert.show_message("Goal Reached!", "Phenomenal pace!\nYou hit your target perfectly.", is_success=True, parent=self)
#         else:
#             self.voice_manager.speak_safe("Bummer! Time is up. Let's try again.")
#             NexusAlert.show_message("BUMMER!", "Time slipped away!\nLet's try again!", is_success=False, parent=self)
        
#         self.session_manager.reset_and_clean_session()
#         self.workout_page.header_label.setText("AI SESSION ACTIVE")
#         self.workout_page.dashboard.status_label.setText("INITIALIZING...")
#         self.workout_page.dashboard.set_paused_ui(False)
#         self.selection_page.go_back_to_cards()
#         self.pages.setCurrentIndex(2)

#     def closeEvent(self, event):
#         print("[SHUTDOWN] Stopping background camera thread safely...")
#         self.timer_manager.stop_workout()
#         self.session_manager.reset_and_clean_session()
#         self.video_worker.stop()
#         event.accept()

#     # ======== 🚨 פרוטוקול חירום (SOS) ========



#     def play_warning_speech(self):
#         print("[GUI] Warning timer started! Playing priority speech IMMEDIATELY.")
#         warning_text = "Fall detected. Emergency protocol will be activated in 10 seconds. Please show signs of life."
#         self.voice_manager.speak_safe(warning_text, priority=True)
        
#         # 🔥 השינוי הוויזואלי הדרמטי בזמן שה-SOS מתחיל לרוץ במקביל:
#         self.workout_page.header_label.setText("🚨 10 SECONDS TO EMERGENCY ACTIVE 🚨")
#         self.workout_page.header_label.setStyleSheet("color: #ff3333; font-weight: bold; font-size: 22px;")
        
#         # הפעלת מצב החירום הוויזואלי בדשבורד ובמצלמה שכתבת
#         self.workout_page.dashboard.set_sos_ui(True)
#         self.workout_page.video_panel.setStyleSheet("border: 6px solid #ff3333; border-radius: 12px;")






#     # def play_warning_speech(self):
#     #     print("[GUI] Warning timer started! Playing priority speech IMMEDIATELY.")
#     #     warning_text = "Fall detected. Emergency protocol will be activated in 10 seconds. Please show signs of life."
#     #     self.voice_manager.speak_safe(warning_text, priority=True)

#     def trigger_emergency_protocol(self):
#         print("[GUI] Emergency signal received! Showing dramatic overlay.")
#         if not hasattr(self, 'emergency_active') or not self.emergency_active:
#             self.emergency_active = True
#             self.session_manager.set_paused(True)
#             self.session_manager.is_workout_active = False
#             self.emergency_manager.show_emergency()
#             self.voice_manager.speak_safe("Emergency detected! Calling emergency services.", priority=True)











# from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,QGridLayout
# from PyQt6.QtCore import Qt, QTimer
# from PyQt6.QtGui import QFont

# # ייבוא המסכים והרכיבים המעוצבים שלך (העיצוב המקורי שלך נשמר במלואו!)
# # from src.gui.workout.video_widget import VideoWidget ,DemoVideoWidget
# from src.gui.workout.camera_widget import VideoWidget
# from src.gui.workout.demo_widget import DemoVideoWidget
# from src.gui.workout.workout_dashboard import WorkoutDashboard
# from src.gui.components.selection_screen import SelectionScreen
# from src.gui.components.nexus_alert import NexusAlert
# from src.gui.auth.auth_screens import LoginScreen, RegisterScreen

# # ייבוא 5 המנג'רים האמיתיים שהעלית עכשיו
# from src.gui.managers.timer_manager import TimerManager
# from src.gui.managers.auth_manager import AuthManager
# from src.gui.managers.location_manager import LocationManager
# from src.gui.managers.voice_manager import VoiceManager
# from src.gui.managers.session_manager import SessionManager
# from src.gui.managers.emergency_manager import EmergencyManager

# from src.ai.workout_worker import VideoWorker

# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
        
#         self.setWindowTitle("AI NEXUS - Fitness Intelligence")
#         self.setGeometry(100, 100, 1200, 750)
#         self.setStyleSheet("background-color: #080b0e;")
        
#         # אתחול ה-Worker של המצלמה וה-AI ברקע
#         self.video_worker = VideoWorker()
#         self.video_worker.main_window_ref = self
#         self.video_worker.start()

#         self.video_panel = VideoWidget(self)

#         # אתחול 5 המנג'רים העצמאיים
#         self.timer_manager = TimerManager()
#         self.auth_manager = AuthManager()
#         self.location_manager = LocationManager()
#         self.voice_manager = VoiceManager()
#         self.session_manager = SessionManager(self.video_worker)
#         self.emergency_manager = EmergencyManager(self.video_panel)
#         self.emergency_active = False
        
#         # טיימר קטן שנשאר במיין אך ורק בשביל לנהל את הטיקים של ה-Get Ready במסך
#         self.ui_countdown_timer = QTimer(self)
#         self.ui_countdown_timer.timeout.connect(self.session_manager.handle_countdown_tick)

#         # בניית המסכים והעברתם לתוך ה-StackedWidget
#         self.pages = QStackedWidget()
#         self.setCentralWidget(self.pages)
        
#         self.login_page = LoginScreen()
#         self.register_page = RegisterScreen()
#         self.selection_page = SelectionScreen()
#         self.workout_page = QWidget()
#         self.setup_workout_ui()
        
#         self.pages.addWidget(self.login_page)       # 0
#         self.pages.addWidget(self.register_page)    # 1
#         self.pages.addWidget(self.selection_page)   # 2
#         self.pages.addWidget(self.workout_page)     # 3
        
#         # חיבור רשת הצינורות (Signals) שמקשרת את המסכים למנג'רים
#         self._connect_signals()


#     def setup_workout_ui(self):
#         layout = QVBoxLayout(self.workout_page)
#         layout.setContentsMargins(20, 20, 20, 20)
        
#         # כותרת עליונה
#         self.header_label = QLabel("AI SESSION ACTIVE")
#         self.header_label.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
#         self.header_label.setStyleSheet("color: #ffffff; letter-spacing: 2px; margin-bottom: 15px;")
#         layout.addWidget(self.header_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
#         # שורת התוכן הראשית
#         content = QHBoxLayout()
#         content.setSpacing(20) 
        
#         # 1. בלוק שמאל: המצלמה המוגדלת (800x600)
#         video_container = QVBoxLayout()
#         video_container.addWidget(self.video_panel)
#         content.addLayout(video_container, stretch=0)
        
#         # 2. בלוק מרכז: עמדת הרובוט המיושרת לתחתית המצלמה 🌟
#         demo_container = QVBoxLayout()
#         demo_container.setSpacing(10)
        
#         # המפתח ל-UX הנכון: ה-Stretch נמצא בהתחלה ודוחף את הכל לתחתית!
#         demo_container.addStretch() 
        
#         # יצירת חלונית הרובוט 
#         self.demo_video_panel = DemoVideoWidget(self.workout_page)
#         self.demo_video_panel.setVisible(False)
        
#         # יצירת כפתור ה-Replay
#         self.replay_demo_btn = QPushButton("🔄 REPLAY DEMO", self.workout_page)
#         self.replay_demo_btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
#         self.replay_demo_btn.setFixedSize(160, 32)
#         self.replay_demo_btn.setCursor(Qt.CursorShape.PointingHandCursor)
#         self.replay_demo_btn.setStyleSheet("""
#             QPushButton {
#                 color: #00f3ff;
#                 background-color: #101418;
#                 border: 1px solid #00f3ff;
#                 border-radius: 6px;
#             }
#             QPushButton:hover { 
#                 background-color: #00f3ff; 
#                 color: #101418; 
#             }
#         """)
#         self.replay_demo_btn.setVisible(False)
        
#         # הוספת הרכיבים כשהם מוצמדים לחלק התחתון (AlignBottom)
#         demo_container.addWidget(self.demo_video_panel, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)
#         demo_container.addWidget(self.replay_demo_btn, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)
        
#         content.addLayout(demo_container, stretch=0)
        
#         # 3. בלוק ימין: דשבורד הנתונים
#         self.dashboard = WorkoutDashboard(self)
#         self.dashboard.setFixedWidth(320)
        
#         self.dashboard.pause_btn.clicked.connect(self.timer_manager.toggle_pause)
#         self.dashboard.exit_session_btn.clicked.connect(lambda: self.handle_gui_session_timeout(is_success=False))
        
#         content.addWidget(self.dashboard, stretch=0)
        
#         layout.addLayout(content)

#         self.emergency_manager = EmergencyManager(self.video_panel)
#         self.emergency_active = False



#     def _connect_signals(self):        
#         # א) הזרמת הוידאו והמדדים מה-Worker למקומות החדשים שלהם
#         self.video_worker.frame_ready.connect(self.video_panel.update_frame)
#         self.video_worker.metrics_ready.connect(self.session_manager.process_live_metrics)


#         # חפשי את מקום החיבורים בקובץ וודאי שקיימת השורה הזו:
#         self.replay_demo_btn.clicked.connect(self.demo_video_panel.trigger_manual_demo)

#         # חיבור כפתור ה-Replay החדש ישירות לפונקציית האתחול של המצלמה
#         # self.replay_demo_btn.clicked.connect(self.video_panel.trigger_manual_demo)

#         # ב) חיבור דפי הלוגין והרגיסטר ל-AuthManager הלוגי
#         self.login_page.login_requested.connect(self.auth_manager.login)
#         self.login_page.go_to_register.connect(lambda: self.pages.setCurrentIndex(1))
        
#         self.register_page.register_requested.connect(self.auth_manager.register)
#         self.register_page.go_to_login.connect(lambda: self.pages.setCurrentIndex(0))
        
#         self.selection_page.launch_workout.connect(self.session_manager.start_countdown_phase)
#         self.selection_page.logout_clicked.connect(self.auth_manager.logout)
        
#         # ג) המיין מקשיב לסטטוס האימות של ה-AuthManager ומעדכן את ה-GUI
#         self.auth_manager.login_success.connect(self.handle_gui_login_success)
#         self.auth_manager.login_failed.connect(lambda msg: self.login_page.error_label.setText(msg))
#         self.auth_manager.registration_success.connect(self.handle_gui_registration_success)
#         self.auth_manager.registration_failed.connect(lambda msg: self.register_page.error_label.setText(msg))
#         self.auth_manager.login_failed.connect(lambda _: self.pages.setCurrentIndex(0)) # חזרה ללוגין ביציאה
#         self.auth_manager.logout_success.connect(lambda: self.pages.setCurrentIndex(0))

#         # ד) המיין מקשיב למהלכי ה-Countdown של ה-SessionManager
#         self.session_manager.countdown_tick_received.connect(self.handle_gui_countdown_tick)
#         self.session_manager.countdown_finished.connect(self.handle_gui_countdown_finished)

#         # ה) עדכון זמנים: טיק השעון ב-TimerManager מניע את הזמן בתוך ה-SessionManager
#         self.timer_manager.time_updated.connect(lambda remaining_seconds: self.session_manager.handle_timer_tick())
#         self.timer_manager.pause_state_changed.connect(self.handle_gui_pause_state_changed)

#         # עדכוני מדדים בלייב וסיום האימון
#         self.session_manager.ui_metrics_updated.connect(self.handle_gui_metrics_updated)
#         self.session_manager.session_completed.connect(self.handle_gui_session_timeout)

#         # --- חיבור מערכת בטיחות וחירום ---
#         self.video_worker.sos_countdown_started.connect(self.play_warning_speech)
#         self.video_worker.emergency_trigger.connect(self.trigger_emergency_protocol)



#     # ======== 🎨 GUIפונקציות ה ========

#     def handle_gui_login_success(self, user_data):
#         self.login_page.error_label.setText("")
#         NexusAlert.show_message("Access Granted", f"Welcome back, {user_data['username']}!\nWe are so glad to see you again.", is_success=True, parent=self)
#         self.selection_page.welcome_label.setText(f"WELCOME, {user_data['username'].upper()}")
#         self.pages.setCurrentIndex(2)


#     def handle_gui_registration_success(self, user_data):
#         NexusAlert.show_message("Profile Initialized", f"Welcome to NEXUS, {user_data['username']}!\nYour physical and SOS parameters are locked.", is_success=True, parent=self)
#         # ניקוי השדות המקורי שלך
#         for field in [self.register_page.user_input, self.register_page.pwd_input, self.register_page.age_input, 
#                       self.register_page.height_input, self.register_page.weight_input, self.register_page.ice_name_input, self.register_page.ice_phone_input]:
#             field.clear()
#         self.register_page.error_label.setText("")
#         self.selection_page.welcome_label.setText(f"WELCOME, {user_data['username'].upper()}")
#         self.pages.setCurrentIndex(2)


#     def handle_gui_countdown_tick(self, seconds, speak_title):
#         if speak_title:
#             self.voice_manager.reset()
#             self.voice_manager.speak_safe(f"Get ready for {speak_title}! Starting in 3. 2. 1.")
            
#             self.demo_video_panel.set_active_exercise(speak_title)
            
#             # בדיקה דינמית גנרית
#             has_demo = self.demo_video_panel.has_demo_video(speak_title)
#             self.demo_video_panel.setVisible(has_demo)
#             self.replay_demo_btn.setVisible(has_demo)
            
#             self.location_manager.trigger_live_geolocation_tracking(self.auth_manager.current_user["id"])
#             self.pages.setCurrentIndex(3)
            
#         self.header_label.setText(f"STARTING IN {seconds}...")
#         self.dashboard.status_label.setText(f"STARTING ({seconds})")
#         self.dashboard.status_label.setStyleSheet("color: #f1c40f; background: transparent; border: none;")
#         self.ui_countdown_timer.start(1000)


#     def handle_gui_countdown_finished(self):
#         self.ui_countdown_timer.stop()
#         self.header_label.setText("AI SESSION ACTIVE")
#         self.dashboard.status_label.setText("GO!")
#         self.dashboard.status_label.setStyleSheet("color: #00ff66; background: transparent; border: none;")
#         # הפעלת שעון הספירה לאחור דרך ה-TimerManager
#         self.timer_manager.start_workout(self.session_manager.stored_config["time_limit"])


#     def handle_gui_pause_state_changed(self, is_paused):
#         self.session_manager.set_paused(is_paused)
#         if is_paused:
#             self.dashboard.status_label.setText("SESSION PAUSED")
#             self.dashboard.status_label.setStyleSheet("color: #ff3333; background: transparent; border: none;")
#             self.dashboard.set_paused_ui(True)
#             self.voice_manager.speak_safe("Session paused.")
#         else:
#             self.dashboard.status_label.setText("GO!")
#             self.dashboard.status_label.setStyleSheet("color: #00ff66; background: transparent; border: none;")
#             self.dashboard.set_paused_ui(False)
#             self.voice_manager.speak_safe("Resuming session.")


#     def handle_gui_metrics_updated(self, target_goal, reps_left, time_left, is_active, feedback):
#         self.dashboard.update_ui_metrics(
#             target_goal=target_goal, reps_left=reps_left, time_left=time_left, is_active=is_active, feedback=feedback
#         )
#         if feedback and not self.session_manager.is_paused:
#             self.voice_manager.speak_safe(feedback)


#     def handle_gui_session_timeout(self, is_success):
#         self.timer_manager.stop_workout()
        
#         self.demo_video_panel.setVisible(False)
#         self.replay_demo_btn.setVisible(False)
#         self.demo_video_panel.set_active_exercise("")
        
#         if is_success:
#             self.voice_manager.speak_safe("Amazing job! You absolutely crushed it!")
#             NexusAlert.show_message("Goal Reached!", "Phenomenal pace!\nYou hit your target perfectly.\nKeep up this incredible energy!", is_success=True, parent=self)
#         else:
#             self.voice_manager.speak_safe("Bummer! Time is up. Let's try again.")
#             NexusAlert.show_message("BUMMER!", "Time slipped away!\nDon't sweat it – reset your pace,\nand let's try again!", is_success=False, parent=self)
        
#         self.session_manager.reset_and_clean_session()
#         self.header_label.setText("AI SESSION ACTIVE")
#         self.dashboard.status_label.setText("INITIALIZING...")
#         self.dashboard.status_label.setStyleSheet("color: #00f3ff; background: transparent; border: none;")
#         self.dashboard.set_paused_ui(False)
#         self.selection_page.go_back_to_cards()
#         self.pages.setCurrentIndex(2)


#     def closeEvent(self, event):
#         print("[SHUTDOWN] Stopping background camera thread safely...")
#         self.timer_manager.stop_workout()
#         self.session_manager.reset_and_clean_session()
#         self.video_worker.stop()
#         event.accept()


#     # ======== 🚨 פרוטוקול חירום (SOS) ========

#     def play_warning_speech(self):
#         print("[GUI] Warning timer started! Playing priority speech IMMEDIATELY.")
#         warning_text = "Fall detected. Emergency protocol will be activated in 10 seconds. Please show signs of life."
#         # קוראים לדיבור דרך ה-voice_manager החדש!
#         self.voice_manager.speak_safe(warning_text, priority=True)

#     def trigger_emergency_protocol(self):
#         print("[GUI] Emergency signal received! Showing dramatic overlay.")
#         if not hasattr(self, 'emergency_active') or not self.emergency_active:
#             self.emergency_active = True
#             # נעילת האימון דרך ה-SessionManager
#             self.session_manager.set_paused(True)
#             self.session_manager.is_workout_active = False
#             # הקפצת המסך האדום דרך מנהל החירום
#             self.emergency_manager.show_emergency()
#             # דיבור סופי
#             self.voice_manager.speak_safe("Emergency detected! Calling emergency services.", priority=True)
