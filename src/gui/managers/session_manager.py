from PyQt6.QtCore import QObject, pyqtSignal
from src.ai.exercises.bicep_curl import BicepCurl
from src.ai.exercises.knee_extension import StandingKneeExtension
from src.ai.exercises.squat import Squat
from src.ai.exercises.base_exercise import BaseExercise

# Placeholder exercise classes, until the real logic is implemented

class DummyPushup(BaseExercise):
    """Placeholder for the pushup exercise (not implemented yet)."""
    def __init__(self):
        super().__init__()
        self.target_goal = 0
        self.feedback = "Pushup training coming soon!"
    def set_target_goal(self, goal): self.target_goal = goal
    def check(self, landmarks): return 0, 0


class SessionManager(QObject):
    """
    The main session manager for the workouts (SOLID - Single Responsibility Principle).
    Solely responsible for managing workout logic, AI metrics, and feedback states.
    """
    # Signals reported to MainWindow for UI updates only
    ui_metrics_updated = pyqtSignal(int, str, int, bool, str) # target_goal, reps_left, time_left, is_active, feedback
    countdown_tick_received = pyqtSignal(int, str)           # reports a countdown tick (seconds, exercise title)
    countdown_finished = pyqtSignal()                        # indicates the countdown has finished and the workout begins
    session_completed = pyqtSignal(bool)                     # indicates the workout has completed (True=success, False=wasted time)

    def __init__(self, video_worker):
        super().__init__()
        self.video_worker = video_worker
        
        # Core workout session state
        self.exercise = None
        self.is_workout_active = False
        self.is_paused = False
        self.stored_config = None
        self.goal_reached_successfully = False
        self.countdown_value = 3
        self.session_time_left = 0

    def start_countdown_phase(self, config_dict):
        """Initializes the session data and starts the preparation phase (instead of start_countdown_phase in MainWindow)"""
        self.is_workout_active = False 
        self.is_paused = False
        self.stored_config = config_dict
        self.goal_reached_successfully = False
        
        exercise_name = config_dict["exercise_name"]
        target_goal = config_dict["target_goal"]
        self.session_time_left = config_dict["time_limit"] 
        
        # 1. Pick the right exercise class based on the selected name
        name_lower = exercise_name.lower()
        if "bicep" in name_lower or "curl" in name_lower:
            self.exercise = BicepCurl()
            speak_title = "Bicep Curls"
        elif "knee" in name_lower or "extension" in name_lower or "développé" in name_lower:
            self.exercise = StandingKneeExtension()
            speak_title = "Knee Extensions"
        elif "squat" in name_lower:
            self.exercise = Squat()
            speak_title = "Squats"
        else:
            self.exercise = DummyPushup()
            speak_title = "Pushups"
            
        # 2. Connect the AI worker to the newly selected exercise
        self.video_worker.set_exercise(self.exercise)
        
        # 3. Initialize the internal countdown
        self.countdown_value = 3
        
        # 4. Send initial UI update for the workout start
        self.ui_metrics_updated.emit(target_goal, str(target_goal), self.session_time_left, False, "")
        self.countdown_tick_received.emit(self.countdown_value, speak_title)

    def handle_countdown_tick(self):
        """Manages the preparation phase ticks (called from the main window's timer)"""
        self.countdown_value -= 1
        if self.countdown_value > 0:
            self.countdown_tick_received.emit(self.countdown_value, "")
        else:
            # The preparation phase has finished - starting the actual workout!
            self.exercise.set_target_goal(self.stored_config["target_goal"])
            self.is_workout_active = True
            self.countdown_finished.emit()

    def handle_timer_tick(self):
        """Decrements the session time and updates the metrics each second."""
        if not self.is_workout_active or self.is_paused: 
            return
        
        self.session_time_left -= 1
        
        # Broadcast the updated metrics to the GUI dashboard
        self.ui_metrics_updated.emit(
            self.exercise.target_goal,
            self.exercise.reps_left,
            self.session_time_left,
            True,
            self.exercise.feedback
        )
        
        # Check if the full workout time has elapsed
        if self.session_time_left <= 0:
            self.is_workout_active = False
            self.session_completed.emit(self.goal_reached_successfully)

    def process_live_metrics(self, current_angle, feedback):
        """Manages the live AI metrics received from the camera (instead of receive_live_metrics in MainWindow)"""
        if self.exercise is not None and self.is_workout_active:
            if self.is_paused:
                return
                
            self.ui_metrics_updated.emit(
                self.exercise.target_goal,
                self.exercise.reps_left,
                self.session_time_left,
                (self.exercise.target_goal > 0 and not self.exercise.goal_finished),
                feedback
            )

            reps_str = str(self.exercise.reps_left).strip()
            if reps_str == "0" or "Bonus" in reps_str or "-" in reps_str or (hasattr(self.exercise, 'counter') and self.exercise.counter >= self.exercise.target_goal):
                self.goal_reached_successfully = True

    def set_paused(self, paused_state):
        """Updates whether AI metrics monitoring is currently paused."""
        self.is_paused = paused_state
        print(f"[SESSION] AI metrics monitoring pause state: {self.is_paused}")

    def reset_and_clean_session(self):
        """Fully clears the current exercise instance and its state."""
        self.is_workout_active = False
        self.is_paused = False
        
        # Disconnect the AI engine from the exercise, to silence feedback immediately
        self.video_worker.set_exercise(None)
        
        if self.exercise is not None:
            self.exercise.target_goal = 0
            self.exercise.feedback = "" 
            self.exercise.has_welcomed = False
            self.exercise.counter = 0
            self.exercise.bonus_counter = 0
            self.exercise.goal_finished = False
            self.exercise = None
        print("[SESSION] Core engine and exercise instance successfully garbage collected.")















