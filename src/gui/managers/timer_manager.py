from PyQt6.QtCore import QObject, QTimer, pyqtSignal

class TimerManager(QObject):
    """
    מנהל הזמן הרשמי של האפליקציה (SOLID - Single Responsibility Principle).
    מתואם ב-100% ללוגיקת הספירה לאחור (Countdown) של ה-MainWindow המקורי.
    """
    # סיגנלים (איתותים) לעדכון ה-GUI ושאר המערכת
    time_updated = pyqtSignal(int)       # משדר את מספר השניות שנותרו (במקום self.session_time_left)
    timeout_triggered = pyqtSignal()     # מאותת לעולם ברגע שנגמר הזמן (מפעיל את handle_session_timeout)
    pause_state_changed = pyqtSignal(bool) # משדר האם האימון כרגע בהקפאה אקטיבית

    def __init__(self):
        super().__init__()
        self.session_time_left = 0
        self.is_paused = False
        
        # יצירת ה-QTimer המקורי שלכן
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._handle_tick)

    def start_workout(self, time_limit_seconds):
        """מאתחל ומתחיל את הספירה לאחור של האימון לפי מגבלת הזמן שנקבעה"""
        self.session_time_left = time_limit_seconds
        self.is_paused = False
        self.timer.start(1000) # טיק בכל שנייה אחת (1000 מילישניות)
        self.time_updated.emit(self.session_time_left)
        self.pause_state_changed.emit(self.is_paused)
        print(f"[TIMER] Countdown started for {self.session_time_left} seconds.")

    def toggle_pause(self):
        """משנה ומנהל את מצב העצירה (Pause/Resume) של השעון"""
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            self.timer.stop()
            print("[TIMER] Workout countdown frozen.")
        else:
            self.timer.start(1000)
            print("[TIMER] Workout countdown resumed.")
            
        self.pause_state_changed.emit(self.is_paused)
        return self.is_paused

    def stop_workout(self):
        """עוצר את השעון לחלוטין ומאפס את המצב (למשל ביציאה למסך הבית)"""
        self.timer.stop()
        self.is_paused = False
        print(f"[TIMER] Workout countdown stopped safely. Remaining time was: {self.session_time_left}s")
        return self.session_time_left

    def _handle_tick(self):
        """פונקציה פנימית שמנהלת את הטיקים ומפחיתה שניות"""
        if self.is_paused:
            return

        self.session_time_left -= 1
        self.time_updated.emit(self.session_time_left)
        
        # זיהוי סיום הזמן - בול כמו ה-if self.session_time_left <= 0 במיין המקורי שלך!
        if self.session_time_left <= 0:
            self.timer.stop()
            print("[TIMER] Countdown expired! Triggering timeout event.")
            self.timeout_triggered.emit()