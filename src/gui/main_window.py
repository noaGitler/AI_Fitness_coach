from PyQt6.QtWidgets import QMainWindow, QStackedWidget
from PyQt6.QtCore import Qt, QTimer

# Screens and components
from src.gui.workout.workout_screen import WorkoutScreen
from src.gui.components.selection_screen import SelectionScreen
from src.gui.components.nexus_alert import NexusAlert
from src.gui.auth.auth_screens import LoginScreen, RegisterScreen

# Managers
from src.gui.managers.timer_manager import TimerManager
from src.gui.managers.auth_manager import AuthManager
from src.gui.managers.location_manager import LocationManager
from src.gui.managers.voice_manager import VoiceManager
from src.gui.managers.session_manager import SessionManager
from src.gui.managers.emergency_manager import EmergencyManager

from src.ai.workout_worker import VideoWorker

class MainWindow(QMainWindow):
    """The main window of the application - manages screen navigation, managers, and signal connections"""
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("AI NEXUS - Fitness Intelligence")
        self.setGeometry(100, 100, 1200, 750)
        
        # Build the UI pages inside the global stacked widget
        self.pages = QStackedWidget()
        self.setCentralWidget(self.pages)
        
        self.login_page = LoginScreen()
        self.register_page = RegisterScreen()
        self.selection_page = SelectionScreen()
        self.workout_page = WorkoutScreen() 
        
        self.pages.addWidget(self.login_page)     
        self.pages.addWidget(self.register_page)   
        self.pages.addWidget(self.selection_page) 
        self.pages.addWidget(self.workout_page) 
        
        # Start the background camera/AI worker
        self.video_worker = VideoWorker()
        self.video_worker.main_window_ref = self
        self.video_worker.start()

        # Initialize the independent managers
        self.timer_manager = TimerManager()
        self.auth_manager = AuthManager()
        self.location_manager = LocationManager()
        self.voice_manager = VoiceManager()
        self.session_manager = SessionManager(self.video_worker)
        self.emergency_manager = EmergencyManager(self)
        self.emergency_active = False

        # Internal timer driving the pre-workout countdown ticks
        self.ui_countdown_timer = QTimer(self)
        self.ui_countdown_timer.timeout.connect(self.session_manager.handle_countdown_tick)

        # Wire up all the signals connecting the screens to the managers
        self._connect_signals()

    def _connect_signals(self):
        """Connects every screen/manager signal to its handler. Called once at startup."""
        
        # a) Stream video/metrics from the worker to the workout screen's widgets
        self.video_worker.frame_ready.connect(self.workout_page.video_panel.update_frame)
        self.video_worker.metrics_ready.connect(self.session_manager.process_live_metrics)
        self.workout_page.replay_demo_btn.clicked.connect(self.workout_page.demo_video_panel.trigger_manual_demo)

        # b) The workout dashboard's internal navigation buttons
        self.workout_page.dashboard.pause_btn.clicked.connect(self.timer_manager.toggle_pause)
        self.workout_page.dashboard.exit_session_btn.clicked.connect(lambda: self.handle_gui_session_timeout(is_success=False))

        # c) Connect the login/register pages to the AuthManager
        self.login_page.login_requested.connect(self.auth_manager.login)
        self.login_page.go_to_register.connect(lambda: self.pages.setCurrentIndex(1))
        
        self.register_page.register_requested.connect(self.auth_manager.register)
        self.register_page.go_to_login.connect(lambda: self.pages.setCurrentIndex(0))
        
        self.selection_page.launch_workout.connect(self.session_manager.start_countdown_phase)
        self.selection_page.logout_clicked.connect(self.auth_manager.logout)
        
        # d) React to authentication status from the AuthManager
        self.auth_manager.login_success.connect(self.handle_gui_login_success)
        self.auth_manager.login_failed.connect(lambda msg: self.login_page.error_label.setText(msg))
        self.auth_manager.registration_success.connect(self.handle_gui_registration_success)
        self.auth_manager.registration_failed.connect(lambda msg: self.register_page.error_label.setText(msg))
        self.auth_manager.login_failed.connect(lambda _: self.pages.setCurrentIndex(0))
        self.auth_manager.logout_success.connect(lambda: self.pages.setCurrentIndex(0))

        # e) Sync the countdown with the SessionManager
        self.session_manager.countdown_tick_received.connect(self.handle_gui_countdown_tick)
        self.session_manager.countdown_finished.connect(self.handle_gui_countdown_finished)

        # f) Time updates and pause state
        self.timer_manager.time_updated.connect(lambda remaining_seconds: self.session_manager.handle_timer_tick())
        self.timer_manager.pause_state_changed.connect(self.handle_gui_pause_state_changed)

        # g) Live metric updates and workout completion
        self.session_manager.ui_metrics_updated.connect(self.handle_gui_metrics_updated)
        self.session_manager.session_completed.connect(self.handle_gui_session_timeout)

        # h) Safety/emergency protocol
        self.video_worker.sos_countdown_started.connect(self.play_warning_speech)
        self.video_worker.emergency_trigger.connect(self.trigger_emergency_protocol)

        # Connect the emergency overlay's exit button to the reset handler
        self.emergency_manager.exit_btn.clicked.connect(self.handle_emergency_exit)

    # GUI handlers 

    def handle_gui_login_success(self, user_data):
        """Shows a welcome message and moves to the exercise selection screen."""
        self.login_page.error_label.setText("")
        NexusAlert.show_message("Access Granted", f"Welcome back, {user_data['username']}!\nWe are so glad to see you again.", is_success=True, parent=self)
        self.selection_page.welcome_label.setText(f"WELCOME, {user_data['username'].upper()}")
        self.pages.setCurrentIndex(2)

    def handle_gui_registration_success(self, user_data):
        """Clears the registration form and moves to the exercise selection screen."""
        NexusAlert.show_message("Profile Initialized", f"Welcome to NEXUS, {user_data['username']}!\nYour physical and SOS parameters are locked.", is_success=True, parent=self)
        for field in [self.register_page.user_input, self.register_page.pwd_input, self.register_page.age_input, 
                      self.register_page.height_input, self.register_page.weight_input, self.register_page.ice_name_input, self.register_page.ice_phone_input]:
            field.clear()
        self.register_page.error_label.setText("")
        self.selection_page.welcome_label.setText(f"WELCOME, {user_data['username'].upper()}")
        self.pages.setCurrentIndex(2)

    def handle_gui_countdown_tick(self, seconds, speak_title):
        """Handles one countdown tick: on the first tick, sets up the exercise
        and demo panel; every tick updates the on-screen countdown text."""
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
        """Stops the countdown timer and starts the actual workout session timer."""
        self.ui_countdown_timer.stop()
        self.workout_page.header_label.setText("AI SESSION ACTIVE")
        self.workout_page.dashboard.status_label.setText("GO!")
        self.timer_manager.start_workout(self.session_manager.stored_config["time_limit"])

    def handle_gui_pause_state_changed(self, is_paused):
        """Updates the dashboard and speaks a short notice when pause is toggled."""
        self.session_manager.set_paused(is_paused)
        if is_paused:
            self.workout_page.dashboard.set_paused_ui(True)
            self.voice_manager.speak_safe("Session paused.")
        else:
            self.workout_page.dashboard.set_paused_ui(False)
            self.voice_manager.speak_safe("Resuming session.")

    def handle_gui_metrics_updated(self, target_goal, reps_left, time_left, is_active, feedback):
        """Updates the dashboard with the latest metrics, and clears the SOS
        state once a sign of life is detected during an active emergency."""
        
        is_sos_active = getattr(self, 'emergency_active', False)
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
                
                self.workout_page.video_panel.setProperty("class", "")
                self.workout_page.video_panel.style().unpolish(self.workout_page.video_panel)
                self.workout_page.video_panel.style().polish(self.workout_page.video_panel)
                
                self.workout_page.dashboard.set_sos_ui(False)
            else:
                return

        self.workout_page.dashboard.update_ui_metrics(
            target_goal=target_goal, reps_left=reps_left, time_left=time_left, is_active=is_active, feedback=feedback
        )

        if feedback and not self.session_manager.is_paused:
            self.voice_manager.speak_safe(feedback)

    def handle_gui_session_timeout(self, is_success):
        """Handles the end of a workout session, whether the goal was reached or time ran out."""
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
        """Ensures the background camera thread is stopped cleanly on app close."""
        print("[SHUTDOWN] Stopping background camera thread safely...")
        self.timer_manager.stop_workout()
        self.session_manager.reset_and_clean_session()
        self.video_worker.stop()
        event.accept()

    # ======== Emergency (SOS) protocol ========

    def play_warning_speech(self):
        """Plays the initial fall-warning speech and switches the UI into the SOS-countdown look."""
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
        """Locks the app into full emergency mode and shows the red overlay."""
        print("[GUI] Emergency signal received! Showing dramatic overlay.")
        if not hasattr(self, 'emergency_active') or not self.emergency_active:
            self.emergency_active = True
            self.session_manager.set_paused(True)
            self.session_manager.is_workout_active = False
            self.emergency_manager.show_emergency()
            self.voice_manager.speak_safe("Emergency detected! Calling emergency services.", priority=True)

    def handle_emergency_exit(self):
            """Handles the "I'M OK" button: clears the emergency state and returns
            to the exercise selection screen."""
            print("[SOS] User clicked exit. Clearing freeze and resetting application state...")
            
            self.emergency_active = False
            if hasattr(self, 'emergency_manager'):
                self.emergency_manager.overlay.hide()
                
            self.timer_manager.stop_workout()
            self.video_worker.set_exercise(None)
            self.session_manager.reset_and_clean_session()
            
            self.workout_page.header_label.setText("AI SESSION ACTIVE")
            self.workout_page.header_label.setProperty("class", "")
            self.workout_page.header_label.style().unpolish(self.workout_page.header_label)
            self.workout_page.header_label.style().polish(self.workout_page.header_label)
            
            self.workout_page.dashboard.set_sos_ui(False)
            self.workout_page.dashboard.status_label.setText("INITIALIZING...")
            self.workout_page.dashboard.set_paused_ui(False)
            
            self.selection_page.go_back_to_cards()
            self.pages.setCurrentIndex(2) 