# from PyQt6.QtCore import QObject, pyqtSignal
# from src.ai.exercises.bicep_curl import BicepCurl
# from src.ai.exercises.base_exercise import BaseExercise

# # מחלקות ה-Dummy שלכן מהמיין
# class DummySquat(BaseExercise):
#     def __init__(self):
#         super().__init__()
#         self.target_goal = 0
#         self.feedback = "Squat training coming soon!"
#     def set_target_goal(self, goal): self.target_goal = goal
#     def check(self, landmarks): return 0, 0

# class DummyPushup(BaseExercise):
#     def __init__(self):
#         super().__init__()
#         self.target_goal = 0
#         self.feedback = "Pushup training coming soon!"
#     def set_target_goal(self, goal): self.target_goal = goal
#     def check(self, landmarks): return 0, 0


# class SessionManager(QObject):
#     """
#     מנהל הסשן הראשי של האימונים (SOLID - Single Responsibility Principle).
#     אחראי בלעדית על ניהול לוגיקת האימון, מדדי ה-AI, ומצבי החזרות והבונוסים.
#     """
#     # סיגנלים המדווחים ל-MainWindow לצורך עדכון ה-GUI בלבד
#     ui_metrics_updated = pyqtSignal(int, str, int, bool, str) # target_goal, reps_left, time_left, is_active, feedback
#     countdown_tick_received = pyqtSignal(int, str)           # מדווח על טיק של קאונטדאון (שניות, כותרת התרגיל)
#     countdown_finished = pyqtSignal()                        # מאותת שהקאונטדאון נגמר והאימון מתחיל
#     session_completed = pyqtSignal(bool)                     # מאותת שהאימון הסתיים (True=הצלחה, False=בזבוז זמן)

#     def __init__(self, video_worker):
#         super().__init__()
#         self.video_worker = video_worker
        
#         # משתני מצב האימון המקוריים מה-MainWindow שלך
#         self.exercise = None
#         self.is_workout_active = False
#         self.is_paused = False
#         self.stored_config = None
#         self.goal_reached_successfully = False
#         self.countdown_value = 3
#         self.session_time_left = 0

#     def start_countdown_phase(self, config_dict):
#         """מאתחל את נתוני הסשן ומתחיל את שלב ההכנה (במקום start_countdown_phase במיין)"""
#         self.is_workout_active = False 
#         self.is_paused = False
#         self.stored_config = config_dict
#         self.goal_reached_successfully = False
        
#         exercise_name = config_dict["exercise_name"]
#         target_goal = config_dict["target_goal"]
#         self.session_time_left = config_dict["time_limit"] 
        
#         # 1. פולימורפיזם חכם ליצירת התרגיל (בול כמו במיין המקורי שלכן)
#         if "Bicep" in exercise_name:
#             self.exercise = BicepCurl()
#             speak_title = "Bicep Curls"
#         elif "Squat" in exercise_name:
#             self.exercise = DummySquat()
#             speak_title = "Squats"
#         else:
#             self.exercise = DummyPushup()
#             speak_title = "Pushups"
            
#         # 2. חיבור מנוע ה-AI (ה-Worker) אל התרגיל החדש שנבחר
#         self.video_worker.set_exercise(self.exercise)
        
#         # 3. אתחול הקאונטדאון הפנימי
#         self.countdown_value = 3
        
#         # 4. איתות ראשוני ל-UI להציג את נתוני הפתיחה
#         self.ui_metrics_updated.emit(target_goal, str(target_goal), self.session_time_left, False, "")
#         self.countdown_tick_received.emit(self.countdown_value, speak_title)

#     def handle_countdown_tick(self):
#         """מנהל את שלב הטיקים של ההכנה (נקרא מהטיימר של המיין)"""
#         self.countdown_value -= 1
#         if self.countdown_value > 0:
#             self.countdown_tick_received.emit(self.countdown_value, "")
#         else:
#             # שלב ההכנה הסתיים - מתחילים את האימון בפועל!
#             self.exercise.set_target_goal(self.stored_config["target_goal"])
#             self.is_workout_active = True
#             self.countdown_finished.emit()

#     def handle_timer_tick(self):
#         """מפחית שניות ומעדכן את המדדים בכל שנייה שעוברת (במקום session_timer_tick במיין)"""
#         if not self.is_workout_active or self.is_paused: 
#             return
        
#         self.session_time_left -= 1
        
#         # שידור המדדים המעודכנים לטובת ה-GUI דשבורד
#         self.ui_metrics_updated.emit(
#             self.exercise.target_goal,
#             self.exercise.reps_left,
#             self.session_time_left,
#             True,
#             self.exercise.feedback
#         )
        
#         # בדיקה אם נגמר הזמן המלא של האימון
#         if self.session_time_left <= 0:
#             self.is_workout_active = False
#             self.session_completed.emit(self.goal_reached_successfully)

#     def process_live_metrics(self, current_angle, feedback):
#         """מנתח את מדדי ה-AI שמתקבלים מהמצלמה בלייב (במקום receive_live_metrics במיין)"""
#         if self.exercise is not None and self.is_workout_active:
#             # 🚨 חוק ה-Pause המקורי שלך: אם אנחנו בהקפאה, מתעלמים לחלוטין מהמדדים!
#             if self.is_paused:
#                 return
                
#             self.ui_metrics_updated.emit(
#                 self.exercise.target_goal,
#                 self.exercise.reps_left,
#                 self.session_time_left,
#                 (self.exercise.target_goal > 0 and not self.exercise.goal_finished),
#                 feedback
#             )

#             # זיהוי הגעה ליעד (ננעל על True ומאפשר לרוץ לבונוסים)
#             reps_str = str(self.exercise.reps_left).strip()
#             if reps_str == "0" or "Bonus" in reps_str or "-" in reps_str or (hasattr(self.exercise, 'counter') and self.exercise.counter >= self.exercise.target_goal):
#                 self.goal_reached_successfully = True

#     def set_paused(self, paused_state):
#         """מעדכן את מצב ההקפאה של ה-AI"""
#         self.is_paused = paused_state
#         print(f"[SESSION] AI metrics monitoring pause state: {self.is_paused}")

#     def reset_and_clean_session(self):
#         """מבצע אירוח וניקוי מוחלט של זיכרון התרגיל (במקום הלוגיקה ב-exit_to_selection_screen)"""
#         self.is_workout_active = False
#         self.is_paused = False
        
#         # ניתוק בטוח של מנוע ה-AI מהתרגיל להשתקת פידבקים מיידית
#         self.video_worker.set_exercise(None)
        
#         if self.exercise is not None:
#             self.exercise.target_goal = 0
#             self.exercise.feedback = "" 
#             self.exercise.has_welcomed = False
#             self.exercise.counter = 0
#             self.exercise.bonus_counter = 0
#             self.exercise.goal_finished = False
#             self.exercise = None
#         print("[SESSION] Core engine and exercise instance successfully garbage collected.")